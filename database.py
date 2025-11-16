import os
import psycopg2
import psycopg2.extras

DB_URL = os.getenv("DATABASE_URL")


def get_conn():
    return psycopg2.connect(DB_URL, sslmode="require")


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS last_heroes (
            user_id BIGINT PRIMARY KEY,
            hero TEXT,
            date TEXT
        );
    """)
    conn.commit()
    conn.close()


def get_last_hero(user_id):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT hero, date FROM last_heroes WHERE user_id = %s;", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row  # {'hero': ..., 'date': ...}


def save_last_hero(user_id, hero, date):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO last_heroes (user_id, hero, date)
        VALUES (%s, %s, %s)
        ON CONFLICT (user_id)
        DO UPDATE SET hero = EXCLUDED.hero, date = EXCLUDED.date;
    """, (user_id, hero, date))
    conn.commit()
    conn.close()


def add_user(user_id, name):
    # Лише додаємо користувача в БД для розсилки
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            name TEXT
        );
    """)
    cur.execute("""
        INSERT INTO users (user_id, name)
        VALUES (%s, %s)
        ON CONFLICT DO NOTHING;
    """, (user_id, name))
    conn.commit()
    conn.close()


def get_users():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT user_id FROM users;")
    rows = cur.fetchall()
    conn.close()
    return rows
