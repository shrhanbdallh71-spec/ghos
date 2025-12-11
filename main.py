import telebot
from telebot import types
from config import BOT_TOKEN, ADMIN_ID, WELCOME_TEXT
from database.db import init_db, get_subjects, get_resources
import logging

# إعداد تسجيل الأخطاء
logging.basicConfig(level=logging.INFO)

bot = telebot.TeleBot(BOT_TOKEN)
init_db()

@bot.message_handler(commands=['start'])
def start(message):
    try:
        markup = types.InlineKeyboardMarkup()
        subjects = get_subjects()
        if not subjects:
            bot.send_message(message.chat.id, "🚫 لا توجد مواد مضافة بعد.")
            return
        for s in subjects:
            markup.add(types.InlineKeyboardButton(s, callback_data=f"subject_{s}"))
        bot.send_message(message.chat.id, WELCOME_TEXT, reply_markup=markup)
    except Exception as e:
        logging.error(f"Error in start: {e}")
        bot.send_message(message.chat.id, "❌ حدث خطأ أثناء التشغيل.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("subject_"))
def subject_details(call):
    subject_name = call.data.split("_", 1)[1]
    data = get_resources(subject_name)

    if not data:
        bot.answer_callback_query(call.id, "🚫 لا توجد كتب أو ملخصات لهذه المادة.")
        return

    books, summaries = [], []
    for rtype, title, link in data:
        if rtype == "book":
            books.append(f"📘 <a href='{link}'>{title}</a>")
        else:
            summaries.append(f"📝 <a href='{link}'>{title}</a>")

    text = f"<b>📚 مادة:</b> {subject_name}\n\n"
    if books:
        text += "📘 <b>الكتب:</b>\n" + "\n".join(books) + "\n\n"
    if summaries:
        text += "📝 <b>الملخصات:</b>\n" + "\n".join(summaries)
    
    bot.send_message(call.message.chat.id, text, parse_mode='HTML')

if __name__ == "__main__":
    logging.info("CyberSec – جامعة ذمار Bot Started 🔐")
    bot.polling(none_stop=True)
