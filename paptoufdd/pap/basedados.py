import sqlite3

conn = sqlite3.connect("dados.db")
cursor = conn.cursor()

# tabela users
cursor.execute("""
CREATE TABLE users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT,
password TEXT
)
""")

# tabela reservas
cursor.execute("""
CREATE TABLE reservas(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user TEXT,
produto_id INTEGER
)
""")

# tabela favoritos
cursor.execute("""
CREATE TABLE favoritos(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user TEXT,
produto_id INTEGER
)
""")

conn.commit()
conn.close()

print("Base de dados criada com sucesso!")