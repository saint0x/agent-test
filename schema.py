import sqlite3

conn = sqlite3.connect('root.db')

cursor = conn.cursor()

# Create users table
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    api_key TEXT UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)''')

# Create analysis_results table
cursor.execute('''
CREATE TABLE IF NOT EXISTS analysis_results (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    overallProjectHealth TEXT,
    overallSummary TEXT,
    formatted_report TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
)''')

# Commit the changes and close the connection
conn.commit()
conn.close()
