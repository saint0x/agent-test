import logging
import sqlite3
import uvicorn
import time
from threading import Thread
from main import app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger(__name__)

# Database connection function

def connect_db():
    try:
        conn = sqlite3.connect('butterfly_api_keys.db')
        logger.info("✅ Database connection established.")
        return conn
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        raise

# Function to insert the API key into the database

def insert_api_key(api_key):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO api_keys (api_key) VALUES (?)', (api_key,))
        conn.commit()
        logger.info("✅ Test API key inserted into the database.")
    except sqlite3.IntegrityError:
        logger.error("❌ API key already exists in the database.")
    except Exception as e:
        logger.error(f"❌ Failed to insert API key: {e}")
    finally:
        conn.close()

# Function to start the FastAPI server

def start_server():
    logger.info("🚀 Starting the FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Start the server in a separate thread
if __name__ == "__main__":
    server_thread = Thread(target=start_server)
    server_thread.start()

    # Wait for the server to be ready
    time.sleep(5)  # Adjust the sleep time as necessary

    # Insert the API key after the server is running
    TEST_API_KEY = "unique_test_api_key_" + str(int(time.time()))  # Generate a unique key based on the current time
    logger.info(f"Inserting API key: {TEST_API_KEY}")  # Log the API key being inserted
    insert_api_key(TEST_API_KEY)

    # Terminate the script after successful execution
    logger.info("✅ Script execution completed. Exiting...")
    exit()