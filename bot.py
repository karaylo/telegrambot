import telebot
import telebot
import random
import datetime
import time
import os
import hashlib
import threading

TOKEN = os.getenv("BOT_TOKEN")



bot = telebot.TeleBot(TOKEN)

heroes = [
    "Бичок",
    "Смик",
    "Pегетун",
    "Качур",
    "Нагла морда",
    "Денис",
    "Лошпед",
    "Чен",
    "бонік 4 без хекса",
    "Хрущик",
    "Шахрай"
    "Шептун Підступний"
    "Бортківський Барон"
    "Смик-Андроїд"


]

USERS_FILE = "users.txt"

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
# ВИБІР ГЕРОЯ
# ---------------------------
def get_today_hero(user_id):
    today = datetime.date.today().isoformat()
    text = f"{user_id}-{today}"
    hash_bytes = hashlib.sha256(text.encode()).digest()
    # створюємо локальний генератор, не змінюючи глобальний random
    rng = random.Random(int.from_bytes(hash_bytes, "big"))
    return rng.choice(heroes)

# ---------------------------
# КОМАНДИ БОТА
# ---------------------------
@bot.message_handler(commands=['start'])
def start(message):
    name = message.from_user.first_name or "Герой"
    save_user(message.chat.id, name)
    bot.send_message(message.chat.id, f"Привіт, {name}! 👋\n"
                                      f"Я скажу, хто ти сьогодні з Dota 2.\n"
                                      f"Напиши /whoami, щоб дізнатись!")

#Степан
@bot.message_handler(commands=['stepan'])
def stepan(message):
    bot.reply_to(message, "В степана в дупі шнобель\nВ степана в дупі шнобель\nВ степана в дупі шнобель\n ")


# Регета
@bot.message_handler(commands=['regeta'])
def regeta(message):
    bot.reply_to(message, "Регета пердун!\nРегета пердун!\nРегета пердун!\n")



@bot.message_handler(commands=['shnobel'])
def shnobel(message):
    bot.reply_to(message, "В Регети в дупі шнобель!\nВ Регети в дупі шнобель!\nВ Регети в дупі шнобель!\n")



@bot.message_handler(commands=['shpaga'])
def shpaga(message):
    bot.reply_to(message, "Регета, не точи шпагу!\nРегета, не точи шпагу!\nРегета, не точи шпагу!\n")



@bot.message_handler(commands=['smekuni'])
def smekuni(message):
    bot.reply_to(message, "🐂Смик бик — Бик Смик!🐂\n🐂Смик бик — Бик Смик!🐂\n🐂Смик бик — Бик Смик!🐂\n")







@bot.message_handler(commands=['baget'])
def baget(message):
    bot.reply_to(message, "Регета — барон багета! Шноблик у дупі😍😋🤭")




@bot.message_handler(commands=['jejeta'])
def jejeta(message):
    bot.reply_to(message, "Він тебе дуже хоче😈😏😍")










@bot.message_handler(commands=['whoami'])
def whoami(message):
    hero = get_today_hero(message.from_user.id)
    name = message.from_user.first_name or "Герой"
    save_user(message.chat.id, name)
    bot.reply_to(message, f"{name}, сьогодні ти — {hero}!")

# --- Тестова команда для миттєвої перевірки ---
#@bot.message_handler(commands=['test_send'])
#def test_send(message):
 #   users = load_users()
  #  for uid in users:
   #     hero = get_today_hero(uid)
    #    try:
     #       bot.send_message(uid, f"[ТЕСТ] 🎯 {message.from_user.first_name or 'Герой'}, сьогодні ти — {hero}!")
      #  except Exception as e:
       #     print(f"Не вдалося відправити {uid}: {e}")
    #bot.reply_to(message, "✅ Тестова розсилка виконана!")

# ---------------------------
# АВТОМАТИЧНА РОЗСИЛКА
# ---------------------------
def send_daily_messages():
    sent_today = None
    while True:
        now = datetime.datetime.now()
        today = now.date()

        # змінюй годину тут — для перевірки постав менше (наприклад, 10)
        if sent_today != today:
            users = load_users()
            for uid, name in users.items():
                hero = get_today_hero(uid)
                try:
                    bot.send_message(uid, f"пук. Нагадую, що існує прекрасний сайт - https://karaylo.github.io/regeta/")
                except Exception as e:
                    print(f"Не вдалося відправити {uid}: {e}")


            sent_today = today

        time.sleep(60)

# ---------------------------
# ЗАПУСК БОТА
# ---------------------------
threading.Thread(target=send_daily_messages, daemon=True).start()
bot.polling()
