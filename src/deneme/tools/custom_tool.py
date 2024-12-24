from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import os
import requests
from dotenv import load_dotenv


class ElevenLabsToolInput(BaseModel):
    """Input schema for ElevenLabs Tool."""
    prompt: str = Field(..., description="Text to be converted into audio.")
    voice_id: str = Field(..., description="Voice ID to use for audio generation.")
    stability: float = Field(default=0.5, description="Stability of the generated voice.")
    similarity_boost: float = Field(default=0.5, description="Similarity boost for the voice.")


class ElevenLabsTool(BaseTool):
    name: str = "ElevenLabs Text-to-Speech Tool"
    description: str = (
        "Generates audio files from text using ElevenLabs API. "
        "You can provide the prompt, voice_id, stability, and similarity_boost as inputs."
    )
    args_schema: Type[BaseModel] = ElevenLabsToolInput

    def _run(self, prompt: str, voice_id: str, stability: float = 0.5, similarity_boost: float = 0.5) -> str:
        """Generate an audio file from text."""
        load_dotenv()
        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            raise ValueError("API key not found. Ensure ELEVENLABS_API_KEY is set in the .env file.")

        try:
            # API request setup
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": api_key,
            }
            data = {
                "text": prompt,
                "voice_settings": {
                    "stability": stability,
                    "similarity_boost": similarity_boost,
                },
            }

            response = requests.post(url, json=data, headers=headers)
            if response.status_code != 200:
                raise RuntimeError(f"Failed to generate audio: {response.status_code} - {response.text}")

            # Save audio file
            file_path = "output.mp3"
            with open(file_path, "wb") as audio_file:
                audio_file.write(response.content)

            return file_path

        except Exception as e:
            raise RuntimeError(f"Error generating audio: {str(e)}")
