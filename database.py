import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.getenv("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DATABASE_URL, sslmode="require")

# -------------------------
# Створюємо таблиці
# -------------------------
def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            first_name TEXT
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS last_heroes (
            user_id BIGINT PRIMARY KEY,
            hero TEXT
        );
    """)

    conn.commit()
    cur.close()
    conn.close()


# -------------------------
# Користувачі
# -------------------------
def add_user(user_id, name):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO users(user_id, first_name)
        VALUES (%s, %s)
        ON CONFLICT (user_id) DO NOTHING;
    """, (user_id, name))

    conn.commit()
    cur.close()
    conn.close()


def get_users():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT * FROM users;")
    rows = cur.fetchall()

    cur.close()
    conn.close()
    return rows


# -------------------------
# Збереження героя
# -------------------------
def get_last_hero(user_id):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT hero FROM last_heroes WHERE user_id = %s;", (user_id,))
    row = cur.fetchone()

    cur.close()
    conn.close()
    return row[0] if row else None


def save_last_hero(user_id, hero):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO last_heroes (user_id, hero)
        VALUES (%s, %s)
        ON CONFLICT(user_id)
        DO UPDATE SET hero = EXCLUDED.hero;
    """, (user_id, hero))

    conn.commit()
    cur.close()
    conn.close()
