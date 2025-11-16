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

# --- INIT DATABASE ---
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

# ---------------------------
# /whoami — стабільний герой
# ---------------------------
def get_today_hero(user_id):
    today = datetime.date.today().isoformat()
    text = f"{user_id}-{today}"

    h = hashlib.sha256(text.encode()).digest()
    rng = random.Random(int.from_bytes(h, "big"))

    return rng.choice(heroes)


# ---------------------------
# Для авто-розсилки — без повторів
# ---------------------------
def get_random_hero_no_repeat(user_id):
    last = get_last_hero(user_id)
    available = [h for h in heroes if h != last]

    hero = random.choice(available)
    save_last_hero(user_id, hero)
    return hero


# ---------------------------
# Команди
# ---------------------------
@bot.message_handler(commands=['start'])
def start(message):
    name = message.from_user.first_name or "Герой"
    add_user(message.chat.id, name)

    bot.send_message(message.chat.id,
        f"Привіт, {name}! Напиши /whoami щоб дізнатися хто ти сьогодні."
    )


@bot.message_handler(commands=['whoami'])
def whoami(message):
    add_user(message.chat.id, message.from_user.first_name)
    hero = get_today_hero(message.from_user.id)

    bot.reply_to(message, f"{message.from_user.first_name}, сьогодні ти — {hero}!")


# Мемні команди (залишаю)
@bot.message_handler(commands=['stepan'])
def stepan(message): bot.reply_to(message, "В степана в дупі шнобель\n" * 3)

@bot.message_handler(commands=['regeta'])
def regeta(message): bot.reply_to(message, "Регета пердун!\n" * 3)

@bot.message_handler(commands=['shnobel'])
def shnobel(message): bot.reply_to(message, "В Регети в дупі шнобель!\n" * 3)

@bot.message_handler(commands=['smekuni'])
def smekuni(message): bot.reply_to(message, "🐂Смик бик — Бик Смик!🐂\n" * 3)


# ---------------------------
# Авто-розсилка
# ---------------------------
def send_daily_messages():
    sent_today = None
    while True:
        now = datetime.datetime.now()
        print(f"[{now}] Worker alive")  # heartbeat

        today = now.date()

        if sent_today != today:
            users = get_users()

            for u in users:
                uid = u["user_id"]
                hero = get_random_hero_no_repeat(uid)

                try:
                    bot.send_message(uid,
                        f"пук. Нагадую, що існує чудовий сайт: https://karaylo.github.io/regeta/\n"
                        f"Сьогодні ти: {hero}!"
                    )
                except Exception as e:
                    print(f"Не вдалося відправити {uid}: {e}")

            sent_today = today

        time.sleep(60)


# ---------------------------
# ЗАПУСК
# ---------------------------
threading.Thread(target=send_daily_messages, daemon=True).start()
bot.polling(none_stop=True)
