import os
import random       
from openai import OpenAI
from django.conf import settings 
from rest_framework import generics, status
from ..utils.response import make_response, make_json_response
from config.settings.conf import app_config

client = OpenAI(api_key=app_config.OPENAI_API_KEY)
class TextAudioAPI(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        try:
            text = request.data.get("text", None)
            message_id = request.data.get("message_id", None)
            if not text:
                return make_response(
                    "Text is required.", status.HTTP_400_BAD_REQUEST, False
                )
            audio_path = convert_text_to_audio(text, message_id)
            
            if audio_path is None:
                return make_response(
                    "Audio creation failed.", status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            return make_json_response(audio_path, "success", status.HTTP_201_CREATED,True)
        
        except Exception as e:
            return make_response(
                f"An error occurred: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR, False
            )
    
def convert_text_to_audio(text, message_id):
    try:
        audio_file_name = f"text_to_audio_{message_id}.mp3"
        # audio_file_path = os.path.join('src', 'media', 'audio', audio_file_name)
        audio_file_path = os.path.join(settings.MEDIA_ROOT, 'audio', audio_file_name)
        
        # Check if the audio file already exists
        if os.path.exists(audio_file_path):
            return os.path.join('audio', audio_file_name)
        
        response = client.audio.speech.create(
            model=app_config.OPENAI_TTS_MODEL_KEY,
            voice="alloy",
            input=text
        )

        audio_file_name = f"text_to_audio_{message_id}.mp3"
    
        audio_file_path = os.path.join(settings.MEDIA_ROOT, 'audio', audio_file_name)
        os.makedirs(os.path.dirname(audio_file_path), exist_ok=True)
        
        response.stream_to_file(audio_file_path)
        return os.path.join('audio', audio_file_name)
        
    except Exception as e:
        print(f"Error in converting text to audio: {str(e)}")
        return None
        