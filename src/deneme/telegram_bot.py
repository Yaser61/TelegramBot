import logging
from crewai.flow.flow import listen
from dotenv import load_dotenv
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from deneme.crew import Deneme, PhotoDecision, VoiceDecision, TexttoPhoto
from pydantic import BaseModel


load_dotenv()

class TaskOutputModel(BaseModel):
    description: str
    summary: str
    raw: str

async def should_use_photo(user_message: str) -> bool:
    try:
        crew = PhotoDecision().crew()

        # Kullanıcı mesajını ajan için input olarak gönderiyoruz
        inputs = {
            "conversation_context": {
                "user_message": user_message,
            }
        }

        # Fotoğraf kararı veren ajanı çalıştır
        photo_decision = crew.kickoff(inputs=inputs)

        logging.info(f"Photo decision result: {photo_decision}")

        if photo_decision and photo_decision.lower() == "yes":
            return True
        return False

    except Exception as e:
        logging.error(f"Photo decision error: {e}")
        return False

@listen(should_use_photo)
async def generate_photo(user_message: str) -> str:
    """
    TextToPhoto görevini kullanarak fotoğraf oluştur.
    """
    try:
        crew = TexttoPhoto().crew()

        # Kullanıcı mesajını input olarak gönderiyoruz
        inputs = {
            "conversation_context": {
                "user_message": user_message
            }
        }

        # Fotoğraf oluşturma görevini başlat
        photo = crew.kickoff(inputs=inputs)

        logging.info(f"Photo generation result: {photo}")

        if photo:
            return photo  # Üretilen fotoğrafın URL'si
        else:
            return "Fotoğraf oluşturulamadı."

    except Exception as e:
        logging.error(f"Photo generation error: {e}")
        return "Bir hata oluştu, fotoğraf üretimi başarısız."


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


        # Crew çalıştırma
        result = crew.kickoff(inputs=inputs)

        if result:
            return str(result)
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
    response = await flort_response(user_message)


    print(f"Telegram Response: {response}")

    await update.message.reply_text(response)


# Botu başlatma
def main():
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