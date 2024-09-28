import sqlite3
from auth_utils import User

DATABASE_PATH = 'butterfly_api_keys.db'

def create_tables():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users
    (username TEXT PRIMARY KEY, hashed_password TEXT)
    ''')
    conn.commit()
    conn.close()

def get_user(username: str):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT username, hashed_password FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return User(username=result[0], hashed_password=result[1])

def insert_user(username: str, hashed_password: str):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (username, hashed_password) VALUES (?, ?)', (username, hashed_password))
    conn.commit()
    conn.close()