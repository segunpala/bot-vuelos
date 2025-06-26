import requests
import sqlite3
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BOT_TOKEN = "7477046829:AAF2KpHRM5UEEh8I7h_vbNPYKAlAp-BUhIs"
CHAT_ID = "6733089327"
PRECIO_LIMITE = 250
ORIGEN = "EZE"

DESTINOS = [
    ("BCN", "Barcelona"),
    ("MAD", "Madrid"),
    ("FCO", "Roma"),
    ("CDG", "París")
]

def meses_a_consultar():
    meses = []
    for year in [2025, 2026]:
        for month in range(1, 13):
            if year == 2025 and month < 11:
                continue
            if year == 2026 and month > 3:
                continue
            meses.append((str(month), str(year)))
    return meses

def crear_tabla():
    try:
        conn = sqlite3.connect('vuelos.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vuelos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT,
                precio REAL,
                mes TEXT,
                año TEXT,
                origen TEXT,
                destino TEXT,
                tipo TEXT
            )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        logging.error(f"Error creando tabla: {e}")

def save_flight_to_db(fecha, precio, mes, año, origen, destino, tipo):
    try:
        conn = sqlite3.connect('vuelos.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO vuelos (fecha, precio, mes, año, origen, destino, tipo)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (fecha, precio, mes, año, origen, destino, tipo))
        conn.commit()
        conn.close()
    except Exception as e:
        logging.error(f"Error guardando en BD: {e}")

def send_telegram_message(message):
    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    try:
        response = requests.post(telegram_url, data=payload, timeout=10)
        if response.status_code != 200:
            logging.error(f"Telegram API error: {response.status_code} - {response.text}")
        return response.status_code == 200
    except Exception as e:
        logging.error(f"Error enviando mensaje de Telegram: {e}")
        return False

def construir_link(origen, destino, fecha):
    return f"https://www.flylevel.com/es/booking#/flights/one-way/{origen}/{destino}/{fecha}/1/0/0/Economy/USD"

def consultar_vuelos_tipo(origen, destino, meses, tipo_vuelo):
    url = "https://www.flylevel.com/nwe/flights/api/calendar/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive"
    }

    vuelos_baratos = []
    retry_delay = 1

    for mes, año in meses:
        params = {
            "triptype": "OW" if tipo_vuelo == "ida" else "RT",
            "origin": origen if tipo_vuelo == "ida" else destino,
            "destination": destino if tipo_vuelo == "ida" else origen,
            "month": mes,
            "year": año,
            "currencyCode": "USD"
        }
        for intento in range(3):
            try:
                response = requests.get(url, params=params, headers=headers, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    if 'data' in data and 'dayPrices' in data['data']:
                        for vuelo in data['data']['dayPrices']:
                            price = vuelo.get('price')
                            date = vuelo.get('date')
                            if price is not None and price < PRECIO_LIMITE:
                                vuelos_baratos.append({
                                    "fecha": date,
                                    "precio": price,
                                    "mes": mes,
                                    "año": año,
                                    "origen": origen if tipo_vuelo == "ida" else destino,
                                    "destino": destino if tipo_vuelo == "ida" else origen,
                                    "tipo": tipo_vuelo
                                })
                    break
                else:
                    logging.warning(f"HTTP {response.status_code} en {tipo_vuelo} {origen}->{destino} mes {mes}/{año}")
                    time.sleep(retry_delay)
                    retry_delay *= 2
            except Exception as e:
                logging.error(f"Error intento {intento+1} consultando {tipo_vuelo} {origen}->{destino} mes {mes}/{año}: {e}")
                time.sleep(retry_delay)
                retry_delay *= 2
        time.sleep(1.5)

    return vuelos_baratos

def check_flights():
    crear_tabla()
    meses = meses_a_consultar()

    for destino_iata, destino_nombre in DESTINOS:
        logging.info(f"🔍 Buscando vuelos a {destino_nombre} ({destino_iata})")

        vuelos_ida = consultar_vuelos_tipo(ORIGEN, destino_iata, meses, "ida")
        vuelos_vuelta = consultar_vuelos_tipo(ORIGEN, destino_iata, meses, "vuelta")

        if vuelos_ida:
            for vuelo in vuelos_ida:
                save_flight_to_db(vuelo["fecha"], vuelo["precio"], vuelo["mes"], vuelo["año"], vuelo["origen"], vuelo["destino"], vuelo["tipo"])
            mensaje_ida = f"✈️ <b>Vuelos baratos - Ida</b>\nRuta: {ORIGEN} → {destino_iata} ({destino_nombre})\n\n"
            for v in vuelos_ida[:5]:
                link = construir_link(v["origen"], v["destino"], v["fecha"])
                mensaje_ida += f"📅 {v['fecha']} - 💸 ${v['precio']} USD\n🔗 <a href='{link}'>Comprar</a>\n------------------\n"
            send_telegram_message(mensaje_ida)

        if vuelos_vuelta:
            for vuelo in vuelos_vuelta:
                save_flight_to_db(vuelo["fecha"], vuelo["precio"], vuelo["mes"], vuelo["año"], vuelo["origen"], vuelo["destino"], vuelo["tipo"])
            mensaje_vuelta = f"✈️ <b>Vuelos baratos - Vuelta</b>\nRuta: {destino_iata} ({destino_nombre}) → {ORIGEN}\n\n"
            for v in vuelos_vuelta[:5]:
                link = construir_link(v["origen"], v["destino"], v["fecha"])
                mensaje_vuelta += f"📅 {v['fecha']} - 💸 ${v['precio']} USD\n🔗 <a href='{link}'>Comprar</a>\n------------------\n"
            send_telegram_message(mensaje_vuelta)

    logging.info("✅ Chequeo finalizado.")

if __name__ == "__main__":
    while True:
        check_flights()
        logging.info("🕑 Esperando 2 minutos para siguiente chequeo...\n")
        time.sleep(120)
