import sqlite3

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
        link TEXT
    )
''')

conn.commit()
conn.close()

print("Tabla vuelos creada o verificada correctamente.")
