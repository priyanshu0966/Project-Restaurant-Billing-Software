# utils/db_utils.py
import sqlite3
import os

DB_PATH = "db/restaurant.db"

def init_db():
    os.makedirs("db", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Menu table
    c.execute('''CREATE TABLE IF NOT EXISTS menu (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_name TEXT,
                    category TEXT,
                    price REAL,
                    gst REAL)''')

    # Orders table
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mode TEXT,
                    payment_method TEXT,
                    subtotal REAL,
                    gst REAL,
                    total REAL,
                    datetime TEXT)''')

    # Order items table
    c.execute('''CREATE TABLE IF NOT EXISTS order_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER,
                    item_name TEXT,
                    quantity INTEGER,
                    price REAL,
                    gst REAL,
                    FOREIGN KEY(order_id) REFERENCES orders(id))''')

    conn.commit()
    conn.close()

def get_menu():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT item_name, category, price, gst FROM menu")
    rows = c.fetchall()
    conn.close()
    return rows

def add_menu_item(item_name, category, price, gst):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO menu (item_name, category, price, gst) VALUES (?, ?, ?, ?)",
              (item_name, category, price, gst))
    conn.commit()
    conn.close()

def save_order(mode, payment_method, subtotal, gst, total, datetime, order_items):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO orders (mode, payment_method, subtotal, gst, total, datetime) VALUES (?, ?, ?, ?, ?, ?)",
              (mode, payment_method, subtotal, gst, total, datetime))
    order_id = c.lastrowid

    for item in order_items:
        c.execute("INSERT INTO order_items (order_id, item_name, quantity, price, gst) VALUES (?, ?, ?, ?, ?)",
                  (order_id, item['item_name'], item['quantity'], item['price'], item['gst']))

    conn.commit()
    conn.close()
