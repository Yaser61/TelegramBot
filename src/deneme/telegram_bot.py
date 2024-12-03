import logging

from dotenv import load_dotenv
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from deneme.crew import Deneme
from pydantic import BaseModel


load_dotenv()

class TaskOutputModel(BaseModel):
    description: str
    summary: str
    raw: str

# LLM ile iletişim kurmak için Flort agent kullanımı
async def flort_response(user_message: str) -> str:
    try:
        crew = Deneme().crew()

        # Dinamik input oluşturma
        inputs = {
            "conversation_context": {
                "user_message": user_message,  # Kullanıcıdan gelen mesaj
            }
        }

        print(f"Inputs: {inputs}")

        # Crew çalıştırma
        print(f"Inputs to kickoff: {inputs}")
        result = crew.kickoff(inputs=inputs)
        print(f"Result: {result}")

        # Sonuçtan görevin çıktısını al, doğrudan result'u kullanabilirsiniz
        if result:
            return str(result).strip()  # result zaten doğru şekilde döndürülmüşse, doğrudan kullanabilirsiniz
        else:
            return "Görev sonucu bulunamadı"

    except Exception as e:
        logging.error(f"Crew execution error: {e}")
        return "Şu anda yanıt veremiyorum. Daha sonra tekrar deneyin."



# /start komutu için işlev
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Merhaba, Ben Elif.")


# Mesajları işleyen işlev
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    print(f"kullanıcı mesajı: {user_message}")
    response = await flort_response(user_message)

    print(f"Telegram Response: {response}")

    await update.message.reply_text(response)


# Botu başlatma
def main():
    # Çevresel değişkenden API anahtarını al
    api_key = os.getenv("TELEGRAM_API_KEY")

    # Botu başlat
    application = ApplicationBuilder().token(api_key).build()

    # Komutlar ve mesaj işleyicileri
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Botu çalıştır
    application.run_polling()


if __name__ == "__main__":
    main()