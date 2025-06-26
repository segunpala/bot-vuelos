import json
import os
import time
import requests
from dotenv import load_dotenv
from telegram import Bot
from datetime import datetime

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = Bot(token=TOKEN)

# CONFIGURACIÓN GENERAL
ORIGEN = "EZE"
AÑO = 2025
MES = 11  # Cambiá esto si querés otro mes
PRECIO_LIMITE = 450  # Precio máximo para avisar
DURACION_MIN = 5
DURACION_MAX = 14

# Cargar destinos desde el JSON
with open("destinos_populares.json", "r") as f:
    destinos = json.load(f)

def buscar_vuelos(destino):
    url = f"https://www.flylevel.com/nwe/flights/api/calendar/?triptype=RT&origin={ORIGEN}&destination={destino}&month={MES}&year={AÑO}&currencyCode=USD"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            day_prices = data["data"].get("dayPrices", [])

            ofertas = []
            for vuelo in day_prices:
                precio = vuelo.get("price")
                fecha = vuelo.get("date")

                if precio and precio <= PRECIO_LIMITE:
                    ofertas.append((fecha, precio))

            return ofertas
        else:
            print(f"[{destino}] Error HTTP {response.status_code}")
            return []
    except Exception as e:
        print(f"[{destino}] Error de conexión: {e}")
        return []

def enviar_mensaje(fecha, precio, destino):
    mensaje = (
        f"✈️ ¡VUELO BARATO DETECTADO!\n\n"
        f"📍 Desde: Buenos Aires (EZE)\n"
        f"📍 Hacia: {destino}\n"
        f"📅 Fecha: {fecha}\n"
        f"💸 Precio: ${precio} USD"
    )
    bot.send_message(chat_id=CHAT_ID, text=mensaje)

# Bucle infinito para revisar cada 30 minutos
while True:
    print(f"⏰ Revisando precios: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    for destino in destinos["europa"] + destinos["eeuu"] + destinos["sudamerica"]:
        ofertas = buscar_vuelos(destino)
        for fecha, precio in ofertas:
            enviar_mensaje(fecha, precio, destino)
        time.sleep(1)  # Espera breve entre cada destino

    print("😴 Esperando 30 minutos...\n")
    time.sleep(1800)  # 30 minutos
