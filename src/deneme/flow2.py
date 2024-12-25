#!/usr/bin/env python
import logging
import os
import requests
import json
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest
from pydantic import BaseModel

from crewai.flow.flow import Flow, start, listen, router

from deneme.crews.TexttoSpeech_crew.text_to_speech import TexttoSpeech
from deneme.crews.VoiceDecision_crew.voice_decision import VoiceDecision
from deneme.crews.deneme_crew.deneme import Deneme
from deneme.crews.PhotoDecision_crew.photo_decision import PhotoDecision
from deneme.crews.TexttoPhoto_crew.text_to_photo import TexttoPhoto, dalle
from deneme.crews.TextWithPhoto_crew.text_with_photo import TextWithPhoto

load_dotenv()


class AutoResponderState(BaseModel):
    user_message: str = ""
    generated_response: str = ""
    generated_photo: str = ""
    needs_photo: bool = False
    photo_decision_result: str = ""
    voice_decision_result: str = ""
    physical_features: str = dalle.prompt


class TelegramBotFlow(Flow[AutoResponderState]):
    initial_state = AutoResponderState

    @start()
    async def start_flow(self):
        """
        Entry point of the flow. Captures user message and initiates processing.
        """
        print(f"Received user message: {self.state.user_message}")
        print(f"Başlangıç fiziksel özellikleri: {self.state.physical_features}")

    @router(start_flow)
    async def decides(self):
        """
        Determine if a photo is needed based on the user's message.
        """
        try:
            photo_decision_crew = PhotoDecision().crew()
            inputs = {
                "conversation_context": {
                    "user_message": self.state.user_message,
                }
            }

            self.state.photo_decision_result = photo_decision_crew.kickoff(inputs=inputs)

            voice_decision_crew = VoiceDecision().crew()
            inputs = {
                "conversation_context": {
                    "user_message": self.state.user_message,
                }
            }

            self.state.voice_decision_result = voice_decision_crew.kickoff(inputs=inputs)

            if self.state.photo_decision_result.raw == "yes":
                return "generate_response_with_photo"
            else:
                return "generate_response_without_photo"

        except Exception as e:
            print(f"decision error: {e}")
            return "karar hatası"  # Hata durumunda yine metin yanıtı

    @listen("generate_response_with_photo")
    async def generate_response_withphoto(self):
        """
        Generate a photo based on the user's message.
        """
        try:
            text_to_photo_crew = TexttoPhoto().crew()
            inputs = {
                "conversation_context": {
                    "physical_features": self.state.physical_features
                }
            }

            photo = text_to_photo_crew.kickoff(inputs=inputs)

            self.state.generated_photo = photo if photo else "Fotoğraf oluşturulamadı."

            if self.state.voice_decision_result.raw == "yes":
                voice_response_crew = TexttoSpeech().crew()
                inputs = {
                    "conversation_context": {
                        "user_message": self.state.user_message
                    }
                }

                response = voice_response_crew.kickoff(inputs=inputs).raw

                tmp_dir = "tmp"
                full_path = os.path.join(tmp_dir, response)

                if os.path.exists(full_path):
                    with open(full_path, "rb") as audio_file:
                        self.state.generated_response = audio_file.read()
                    os.remove(full_path)
                    print(f"Temporary file {full_path} deleted.")
                else:
                    self.state.generated_response = None
                    print("Ses dosyası bulunamadı.")

            else:
                response_withphoto = TextWithPhoto().crew()
                inputs = {
                    "conversation_context": {
                        "user_message": self.state.user_message,
                        "physical_features": self.state.physical_features
                    }
                }

                response = response_withphoto.kickoff(inputs=inputs)
                self.state.generated_response = response.raw

            return "generate_response1"  # Fotoğraf üretildikten sonra metin yanıtına geç

        except Exception as e:
            logging.error(f"error: {e}")
            return "generate_response1"  # Fotoğraf üretilemezse metin yanıtı


    @listen("generate_response_without_photo")
    async def generate_response_withoutphoto(self):
        """
        Generate a text response using the Deneme crew.
        """
        try:

            if self.state.voice_decision_result.raw == "yes":
                voice_response_crew = TexttoSpeech().crew()
                inputs = {
                    "conversation_context": {
                        "user_message": self.state.user_message
                    }
                }

                response = voice_response_crew.kickoff(inputs=inputs).raw

                tmp_dir = "tmp"
                full_path = os.path.join(tmp_dir, response)

                if os.path.exists(full_path):
                    with open(full_path, "rb") as audio_file:
                        self.state.generated_response = audio_file.read()
                    # Dosyayı temizle
                    os.remove(full_path)
                    print(f"Temporary file {full_path} deleted.")
                else:
                    self.state.generated_response = None
                    print("Ses dosyası bulunamadı.")

            else:
                text_response_crew = Deneme().crew()
                inputs = {
                    "conversation_context": {
                        "user_message": self.state.user_message,
                    }
                }

                response = text_response_crew.kickoff(inputs=inputs)
                self.state.generated_response = str(response)

        except Exception as e:
            logging.error(f"Response generation error: {e}")
            self.state.generated_response = "Şu anda yanıt veremiyorum. Daha sonra tekrar deneyin."
            return "Yanıt oluşturulamıyo" # Hata durumunda genel mesaj döndür


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        flow = TelegramBotFlow()
        await flow.kickoff_async(inputs={
            "user_message": update.message.text,
            "physical_features": flow.state.physical_features
        })

    except Exception as e:
        logging.error(f"Error in flow kickoff: {e}")
        await update.message.reply_text("Akış hatası")
        return

    if flow.state.generated_photo and flow.state.generated_photo != "Fotoğraf oluşturulamadı.":
        if flow.state.voice_decision_result.raw == "yes":
            photo = requests.get(flow.state.generated_photo)
            photo_data = photo.content
            await update.message.reply_photo(photo_data)
            await update.message.reply_audio(flow.state.generated_response)
        else:
            photo = requests.get(flow.state.generated_photo)
            photo_data = photo.content
            await update.message.reply_photo(photo_data)
            await update.message.reply_text(flow.state.generated_response)
    else:
        if flow.state.voice_decision_result.raw == "yes":
            await update.message.reply_audio(flow.state.generated_response)
        else:
            await update.message.reply_text(flow.state.generated_response)


def main():
    request = HTTPXRequest(
        connection_pool_size=8,
        read_timeout=60,  # 1 dakika
        write_timeout=60,  # 1 dakika
        connect_timeout=30,  # 30 saniye
        pool_timeout=60  # 1 dakika
    )

    api_key = os.getenv("TELEGRAM_API_KEY")
    application = ApplicationBuilder().token(api_key).request(request).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot başlatılıyor...")
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()