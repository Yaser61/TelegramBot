from dotenv import load_dotenv
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from deneme.crew import Deneme

load_dotenv()


# LLM ile iletişim kurmak için Flort agent kullanımı
async def flort_response(user_message: str) -> str:
    inputs = {
        "topic": "Sohbet",
        "flort_task": {
            "input": f"Kullanıcı şunu söyledi: {user_message}. Bu mesaja Elif karakteri olarak samimi ve doğal bir şekilde yanıt ver."
        }
    }
    try:
        result = Deneme().crew().kickoff(inputs=inputs)

        # CrewOutput nesnesinin tüm özelliklerini yazdır
        print("CrewOutput Attributes:", dir(result))
        print("CrewOutput:", result)

        # Çıktıyı alma girişimi
        if hasattr(result, 'output'):
            print("Output:", result.output)
            return result.output
        elif hasattr(result, 'tasks') and result.tasks:
            print("Tasks:", result.tasks)
            return result.tasks[0].output or "Yanıt üretilemedi"
        else:
            return "Yanıt üretilemedi"

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Hata: {e}"


# /start komutu için işlev
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Merhaba, Ben Elif.")


# Mesajları işleyen işlev
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    response = await flort_response(user_message)
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