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

# Ініціалізація БД при старті
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

# ============================================
#  Алгоритм whoami
# ============================================

def get_today_hero(user_id):
    today = datetime.date.today().isoformat()

    last = get_last_hero(user_id)
    if last and last["date"] == today:
        return last["hero"]

    seed = f"{user_id}-{today}"
    h = hashlib.sha256(seed.encode()).digest()
    rng = random.Random(int.from_bytes(h, "big"))
    hero = rng.choice(heroes)

    yesterday_hero = last["hero"] if last else None

    if yesterday_hero == hero:
        available = [h for h in heroes if h != yesterday_hero]
        hero = rng.choice(available)

    save_last_hero(user_id, hero, today)
    return hero

# ============================================
#            КОМАНДИ БОТА
# ============================================

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    name = message.from_user.first_name or "Герой"
    add_user(user_id, name)

    bot.send_message(message.chat.id,
                     f"Привіт, {name}! Напиши /whoami щоб дізнатися свого героя на сьогодні.")

@bot.message_handler(commands=['whoami'])
def whoami(message):
    user_id = message.from_user.id
    name = message.from_user.first_name or "Герой"

    add_user(user_id, name)

    hero = get_today_hero(user_id)
    bot.reply_to(message, f"{name}, сьогодні ти — {hero}!")

# Мемні команди
@bot.message_handler(commands=['stepan'])
def stepan(message):
    bot.reply_to(message, "В степана в дупі шнобель\n" * 3)

@bot.message_handler(commands=['regeta'])
def regeta(message):
    bot.reply_to(message, "Регета пердун!\n" * 3)

@bot.message_handler(commands=['shnobel'])
def shnobel(message):
    bot.reply_to(message, "В Регети в дупі шнобель!\n" * 3)

@bot.message_handler(commands=['smekuni'])
def smekuni(message):
    bot.reply_to(message, "🐂Смик бик — Бик Смик!🐂\n" * 3)


@bot.message_handler(commands=['shpaga'])
def smekuni(message):
    bot.reply_to(message, "Регета, не точи шпагу!\n" * 3)


# ============================================
#         АВТОМАТИЧНА ЩОДЕННА РОЗСИЛКА
# ============================================

def send_daily_messages():
    sent_today = None

    while True:
        now = datetime.datetime.now()
        print(f"[{now}] Worker alive")

        today = now.date()

        if sent_today != today:
            users = get_users()

            print(f"Відправляю розсилку {len(users)} користувачам...")

            for u in users:
                uid = u["user_id"]
                try:
                    bot.send_message(
                        uid,
                        "пук. Нагадую, що існує прекрасний сайт: https://karaylo.github.io/regeta/"
                    )
                except Exception as e:
                    print(f"Не вдалося відправити {uid}: {e}")

            sent_today = today

        time.sleep(60)

# ============================================
#               ЗАПУСК БОТА
# ============================================

if __name__ == "__main__":
    threading.Thread(target=send_daily_messages, daemon=True).start()
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
