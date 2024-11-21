import json
import os
import jwt
import time
import aiofiles
import base64
import requests
from openai import OpenAI
from urllib.parse import parse_qs
from datetime import datetime
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework import status
from django.conf import settings 
from config.settings.conf import app_config
from src.utils.response import make_json_response_for_socket
from .SocketEvents import EVENTS_LIST, EVENTS
from src.models import ChatSession

class Consumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.client = OpenAI(api_key=app_config.OPENAI_API_KEY)
        self.middleware_error = None
        self.event_handlers = {
            EVENTS.TRANSCRIBE: self._handle_transcribe,
            EVENTS.CHAT_HISTORY: self._handle_chat_history,
            EVENTS.MSG_EVENT: self._handle_msg_event
        }
        # Cache for browser_id to thread_id mapping
        self._thread_id_cache = {}

    async def _send_error(
        self,
        data={},
        message: str = "",
        event: str = "",
        status_code: int = status.HTTP_200_OK,
        disconnect=False,
    ):
        error_msg_str = make_json_response_for_socket(data, message, event, status_code, False)
        res = await self.send(error_msg_str)
        if disconnect:
            await self.close()
        return res

    async def _send_data(self, data, message: str = "Success",event: str = ""):
        data_msg_str = make_json_response_for_socket(data, message, event, 200, True)
        res = await self.send(data_msg_str)
        return res

    async def connect(self):
        self.middleware_error = self.scope["error"]
        subprotocol = None
        thread_id = None

        for header in self.scope.get('headers', []):
            key, value = header

            if key == b'sec-websocket-protocol':
                decoded_value = value.decode()
                parts = decoded_value.split(', ')
    
                # Check if there are two parts or just one
                if len(parts) == 2:
                    subprotocol, thread_id = parts
                else:
                    subprotocol = parts[0]
                    thread_id = None
                break
                

        await self.accept(subprotocol=subprotocol)
        
        if self.middleware_error is not None:
            await self._send_error(
                {"error": f"{self.middleware_error}"},
                "",
                status.HTTP_400_BAD_REQUEST,
                disconnect=True,
            )
            return
        
        # data = {'role': 'assistant', 'content': 'welcome to mac papers', 'timestamp': datetime.now().isoformat(), 'thread_id': thread_id}
        # await self.call_openai_api_v2(data)
        return

    async def disconnect(self, cancel_code):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        try:
            text_data = json.loads(text_data)
            event = text_data.get("event")
            
            if not await self._validate_event(event):
                return
            
            handler = self.event_handlers.get(event)
            await handler(text_data.get("data"))
            
        except json.JSONDecodeError:
            await self._send_error({}, "Invalid request JSON body", status.HTTP_400_BAD_REQUEST)

    async def _validate_event(self, event):
        if not event:
            await self._send_error({}, "`event` is required in json", status.HTTP_400_BAD_REQUEST)
            return False
        
        if event not in EVENTS_LIST:
            await self._send_error({}, f"Invalid event sent. Allowed events are {EVENTS_LIST}", status.HTTP_400_BAD_REQUEST)
            return False
        return True

    async def _handle_transcribe(self, data):
        transcript = await self.audio_to_text(data)
        response_data = [{
            "role": "assistant",
            "content": transcript,
            "created_at": datetime.now().isoformat(),
            "thread_id": None,
            "message_id": None
        }]
        await self.send_json(response_data, event=EVENTS.TRANSCRIBE)

    async def _handle_chat_history(self, data):
        if data is None:
            await self._send_error({}, "`data` field is required", status.HTTP_400_BAD_REQUEST, False)
            return
        
        res, error = await self.openai_chat_history(data)
        if error:
            await self._send_error({}, str(error), status.HTTP_400_BAD_REQUEST, False)
        else:
            await self.send_json(res, event=EVENTS.CHAT_HISTORY)

    async def _handle_msg_event(self, data):
        if data is None:
            await self._send_error({}, "`data` field is required", status.HTTP_400_BAD_REQUEST, False)
            return
        
        start_time = time.time()
        await self.call_openai_api_v2(data)
        end_time = time.time()
        print("Time taken to execute call_openai_api_v2:", end_time - start_time)


    @sync_to_async
    def _get_chat_session(self, browser_id):
        return ChatSession.objects.filter(browser_id=browser_id).first()

    @sync_to_async
    def _update_chat_session(self, browser_id, thread_id):
        ChatSession.objects.filter(browser_id=browser_id).update(thread_id=thread_id)

    async def openai_chat_history(self, content):
        try:
            # Check cache first
            thread_id = content.get('thread_id', None)

            if not thread_id:
                return [], None

            # Batch fetch messages
            messages_obj = self.client.beta.threads.messages.list(
                thread_id=thread_id, 
                order="desc",
                limit=20  # Adjust based on your needs
            )
            rev_messages_obj = list(reversed(messages_obj.data))
            
            # Process messages in bulk
            return [self._format_message(msg) for msg in rev_messages_obj], None
            
        except (jwt.ExpiredSignatureError, jwt.DecodeError) as e:
            return None, str(e)
        except Exception as e:
            print("error in openai_chat_history:", e)
            return None, str(e)

    def _format_message(self, message):
        """Helper method to format OpenAI messages consistently"""
        return {
            "role": message.role,
            "content": message.content[0].text.value if message.content and len(message.content) > 0 else "",
            "created_at": message.created_at,
            "thread_id": message.thread_id,
            "message_id": message.id,
            # TODO: add audiofile_path
            "audio_path": os.path.join('audio', f"text_to_audio_{message.id}.mp3")
        }

    # Use streaming functionality of openai
    async def call_openai_api_v2(self, content):
        try:
            role = content.get('role', None)
            message = content.get('content', None)
            thread_id = content.get('thread_id', None)

            if not thread_id:
                browser_id = await self.get_browser_id_from_token()
                thread_id = await self._create_new_thread(browser_id)
                await self._create_thread_message(thread_id, role, message)
                messages = await self._fetch_thread_messages(thread_id)
                await self.send_json(messages, event=EVENTS.MSG_EVENT)
                return

            # Create message and run assistant
            await self._create_thread_message(thread_id, role, message)
            
            # Start streaming messages to frontend
            await self.stream_openai_responses(thread_id)

        except Exception as e:
            messages = None
            print("error in call_openai_api_v2:", e)
            messages = await self._fetch_thread_messages(thread_id)
            return messages, None

    # openai steam function
    async def stream_openai_responses(self, thread_id):
        assistant_id = app_config.OPENAI_ASSISTANT_KEY

        stream = self.client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id,
            stream=True  # Enable streaming mode
            )
    
        try:
            for event in stream:
                if event.event == "thread.message.completed":
                    response = [{
                        'role': 'assistant',
                        'content': event.data.content[0].text.value,
                        'created_at': event.data.created_at,
                        'thread_id': thread_id,
                        'message_id': event.data.id,
                        'audio_path': None
                    }]
                    # TODO: add audiofile_path
                    await self.send_json(response, event=EVENTS.MSG_EVENT)

                elif event.event == "thread.run.requires_action":
                    await self._handle_required_action(thread_id, event.data.id, event.data)
                
        except Exception as e:
            print(f"Error streaming responses: {e}")


    async def _create_new_thread(self, browser_id):
        new_thread = self.client.beta.threads.create()
        thread_id = new_thread.id
        await self._update_chat_session(browser_id, thread_id)
        # Update cache
        self._thread_id_cache[browser_id] = thread_id
        return thread_id

    async def _create_thread_message(self, thread_id, role, message):
        return self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role=role,
            content=message
        )

    async def _handle_required_action(self, thread_id, run_id, thread_status):
        tool_call = thread_status.required_action.submit_tool_outputs.tool_calls[0]
        response = await self.handle_requires_action(
            tool_call.function.name,
            tool_call.function.arguments
        )
        await self._submit_tool_output(thread_id, run_id, tool_call.id, response)

    # Submit tool output converts json resonse to human readable text
    async def _submit_tool_output(self, thread_id, run_id, tool_call_id, response):
        stream = self.client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread_id,
            run_id=run_id,
            tool_outputs=[{
                "tool_call_id": tool_call_id,
                "output": json.dumps(response)
            }],
            stream=True
        )

        for event in stream:
            if event.event == "thread.message.completed":
                    response = [{
                        'role': 'assistant',
                        'content': event.data.content[0].text.value,
                        'created_at': event.data.created_at,
                        'thread_id': thread_id,
                        'message_id': event.data.id,
                        'audio_path': None
                    }]
                    await self.send_json(response, event=EVENTS.MSG_EVENT)

    async def _fetch_thread_messages(self, thread_id):
        try:
            messages_obj = self.client.beta.threads.messages.list(
                thread_id=thread_id,
                order="desc",
                limit=20
            )
            if not isinstance(messages_obj.data, list):
                print("Expected a list but got:", messages_obj)
                return [] # Return an empty list if data is not a list
            
            rev_messages_obj = list(reversed(messages_obj.data))

            assistant_messages = [msg for msg in rev_messages_obj if msg.role == "assistant"]
            
            audio_dir = os.path.join(settings.MEDIA_ROOT, 'audio')
            os.makedirs(audio_dir, exist_ok=True)

            for msg in assistant_messages:
                audio_file_name = f"text_to_audio_{msg.id}.mp3"
                audio_file_path = os.path.join(audio_dir, audio_file_name)
                
                if os.path.exists(audio_file_path):
                    continue
                
                try:
                    # Create audio only if it doesn't exist
                    response = self.client.audio.speech.create(
                        model=app_config.OPENAI_TTS_MODEL_KEY,
                        voice="alloy",
                        input=msg.content[0].text.value if msg.content and len(msg.content) > 0 else None
                    )
                    if response.response.status_code == 200:
                        response.stream_to_file(audio_file_path)
                    continue

                except Exception as audio_error:
                    print(f"Error generating audio for message {msg.id}: {audio_error}")

            return [self._format_message(msg) for msg in rev_messages_obj]

        except Exception as e:
            print(f"Error fetching messages for thread {thread_id}: {e}")

            messages_obj = self.client.beta.threads.messages.list(
                thread_id=thread_id,
                order="desc",
                limit=20
            )
            rev_messages_obj = list(reversed(messages_obj.data))
            return [self._format_message(msg) for msg in rev_messages_obj] # Handle the error as needed


    async def audio_to_text(self, content):
        try:
            audio_bytes = base64.b64decode(content)
            audio_file_path = os.path.join(settings.MEDIA_ROOT, 'audio', 'filename.wav')
            
            os.makedirs(os.path.dirname(audio_file_path), exist_ok=True)
            
            # Use async file operations
            async with aiofiles.open(audio_file_path, "wb") as temp_audio_file:
                await temp_audio_file.write(audio_bytes)
            
            try:
                with open(audio_file_path, "rb") as audio_file:
                    transcript = self.client.audio.transcriptions.create(
                        model=app_config.OPENAI_WHISPER_MODEL_KEY,
                        file=audio_file,
                        language="en",
                        prompt="Please provide details related to customer inquiries including order details, item availability, item prices, and available dates. Common location codes are ASH (Asheville), ASQ (All Square Digital Solutions), ATL (Atlanta), BIR (Birmingham), CHA (Chattanooga), CLT (Charlotte), CLW (Clearwater), COL (Columbia), DPS (DPS), GBO (Greensboro), GVL (Greenville), JAX (Jacksonville), MAL (Mac Mall), MCL (MM Clearwater), MEM (Memphis), MFM (MM Ft. Myers), MIA (Miami), MMA (MM Marietta), MNC (MM Norcross), NAS (Nashville), NOL (New Orleans), NTL (Mac National), ORL (Orlando), RAL (Raleigh), TAL (Tallahassee), and TPA (Tampa). Include any shortcuts or identifiers for items checked, such as 'skey: quick copy'. Also, specify the unit of measurement for time, which may be in days (d), months (m), or weeks (w), and indicate the delivery method (PUP, COU, OUR, UPS, EXP)."
                    )
                    return transcript.text
            finally:
                if os.path.exists(audio_file_path):
                    os.remove(audio_file_path)
                    
        except Exception as e:
            print("error in audio_to_text:", e)
            return {"error": str(e)}

    async def _transcribe_audio(self, audio_content):
        return self.client.audio.translations.create(
            model=app_config.OPENAI_WHISPER_MODEL_KEY,
            file=audio_content
        )

    async def get_browser_id_from_token(self):
        # Helper function to get the browser_id from the token
        query_string = self.scope['query_string'].decode('utf-8')
        query_params = parse_qs(query_string)
        token = query_params.get('auth', [None])[0]
        if not token:
            return None
        
        try:
            # Decode the token
            payload = jwt.decode(token, app_config.JWT_SECRET_KEY, algorithms=[app_config.JWT_ALGORITHM])
            return payload.get("browser_id")
        except (jwt.ExpiredSignatureError, jwt.DecodeError) as e:
            return None 
        

    async def handle_requires_action(self,assitant_function_name, assitant_function_args):
        
        payload = json.loads(assitant_function_args)
        if assitant_function_name == "get_order_details":
            url = "https://ezmacpro.macpapers.com/getorderstatus"
            response = requests.get(url, json=payload)
            print("get_order_details response", response.status_code)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": response.status_code, "message": response.text}
        
        elif assitant_function_name == "get_available_dates":
            url = "https://ezmacpro.macpapers.com/getavailablereqdate"
            response = requests.post(url, json=payload)
            print("get_available_dates response", response.status_code)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": response.status_code, "message": response.text}
        
        elif assitant_function_name == "get_item_price":
            url = "https://ezmacpro.macpapers.com/getprice"
            response = requests.get(url, json=payload)
            print("get_item_price response", response.status_code)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": response.status_code, "message": response.text}
        
        elif assitant_function_name == "get_inventory_details":
            url = "https://ezmacpro.macpapers.com/getitems"
            response = requests.get(url, json=payload)
            print("get_inventory_details response", response.status_code)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": response.status_code, "message": response.text}

        elif assitant_function_name == "check_item_availability":
            url = "https://ezmacpro.macpapers.com/getinventory"
            response = requests.get(url, json=payload)
            print("check_item_availability response", response.status_code)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": response.status_code, "message": response.text}

        else:
            return

#------------------------------------------------------------------------------------------------------------

    async def send_json(self, data=None, event=None):
        await self._send_data(data, event=event)

   