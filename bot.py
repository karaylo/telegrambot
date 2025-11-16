import telebot
import random
import datetime
import time
import os
import hashlib
import threading

from database import (
    init_db,
    add_user,
    get_users,
    get_last_hero,
    save_last_hero
)

# ---------------------------
# INIT DB
# ---------------------------
init_db()

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

heroes = [
    "Бичок",
    "Смик",
    "Регетун",
    "Качур",
    "Нагла морда",
    "Денис",
    "Лошпед",
    "Чен",
    "Бонік 4 без хекса",
    "Хрущик",
    "Шахрай",
    "Шептун Підступний",
    "Бортківський Барон",
    "Смик-Андроїд",
]


# =====================================================
#  СТАБІЛЬНИЙ ЩОДЕННИЙ ГЕРОЙ БЕЗ ПОВТОРІВ ДВА ДНІ ПІДРЯД
# =====================================================

def get_today_hero(user_id):
    # 1. Детермінований герой (один на день)
    today = datetime.date.today().isoformat()
    seed_text = f"{user_id}-{today}"

    h = hashlib.sha256(seed_text.encode()).digest()
    rng =
