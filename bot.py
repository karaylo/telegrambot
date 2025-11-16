import telebot
import random
import datetime
import time
import os
import hashlib
import threading

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# ---------------------------
# СПИСОК ГЕРОЇВ
# ---------------------------
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

USERS_FILE = "users.txt"
LAST_HERO_FILE = "last_heroes.txt"

# ---------------------------
# ЗБЕРІГАННЯ КОРИСТУВАЧІВ
# ---------------------------
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    users = {}
    with open(USERS_FILE, "r") as f:
        for line in f:
            parts = line.strip().split(";")
            if len(parts) == 2:
                uid, name = parts
                users[int(uid)] = name
    return users


def save_user(user_id, first_name):
    users = load_users()
    if user_id not in users:
        with open(USERS_FILE, "a") as f:
            f.write(f"{user_id};{first_name}\n")


# ---------------------------
# ЗБЕРІГАННЯ ОСТАННЬОГО ГЕРОЯ (для уникнення повторів)
# ---------------------------
def load_last_heroes():
    if not os.path.exists(LAST_HERO_FILE):
        return {}
    data = {}
    with open(LAST_HERO_FILE, "r") as f:
        for line in f:
            uid, hero = line.strip().split(";")
            data[int(uid)] = hero
    return data


def save_last_hero(user_id, hero):
    heroes_data = load_last_heroes()
    heroes_data[user_id] = hero

    with open(LAST_HERO_FILE, "w") as f:
        for uid, h in heroes_data.items():
            f.write(f"{uid};{h}\n")


# ---------------------------
# ВИБІР ГЕРОЯ /whoami (стабільний, залежить від дня)
# ---------------------------
def get_today_hero(user_id):
    today = datetime.date.today().isoformat()
    text = f"{user_id}-{today}"

    hash_bytes = hashlib.sha256(text.encode()).digest()
    rng = random.Random(int.from_bytes(hash_bytes, "big"))

    return rng.choice(heroes)


# ---------------------------
# РЕАЛЬНИЙ ВИПАДКОВИЙ ГЕРОЙ БЕЗ ПОВТОРУ (для розсилки)
# ---------------------------
def get_random_hero_no_repeat(user_id):
    last = load_last_heroes().get(user_id)
    available = [h for h in heroes if h != last]

    hero = random.choice(available)
    save_last_hero(user_id, hero)
    return hero


# ---------------------------
# КОМАНДИ БОТА
# ---------------------------
@bot.message_handler(commands=['start'])
def start(message):
    name = message.from_user.first_name or "Герой"
    save_user(message.chat.id, name)
    bot.send_message(message.chat.id,
        f"Привіт, {name}! 👋\n"
        f"Напиши /whoami, щоб дізнатись хто ти сьогодні!"
    )


@bot.message_handler(commands=['whoami'])
def whoami(message):
    hero = get_today_hero(message.from_user.id)
    name = message.from_user.first_name or "Герой"
    save_user(message.chat.id, name)
    bot.reply_to(message, f"{name}, сьогодні ти — {hero}!")


# ---- Твої мемні команди -----------------
@bot.message_handler(commands=['stepan'])
def stepan(message):
    bot.reply_to(message, "В степана в дупі шнобель\n" * 3)

@bot.message_handler(commands=['regeta'])
def regeta(message):
    bot.reply_to(message, "Регета пердун!\n" * 3)

@bot.message_handler(commands=['shnobel'])
def shnobel(message):
    bot.reply_to(message, "В Регети в дупі шнобель!\n" * 3)

@bot.message_handler(commands=['shpaga'])
def shpaga(message):
    bot.reply_to(message, "Регета, не точи шпагу!\n" * 3)

@bot.message_handler(commands=['smekuni'])
def smekuni(message):
    bot.reply_to(message, "🐂Смик бик — Бик Смик!🐂\n" * 3)

@bot.message_handler(commands=['baget'])
def baget(message):
    bot.reply_to(message, "Регета — барон багета! Шноблик у дупі😍😋🤭")

@bot.message_handler(commands=['jejeta'])
def jejeta(message):
    bot.reply_to(message, "Він тебе дуже хоче😈😏😍")


# ---------------------------
# АВТОМАТИЧНА РОЗСИЛКА
# ---------------------------
def send_daily_messages():
    sent_today = None
    while True:
        now = datetime.datetime.now()
        today = now.date()

        if sent_today != today:
            users = load_users()

            for uid, name in users.items():
                hero = get_random_hero_no_repeat(uid)

                try:
                    bot.send_message(uid,
                        f"пук. Нагадую, що існує прекрасний сайт - https://karaylo.github.io/regeta/\n"
                        f"Сьогодні ти: {hero}!"
                    )
                except Exception as e:
                    print(f"Не вдалося відправити {uid}: {e}")

            sent_today = today

        time.sleep(60)


# ---------------------------
# ЗАПУСК БОТА
# ---------------------------
threading.Thread(target=send_daily_messages, daemon=True).start()
bot.polling()
