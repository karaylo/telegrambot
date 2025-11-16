import os
import psycopg2
import psycopg2.extras
from psycopg2.pool import SimpleConnectionPool

DB_URL = os.getenv("DATABASE_URL")

# Глобальний пул підключень (створюється один раз)
pool = SimpleConnectionPool(
    minconn=1,
    maxconn=5,
    dsn=DB_URL,
    sslmode="require"
)

def get_conn():
    """Взяти існуюче з'єднання з пулу (миттєво)"""
    return pool.getconn()

def put_conn(conn):
    """Повернути з'єднання назад у пул"""
    pool.putconn(conn)

# ---------------------------------------------------------
#  INIT ALL TABLES HERE
# ---------------------------------------------------------
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

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            name TEXT
        );
    """)

    conn.commit()
    put_conn(conn)

# ---------------------------------------------------------
#  LAST HERO (історія генерацій)
# ---------------------------------------------------------
def get_last_hero(user_id):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("SELECT hero, date FROM last_heroes WHERE user_id = %s;", (user_id,))
    row = cur.fetchone()

    put_conn(conn)
    return row


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
    put_conn(conn)

# ---------------------------------------------------------
#  USERS (для розсилки)
# ---------------------------------------------------------
def add_user(user_id, name):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO users (user_id, name)
        VALUES (%s, %s)
        ON CONFLICT DO NOTHING;
    """ ,(user_id, name))

    conn.commit()
    put_conn(conn)


def get_users():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("SELECT user_id FROM users;")
    rows = cur.fetchall()

    put_conn(conn)
    return rows
