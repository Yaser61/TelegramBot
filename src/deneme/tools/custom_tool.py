import os
import uuid
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
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

        # Initialize ElevenLabs client
        client = ElevenLabs(api_key=api_key)

        # Ensure tmp directory exists
        tmp_dir = "tmp"
        os.makedirs(tmp_dir, exist_ok=True)

        try:
            # Call ElevenLabs text-to-speech API
            response = client.text_to_speech.convert(
                voice_id=voice_id,
                output_format="mp3_22050_32",
                text=prompt,
                model_id="eleven_turbo_v2_5",  # Use turbo model for low latency
                voice_settings=VoiceSettings(
                    stability=stability,
                    similarity_boost=similarity_boost,
                ),
            )

            # Generate a unique file name in tmp directory
            save_file_path = os.path.join(tmp_dir, f"{uuid.uuid4()}.mp3")

            # Save the audio file
            with open(save_file_path, "wb") as f:
                for chunk in response:
                    if chunk:
                        f.write(chunk)

            print(f"{save_file_path}: A new audio file was saved successfully!")

            # Return the path of the saved audio file
            return save_file_path

        except Exception as e:
            raise RuntimeError(f"Error generating audio: {str(e)}")

    @staticmethod
    def cleanup_file(file_path: str):
        """Delete the temporary file."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"{file_path} was deleted successfully.")
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
