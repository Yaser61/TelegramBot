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

load_dotenv()


class AutoResponderState(BaseModel):
    user_message: str = ""
    generated_response: str = ""
    generated_photo: str = ""
    needs_photo: bool = False
    photo_decision_result: str = ""


class TelegramBotFlow(Flow[AutoResponderState]):
    initial_state = AutoResponderState

    @start()
    async def start_flow(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Entry point of the flow. Captures user message and initiates processing.
        """
        self.state.user_message = update.message.text
        print(f"Received user message: {self.state.user_message}")

        # Fotoğraf gereksinimini belirle
        await self.decide_photo_need()

    @router(start_flow)
    async def decide_photo_need(self):
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

            # Fotoğraf gerekip gerekmediğini belirle
            self.state.photo_decision_result = photo_decision_crew.kickoff(inputs=inputs)
            print(f"Photo decision result: {self.state.photo_decision_result}")

            # Fotoğraf gerekirse generate_photo fonksiyonuna yönlendir
            if self.state.photo_decision_result == "yes":
                return "generate_photo"  # "yes" ise fotoğraf üret
            else:
                return "generate_response"  # Fotoğraf gerekmezse metin yanıtını oluştur

        except Exception as e:
            logging.error(f"Photo decision error: {e}")
            return "generate_response"  # Hata durumunda yine metin yanıtı

    @listen("generate_photo")
    async def generate_photo(self):
        """
        Generate a photo based on the user's message.
        """
        try:
            text_to_photo_crew = TexttoPhoto().crew()
            inputs = {
                "conversation_context": {
                    "user_message": self.state.user_message
                }
            }

            print("Fotoğraf üretiliyor...")
            photo = text_to_photo_crew.kickoff(inputs=inputs)
            print(f"Photo generation result: {photo}")

            self.state.generated_photo = photo if photo else "Fotoğraf oluşturulamadı."
            return await self.generate_response()  # Fotoğraf üretildikten sonra metin yanıtına geç

        except Exception as e:
            logging.error(f"Photo generation error: {e}")
            return await self.generate_response()  # Fotoğraf üretilemezse metin yanıtı

    @listen("generate_response")
    async def generate_response(self):
        """
        Generate a text response using the Deneme crew.
        """
        try:
            response_crew = Deneme().crew()
            inputs = {
                "conversation_context": {
                    "user_message": self.state.user_message,
                }
            }

            self.state.generated_response = str(response_crew.kickoff(inputs=inputs))
            print(f"Generated response: {self.state.generated_response}")

            return await self.finalize_response()  # Son olarak yanıtı döndür

        except Exception as e:
            logging.error(f"Response generation error: {e}")
            self.state.generated_response = "Şu anda yanıt veremiyorum. Daha sonra tekrar deneyin."
            return await self.finalize_response()  # Hata durumunda genel mesaj döndür

    async def finalize_response(self):
        """
        Final step to return the generated response and photo.
        """
        return self.state.generated_response  # Final yanıtı döndür


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    flow = TelegramBotFlow()
    response = await flow.start_flow(update, context)

    # Fotoğraf varsa gönder
    if flow.state.generated_photo and flow.state.generated_photo != "Fotoğraf oluşturulamadı.":
        await update.message.reply_photo(flow.state.generated_photo)

    # Yanıtı gönder
    await update.message.reply_text(response)


def main():
    api_key = os.getenv("TELEGRAM_API_KEY")
    application = ApplicationBuilder().token(api_key).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot başlatılıyor...")
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
