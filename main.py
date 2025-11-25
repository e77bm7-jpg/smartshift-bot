import telebot
from datetime import datetime, timedelta
import calendar
import os

TOKEN = os.getenv("BOT_TOKEN")  # Токен из переменных Render
bot = telebot.TeleBot(TOKEN)

users = {}
availability = {}

@bot.message_handler(commands=['start'])
def start(m):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("I'm the owner", "I'm an employee")
    bot.send_message(m.chat.id, 
        "Hi! I'm SmartShift AI — smart shift scheduling for cafés, salons & clinics in Canada 🇨🇦\n\nWho are you?", 
        reply_markup=markup)

@bot.message_handler(func=lambda m: "owner" in m.text.lower())
def owner(m):
    users[m.from_user.id] = "owner"
    msg = bot.send_message(m.chat.id, "Great! What's the name of your business?")
    bot.register_next_step_handler(msg, save_name)

def save_name(m):
    business = m.text.strip()
    bot.send_message(m.chat.id, 
        f"Perfect, {business}! \n\nNow send me staff availability for the week:\n2025-12-01 9am-5pm\n2025-12-02 12pm-8pm\n(one line per day)", 
        reply_markup=telebot.types.ReplyKeyboardRemove())

@bot.message_handler(func=lambda m: "2025-" in m.text or "2026-" in m.text)
def save_avail(m):
    lines = [l.strip() for l in m.text.split('\n') if " " in l]
    saved = 0
    for line in lines:
        if " " in line:
            date, hours = line.split(" ", 1)
            availability[f"{m.from_user.id}_{date}"] = hours
            saved += 1
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Create weekly schedule")
    bot.send_message(m.chat.id, f"Saved {saved} days! Ready when you are", reply_markup=markup)

@bot.message_handler(func=lambda m: "create" in m.text.lower() or "schedule" in m.text.lower())
def schedule(m):
    today = datetime.now()
    monday = today + timedelta(days=(7 - today.weekday()) % 7)
    dates = [(monday + timedelta(i)).strftime("%Y-%m-%d") for i in range(7)]
    
    text = "Your weekly schedule:\n\n"
    for date in dates:
        day = calendar.day_name[datetime.strptime(date, "%Y-%m-%d").weekday()][:3]
        hours = availability.get(f"{m.from_user.id}_{date}", "—")
        text += f"{date} ({day}) → {hours}\n"
    text += "\nReady to send to your team!"
    bot.send_message(m.chat.id, text)

if __name__ == "__main__":
    print("SmartShift AI is running!")
    bot.infinity_polling()
