import sqlite3
import os

DB_FILE = "vault.db"

def get_connection():
    return sqlite3.connect(DB_FILE)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS config (
            user_id INTEGER,
            key TEXT,
            value TEXT,
            PRIMARY KEY (user_id, key),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS vault (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            service TEXT NOT NULL,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

def create_user(username: str) -> int:
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username) VALUES (?)", (username,))
        user_id = c.lastrowid
        conn.commit()
    except sqlite3.IntegrityError:
        user_id = -1
    conn.close()
    return user_id

def get_users() -> list:
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT id, username FROM users")
        rows = c.fetchall()
        conn.close()
        return rows
    except sqlite3.OperationalError:
        return []

def get_config(user_id: int, key: str):
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT value FROM config WHERE user_id = ? AND key = ?", (user_id, key))
        row = c.fetchone()
        conn.close()
        return row[0] if row else None
    except sqlite3.OperationalError:
        return None

def set_config(user_id: int, key: str, value: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO config (user_id, key, value) VALUES (?, ?, ?)", (user_id, key, value))
    conn.commit()
    conn.close()

def add_credential(user_id: int, service: str, username: str, encrypted_password: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO vault (user_id, service, username, password) VALUES (?, ?, ?, ?)",
              (user_id, service, username, encrypted_password))
    conn.commit()
    conn.close()

def get_all_credentials(user_id: int):
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT id, service, username, password FROM vault WHERE user_id = ?", (user_id,))
        rows = c.fetchall()
        conn.close()
        return rows
    except sqlite3.OperationalError:
        return []

def delete_credential(cred_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM vault WHERE id = ?", (cred_id,))
    conn.commit()
    conn.close()

def update_credential(cred_id: int, service: str, username: str, encrypted_password: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE vault SET service = ?, username = ?, password = ? WHERE id = ?",
              (service, username, encrypted_password, cred_id))
    conn.commit()
    conn.close()

def delete_user(user_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM vault WHERE user_id = ?", (user_id,))
    c.execute("DELETE FROM config WHERE user_id = ?", (user_id,))
    c.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
