#!/usr/bin/env python
import logging
import os
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from pydantic import BaseModel

from crewai.flow.flow import Flow, start, listen
from deneme.crew import Deneme

load_dotenv()


class AutoResponderState(BaseModel):
    user_message: str = ""
    generated_response: str = ""


class MessageHandlingFlow(Flow[AutoResponderState]):
    initial_state = AutoResponderState

    @start()
    async def handle_user_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Kullanıcı mesajını state'e kaydet
        self.state.user_message = update.message.text
        print(f"User Message: {self.state.user_message}")

        # Yanıt üretme akışını başlat
        return await self.generate_response()

    @listen(handle_user_message)
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

            result = crew.kickoff(inputs=inputs)

            self.state.generated_response = str(result)
            return self.state.generated_response

        except Exception as e:
            logging.error(f"Crew execution error: {e}")
            return "Şu anda yanıt veremiyorum. Daha sonra tekrar deneyin."


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    flow = MessageHandlingFlow()
    response = await flow.handle_user_message(update, context)
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