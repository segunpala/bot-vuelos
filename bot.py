from telegram import Bot
from dotenv import load_dotenv
import os
import time

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = Bot(token=TELEGRAM_TOKEN)

# Enviar un mensaje de prueba
mensaje = "✅ ¡Tu bot funciona! Este es un mensaje de prueba."
bot.send_message(chat_id=CHAT_ID, text=mensaje)

# Repetir el mensaje cada 2 minutos (opcional)
while True:
    print("Mensaje enviado. Esperando 2 minutos...")
    time.sleep(2 * 60)
    bot.send_message(chat_id=CHAT_ID, text="⏰ Recordatorio de prueba.")
