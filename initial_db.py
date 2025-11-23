import sqlite3
import os

DB_NAME = "shop_data.db"

def init_db():
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        print(f"Removed existing database: {DB_NAME}")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Create Sales table
    # We store date as TEXT (ISO8601 strings) for SQLite simplicity
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            revenue REAL
        )
    ''')

    conn.commit()
    conn.close()
    print(f"Database {DB_NAME} initialized successfully.")

if __name__ == "__main__":
    init_db()
