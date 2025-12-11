import telebot
from config import BOT_TOKEN, ADMIN_ID
from database.db import add_subject, add_resource
import logging

bot = telebot.TeleBot(BOT_TOKEN)
logging.basicConfig(level=logging.INFO)

@bot.message_handler(commands=['add_subject'])
def add_subject_handler(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "🚫 غير مصرح لك باستخدام هذا الأمر.")
        return
    msg = bot.send_message(message.chat.id, "أرسل اسم المادة الجديدة:")
    bot.register_next_step_handler(msg, save_subject)

def save_subject(message):
    subject = message.text.strip()
    add_subject(subject)
    bot.send_message(message.chat.id, f"✅ تمت إضافة المادة: {subject}")

@bot.message_handler(commands=['add_resource'])
def add_resource_handler(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "🚫 غير مصرح لك باستخدام هذا الأمر.")
        return
    msg = bot.send_message(message.chat.id, "أرسل اسم المادة:")
    bot.register_next_step_handler(msg, ask_type)

def ask_type(message):
    subject = message.text.strip()
    msg = bot.send_message(message.chat.id, "هل المرجع كتاب أم ملخص؟ (اكتب: book أو summary)")
    bot.register_next_step_handler(msg, lambda m: ask_title(m, subject))

def ask_title(message, subject):
    res_type = message.text.strip().lower()
    if res_type not in ['book', 'summary']:
        bot.send_message(message.chat.id, "❌ النوع غير صالح. استخدم فقط book أو summary.")
        return
    msg = bot.send_message(message.chat.id, "أرسل عنوان المرجع:")
    bot.register_next_step_handler(msg, lambda m: ask_link(m, subject, res_type))

def ask_link(message, subject, res_type):
    title = message.text.strip()
    msg = bot.send_message(message.chat.id, "أرسل رابط المرجع:")
    bot.register_next_step_handler(msg, lambda m: save_resource(m, subject, res_type, title))

def save_resource(message, subject, res_type, title):
    link = message.text.strip()
    add_resource(subject, res_type, title, link)
    bot.send_message(message.chat.id, f"✅ تمت إضافة {('كتاب' if res_type=='book' else 'ملخص')} '{title}' للمادة '{subject}'")

if __name__ == "__main__":
    logging.info("لوحة تحكم CyberSec DMU قيد التشغيل 🧩")
    bot.polling()
