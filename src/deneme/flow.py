#!/usr/bin/env python
import logging
import os
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from pydantic import BaseModel

from crewai.flow.flow import Flow, start, listen, router
from deneme.crews.deneme_crew.deneme import Deneme
from deneme.crews.PhotoDecision_crew.photo_decision import PhotoDecision
from deneme.crews.TexttoPhoto_crew.text_to_photo import TexttoPhoto
from deneme.crews.TexttoSpeech_crew.text_to_speech import TexttoSpeech
from deneme.crews.VoiceDecision_crew.voice_decision import VoiceDecision

load_dotenv()

class AutoResponderState(BaseModel):
    user_message: str = ""
    generated_response: str = ""
    generated_photo: str = ""
    needs_photo: bool = False


class MessageHandlingFlow(Flow[AutoResponderState]):
    initial_state = AutoResponderState

    @start()
    async def handle_user_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Kullanıcı mesajını state'e kaydet
        self.state.user_message = update.message.text
        print(f"User Message: {self.state.user_message}")

        #self.state.needs_photo = await self.check_photo_need()
        #print(self.state.needs_photo)
        #print(self.check_photo_need())

        # Yanıt üretme akışını başlat
        return await self.generate_response()

    async def check_photo_need(self) -> bool:
        try:
            crew = PhotoDecision().crew()
            inputs = {
                "conversation_context": {
                    "user_message": self.state.user_message,
                }
            }

            photo_decision = crew.kickoff(inputs=inputs)
            logging.info(f"Photo decision result: {photo_decision}")

            if photo_decision and photo_decision == "yes":
                return True
            return False
        except Exception as e:
            logging.error(f"Photo decision error: {e}")
            return False

    async def generate_photo(self) -> str:
        try:
            crew = TexttoPhoto().crew()
            inputs = {
                "conversation_context": {
                    "user_message": self.state.user_message
                }
            }

            print("Fotoğraf üretiliyor")
            photo = crew.kickoff(inputs=inputs)
            logging.info(f"Photo generation result: {photo}")

            return photo if photo else "Fotoğraf oluşturulamadı."
        except Exception as e:
            logging.error(f"Photo generation error: {e}")
            return "Bir hata oluştu, fotoğraf üretimi başarısız."

    @listen(check_photo_need)
    async def generate_response(self):
        try:
            # Crew oluştur
            crew = Deneme().crew()

            # Dinamik input hazırla
            inputs = {
                "conversation_context": {
                    "user_message": self.state.user_message,
                }
            }

            # Metin yanıtını oluştur
            result = crew.kickoff(inputs=inputs)
            self.state.generated_response = str(result)

            # Fotoğraf gerekiyorsa fotoğraf oluştur
            if self.state.needs_photo:
                self.state.generated_photo = await self.generate_photo()

            return self.state.generated_response

        except Exception as e:
            logging.error(f"Crew execution error: {e}")
            return "Şu anda yanıt veremiyorum. Daha sonra tekrar deneyin."

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    flow = MessageHandlingFlow()
    response = await flow.handle_user_message(update, context)

    if flow.state.generated_photo and flow.state.generated_photo != "Fotoğraf oluşturulamadı.":
        await update.message.reply_photo(flow.state.generated_photo)

    # Yanıtı gönder
    await update.message.reply_text(response)

def main():
    api_key = os.getenv("TELEGRAM_API_KEY")

    application = ApplicationBuilder().token(api_key).build()

    # Mesaj handler'ını ekle
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot başlatılıyor...")
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()