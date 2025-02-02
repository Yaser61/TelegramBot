#!/usr/bin/env python
import logging
import os
import requests
import json
from dotenv import load_dotenv
from litellm.proxy.management_endpoints.internal_user_endpoints import user_update

from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest
from pydantic import BaseModel

from crewai.flow.flow import Flow, start, listen, router

from crews.TexttoSpeech_crew.text_to_speech import TexttoSpeech
from crews.VoiceDecision_crew.voice_decision import VoiceDecision
from crews.VoiceWithPhoto_crew.voice_with_photo import VoiceWithPhoto
from crews.TextResponse_crew.text_response import TextResponse
from crews.PhotoDecision_crew.photo_decision import PhotoDecision
from crews.TexttoPhoto_crew.text_to_photo import TexttoPhoto, dalle
from crews.TextWithPhoto_crew.text_with_photo import TextWithPhoto

from db.redis_connection import RedisConnection

load_dotenv()

class AutoResponderState(BaseModel):
    username: str = ""
    user_message: str = ""
    chat_history: list = ()
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
                    "user_message": self.state.user_message
            }

            self.state.photo_decision_result = photo_decision_crew.kickoff(inputs=inputs).raw

            voice_decision_crew = VoiceDecision().crew()
            inputs = {
                    "user_message": self.state.user_message
            }

            self.state.voice_decision_result = voice_decision_crew.kickoff(inputs=inputs).raw

            if self.state.photo_decision_result == "yes":
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
                    "physical_features": self.state.physical_features
            }

            photo = text_to_photo_crew.kickoff(inputs=inputs)

            self.state.generated_photo = photo if photo else "Fotoğraf oluşturulamadı."

            chat_history_json = json.dumps(self.state.chat_history, ensure_ascii=False)

            if self.state.voice_decision_result == "yes":
                voice_response_crew = VoiceWithPhoto().crew()
                inputs = {
                        "username": self.state.username,
                        "chat_history": chat_history_json,
                        "user_message": self.state.user_message,
                        "physical_features": self.state.physical_features
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
                        "username": self.state.username,
                        "user_message": self.state.user_message,
                        "chat_history": chat_history_json,
                        "physical_features": self.state.physical_features
                }

                response = response_withphoto.kickoff(inputs=inputs)
                self.state.generated_response = response.raw

            return "generate_response1"

        except Exception as e:
            logging.error(f"error: {e}")
            return "generate_response1"


    @listen("generate_response_without_photo")
    async def generate_response_withoutphoto(self):
        """
        Generate a text response using the TextResponse crew.
        """
        try:

            chat_history_json = json.dumps(self.state.chat_history, ensure_ascii=False)

            if self.state.voice_decision_result == "yes":
                voice_response_crew = TexttoSpeech().crew()
                inputs = {
                        "username": self.state.username,
                        "user_message": self.state.user_message,
                        "chat_history": chat_history_json
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
                text_response_crew = TextResponse().crew()
                inputs = {
                        "username": self.state.username,
                        "user_message": self.state.user_message,
                        "chat_history": chat_history_json
                }

                response = text_response_crew.kickoff(inputs=inputs)
                self.state.generated_response = response.raw

        except Exception as e:
            logging.error(f"Response generation error: {e}")
            self.state.generated_response = "Şu anda yanıt veremiyorum. Daha sonra tekrar deneyin."
            return "Yanıt oluşturulamıyo" # Hata durumunda genel mesaj döndür


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.message.chat_id
        username = update.message.chat.first_name
        user_message = update.message.text

        redis_client = RedisConnection().get_client()

        redis_key = f"user:{user_id}:chat_history"

        chat_history_raw = redis_client.lrange(redis_key, 0, -1)
        chat_history = [json.loads(message) for message in chat_history_raw]

        chat_history.append({"sender": username, "message": user_message})
        redis_client.rpush(redis_key, json.dumps({"sender": username, "message": user_message}))

        flow = TelegramBotFlow()
        flow.state.username = username
        flow.state.user_message = update.message.text
        flow.state.chat_history = chat_history
        flow.state.physical_features = flow.state.physical_features
        await flow.kickoff_async()

        print(f"{username}:, {user_message}")

    except Exception as e:
        logging.error(f"Error in flow kickoff: {e}")
        await update.message.reply_text("Akış hatası")
        return

    if flow.state.generated_photo and flow.state.generated_photo != "Fotoğraf oluşturulamadı.":
        if flow.state.voice_decision_result == "yes":
            photo = requests.get(flow.state.generated_photo)
            photo_data = photo.content
            await update.message.reply_photo(photo_data)
            await update.message.reply_audio(flow.state.generated_response)
        else:
            photo = requests.get(flow.state.generated_photo)
            photo_data = photo.content
            await update.message.reply_photo(photo_data)
            await update.message.reply_text(flow.state.generated_response)
            redis_client.rpush(redis_key, json.dumps({"sender": "bot", "message": flow.state.generated_response}))
            redis_client.ltrim(redis_key, -100, -1)
    else:
        if flow.state.voice_decision_result == "yes":
            await update.message.reply_audio(flow.state.generated_response)
        else:
            await update.message.reply_text(flow.state.generated_response)
            redis_client.rpush(redis_key, json.dumps({"sender": "bot", "message": flow.state.generated_response}))
            redis_client.ltrim(redis_key, -100, -1)

def main():
    request = HTTPXRequest(
        connection_pool_size=8,
        read_timeout=120,  # 1 dakika
        write_timeout=120,  # 1 dakika
        connect_timeout=60,  # 30 saniye
        pool_timeout=120  # 1 dakika
    )

    api_key = os.getenv("TELEGRAM_API_KEY")
    application = ApplicationBuilder().token(api_key).request(request).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot başlatılıyor...")

    application.run_polling(drop_pending_updates=False)


if __name__ == "__main__":
    main()