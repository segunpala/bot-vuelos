from telegram import Bot
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = Bot(token=TOKEN)

mensaje = "✅ ¡El bot está conectado y enviando mensajes!"

bot.send_message(chat_id=CHAT_ID, text=mensaje)

print("Mensaje enviado con éxito.")
