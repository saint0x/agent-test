import os
import sqlite3

DATABASE_PATH = os.getenv('DATABASE_PATH')


def create_tables():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS api_keys
    (api_key TEXT PRIMARY KEY)
    ''')
    conn.commit()
    conn.close()


def get_user(api_key: str):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT api_key FROM api_keys WHERE api_key = ?', (api_key,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {"api_key": result[0]}  # Return a dictionary


def insert_user(api_key: str):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO api_keys (api_key) VALUES (?)', (api_key,))
        conn.commit()
        print("✅ API key inserted successfully.")
    except sqlite3.IntegrityError:
        print("❌ API key already exists.")
    except Exception as e:
        print(f"❌ Failed to insert API key: {e}")
    finally:
        conn.close()


def delete_user(api_key: str):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM api_keys WHERE api_key = ?', (api_key,))
        if cursor.rowcount == 0:
            print("❌ API key does not exist.")
        else:
            conn.commit()
            print("✅ API key deleted successfully.")
    except Exception as e:
        print(f"❌ Failed to delete API key: {e}")
    finally:
        conn.close()