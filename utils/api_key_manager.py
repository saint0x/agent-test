import os
import uuid
import sqlite3
from datetime import datetime, timedelta

DATABASE_PATH = os.getenv('DATABASE_PATH')

def create_api_key_table():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS api_keys
    (key TEXT PRIMARY KEY, created_at TIMESTAMP, expires_at TIMESTAMP)
    ''')
    conn.commit()
    conn.close()

def generate_api_key():
    return str(uuid.uuid4())

def store_api_key(api_key, expiration_days=365):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    created_at = datetime.now()
    expires_at = created_at + timedelta(days=expiration_days)
    cursor.execute('INSERT INTO api_keys (key, created_at, expires_at) VALUES (?, ?, ?)',
                   (api_key, created_at, expires_at))
    conn.commit()
    conn.close()

def validate_api_key(api_key):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT expires_at FROM api_keys WHERE key = ?', (api_key,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        expires_at = datetime.strptime(result[0], '%Y-%m-%d %H:%M:%S.%f')
        return datetime.now() < expires_at
    return False

def generate_and_store_api_key():
    api_key = generate_api_key()
    store_api_key(api_key)
    return api_key

# Initialize the database
create_api_key_table()