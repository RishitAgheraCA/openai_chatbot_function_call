# Mac-Audio-bot

**Audio bot leveraging Django backend for speech recognition and seamless interaction with external APIs.**

## Project Overview

The Mac-Audio-bot is an innovative audio processing application designed to facilitate real-time speech recognition and interaction with various external APIs. By leveraging advanced technologies, the bot transforms audio input into text, processes it using natural language processing (NLP), and provides seamless text-to-speech capabilities.

## Flow

1. **User Interaction**: Users interact with the bot via a WebSocket connection, enabling real-time communication.
2. **Audio Input**: The bot captures audio input from the user.
3. **Audio Processing**:
   - The captured audio is processed using **FFmpeg** to ensure optimal format and quality.
   - The processed audio is then converted to text using the **OpenAI Whisper** model.
4. **NLP Processing**: The transcribed text is processed using the **OpenAI GPT-4o** model, which performs natural language processing and generates structured JSON data for interaction with external APIs.
5. **API Interaction**: The bot seamlessly communicates with external APIs using the structured JSON data.
6. **Text-to-Speech**: The response from the API is converted back into audio using the **OpenAI TTS-1-hd** model, allowing the bot to respond audibly to the user.
7. **Real-time Feedback**: Users receive immediate feedback through the WebSocket connection, ensuring a smooth conversational experience.

## Technologies Used

- **Python**: Backend language.
- **Django Rest Framework**: Backend technology for building APIs.
- **Django Channels**: Enables WebSocket real-time chat functionality.
- **Swagger**: API documentation and testing tool.
- **OpenAI Whisper**: Audio-to-text transcription.
- **OpenAI TTS-1-hd model**: Text-to-speech conversion.
- **OpenAI GPT-4o**: NLP processing and JSON creation for external API interaction.
- **FFmpeg**: Audio processing framework.
- **PostgreSQL**: Database management system.
- **Docker/Docker-Compose**: Containerization for easy deployment.
- **GitLab/GitHub**: Version control for source code management.

## Getting Started

To get started with the Mac-Audio-bot, follow these steps:

1. Clone the repository:
   ```bash
   git clone git@0.0.0.0:root/mac-audio-bot.git
   cd Mac-Audio-bot
   ```

2. Set up Docker:
   ```bash
   docker-compose up --build
   ```

3. Access the API documentation via Swagger at `http://localhost:8000/swagger/`.

4. Connect to the WebSocket to start interacting with the audio bot.

-------------------------------------
## docker build and push 
# docker build
docker build -t juniorjohndoejd/mac-audiobot:0.0.1 --build-arg APP_VERSION=0.0.1 .
# docker push
docker push juniorjohndoejd/mac-audiobot:tagname