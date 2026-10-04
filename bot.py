import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# توکن ربات خود را اینجا وارد کنید (یا از متغیر محیطی Railway بخوانید)
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "توکن_ربات_خود_را_اینجا_بگذارید")
DOMAIN = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "pompnet-dashboard.up.railway.app")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("🔗 Get Config", url=f"https://{DOMAIN}/sub"),
        InlineKeyboardButton("📱 Supported Clients", callback_data="clients"),
        InlineKeyboardButton("📊 Usage", callback_data="usage"),
        InlineKeyboardButton("🐙 GitHub", url="https://github.com/uxurx7rh7e7xr73uue73e8/pompnet-dashboard")
    )
    
    text = (
        "🤖 *Pomp Net Panel Bot*\n\n"
        "🧩 Source: GitHub\n"
        "💙 This service is completely free and is not for sale.\n"
        "این سرویس کاملاً رایگان است و فروشی نیست.\n\n"
        "Choose an option:"
    )
    
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    if call.data == "clients":
        bot.answer_callback_query(call.id, "کلاینت‌های پشتیبانی‌شده: v2rayNG, Sing-box, Shadowrocket", show_alert=True)
    elif call.data == "usage":
        bot.answer_callback_query(call.id, "حجم مصرفی شما: 12.4 GB از 100 GB", show_alert=True)

if __name__ == "__main__":
    bot.infinity_polling()
