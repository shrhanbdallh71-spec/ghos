import telebot
from telebot import types
from flask import Flask, request
import logging
import sqlite3

# ===== إعدادات البوت =====
BOT_TOKEN = "8585096387:AAHNrx3_2Lb8hz-gTjjKcfrcUvWq41OFD_Y"
ADMIN_ID = 8100614908  # ضع رقم الايدي الخاص بك هنا
WEBHOOK_URL = "https://YOUR_RENDER_URL.onrender.com"  # ضع رابط render هنا

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# ===== إعداد تسجيل الأخطاء =====
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ===== إنشاء قاعدة البيانات =====
def init_db():
    conn = sqlite3.connect("cybersec_dhamar.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS materials (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    summary TEXT,
                    book_link TEXT
                )''')
    conn.commit()
    conn.close()

init_db()

# ===== رسالة الترحيب =====
def welcome_message(name):
    return (
        f"🎓 مرحباً {name} في بوت قسم الأمن السيبراني – جامعة ذمار (CyberSec Dhamar University)\n\n"
        "📚 هذا البوت مخصص لتجميع الملخصات والكتب الخاصة بمواد الأمن السيبراني في جامعة ذمار.\n\n"
        "اختر المادة لعرض الكتب والملخصات المتوفرة 👇"
    )

# ===== أمر /start =====
@bot.message_handler(commands=['start'])
def start(message):
    user_first = message.from_user.first_name
    markup = types.InlineKeyboardMarkup()

    # جلب المواد من قاعدة البيانات
    conn = sqlite3.connect("cybersec_dhamar.db")
    c = conn.cursor()
    c.execute("SELECT id, name FROM materials")
    materials = c.fetchall()
    conn.close()

    if not materials:
        bot.send_message(message.chat.id, "🚫 لا توجد مواد مضافة بعد. الرجاء العودة لاحقاً.")
        return

    for m_id, name in materials:
        markup.add(types.InlineKeyboardButton(f"📘 {name}", callback_data=f"material_{m_id}"))

    bot.send_message(message.chat.id, welcome_message(user_first), reply_markup=markup)

# ===== عرض تفاصيل المادة =====
@bot.callback_query_handler(func=lambda call: call.data.startswith("material_"))
def show_material(call):
    mat_id = call.data.split("_")[1]

    conn = sqlite3.connect("cybersec_dhamar.db")
    c = conn.cursor()
    c.execute("SELECT name, summary, book_link FROM materials WHERE id=?", (mat_id,))
    material = c.fetchone()
    conn.close()

    if material:
        name, summary, book_link = material
        text = f"📘 <b>{name}</b>\n\n📖 <b>الملخص:</b>\n{summary}\n\n🔗 <b>رابط الكتاب:</b>\n{book_link}"
        bot.send_message(call.message.chat.id, text, parse_mode="HTML")
    else:
        bot.send_message(call.message.chat.id, "❌ حدث خطأ أثناء جلب بيانات المادة.")

# ===== لوحة تحكم المشرف لإضافة المواد =====
@bot.message_handler(commands=['add'])
def add_material(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "🚫 هذا الأمر خاص بالمشرف فقط.")
        return
    msg = bot.send_message(message.chat.id, "📘 أرسل اسم المادة:")
    bot.register_next_step_handler(msg, get_material_name)

def get_material_name(message):
    name = message.text.strip()
    msg = bot.send_message(message.chat.id, "📝 أرسل الملخص:")
    bot.register_next_step_handler(msg, lambda m: get_material_summary(m, name))

def get_material_summary(message, name):
    summary = message.text.strip()
    msg = bot.send_message(message.chat.id, "🔗 أرسل رابط الكتاب:")
    bot.register_next_step_handler(msg, lambda m: save_material(m, name, summary))

def save_material(message, name, summary):
    book_link = message.text.strip()

    conn = sqlite3.connect("cybersec_dhamar.db")
    c = conn.cursor()
    c.execute("INSERT INTO materials (name, summary, book_link) VALUES (?, ?, ?)", (name, summary, book_link))
    conn.commit()
    conn.close()

    bot.send_message(message.chat.id, f"✅ تم إضافة المادة <b>{name}</b> بنجاح!", parse_mode="HTML")

# ===== Flask Webhook =====
@app.route('/' + BOT_TOKEN, methods=['POST'])
def getMessage():
    json_str = request.stream.read().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return 'OK', 200

@app.route('/')
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
    return "Webhook set successfully!", 200

# ===== التشغيل =====
if __name__ == "__main__":
    logging.info("🚀 Bot is running via Flask (Webhook Mode)")
    app.run(host="0.0.0.0", port=10000)
