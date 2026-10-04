import os
import base64
import threading
import psutil
from fastapi import FastAPI, Request, Form, Response, Cookie
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

import mohammad_core as config

os.environ['TZ'] = 'Asia/Tehran'

app = FastAPI(title=config.PANEL_TITLE)

os.makedirs("templates", exist_ok=True)
templates = Jinja2Templates(directory="templates")

# تابع اجرای ربات تلگرام در پس‌زمینه
def run_telegram_bot():
    while True:
        try:
            token = config.PANEL_CONFIG["bot_token"]
            if token and token != "توکن_ربات_خود_را_اینجا_بگذارید":
                bot = telebot.TeleBot(token)

                @bot.message_handler(commands=['start'])
                def send_welcome(message):
                    markup = InlineKeyboardMarkup(row_width=1)
                    markup.add(
                        InlineKeyboardButton("🔗 Get Config", url=f"https://{config.RAILWAY_PUBLIC_DOMAIN}/sub"),
                        InlineKeyboardButton("📱 Supported Clients", callback_data="clients"),
                        InlineKeyboardButton("📊 Usage", callback_data="usage"),
                        InlineKeyboardButton("🐙 GitHub", url=config.SOCIAL_LINKS["github_project"])
                    )
                    
                    text = (
                        "🤖 *Mohammad Panel Bot*\n\n"
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

                bot.infinity_polling(none_stop=True)
        except Exception as e:
            print(f"Bot error: {e}")
        import time
        time.sleep(5)

@app.on_event("startup")
async def startup_event():
    bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    bot_thread.start()

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str = None):
    return templates.TemplateResponse("login.html", {"request": request, "error": error})

@app.post("/login")
async def login_action(response: Response, username: str = Form(...), password: str = Form(...)):
    if username == config.PANEL_CONFIG["username"] and password == config.PANEL_CONFIG["password"]:
        resp = RedirectResponse(url="/", status_code=303)
        resp.set_cookie(key="mohammad_session", value="authenticated", httponly=True)
        return resp
    return RedirectResponse(url="/login?error=1", status_code=303)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, mohammad_session: str = Cookie(None)):
    if mohammad_session != "authenticated":
        return RedirectResponse(url="/login", status_code=303)

    domain = request.headers.get("host", config.RAILWAY_PUBLIC_DOMAIN)
    stats = {
        "cpu": psutil.cpu_percent(interval=None),
        "ram": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent,
        "total_active": 4
    }
    return templates.TemplateResponse("panel_home.html", {
        "request": request,
        "title": config.PANEL_TITLE,
        "brand": config.BRAND_NAME,
        "logo": config.LOGO_URL,
        "stats": stats,
        "sub_link": f"https://{domain}/sub",
        "config": config.PANEL_CONFIG,
        "social": config.SOCIAL_LINKS,
        "inbounds": [
            {"name": "Mohammad-VLESS-WS", "protocol": "VLESS", "port": 443, "status": "Active", "link": f"vless://test-uuid@{domain}:443?type=ws#Mohammad-VLESS"}
        ]
    })

@app.post("/update-settings")
async def update_settings(
    new_username: str = Form(...),
    new_password: str = Form(None),
    bot_token: str = Form(...),
    admin_id: str = Form(...)
):
    config.PANEL_CONFIG["username"] = new_username
    if new_password and new_password.strip():
        config.PANEL_CONFIG["password"] = new_password
    config.PANEL_CONFIG["bot_token"] = bot_token
    config.PANEL_CONFIG["admin_id"] = admin_id
    return RedirectResponse(url="/", status_code=303)

@app.get("/logout")
async def logout():
    resp = RedirectResponse(url="/login", status_code=303)
    resp.delete_cookie(key="mohammad_session")
    return resp

@app.get("/sub")
async def get_subscription(request: Request):
    domain = request.headers.get("host", config.RAILWAY_PUBLIC_DOMAIN)
    links = [f"vless://test-uuid@{domain}:443?type=ws#Mohammad-VLESS"]
    raw_sub = "\n".join(links)
    b64_sub = base64.b64encode(raw_sub.encode('utf-8')).decode('utf-8')
    return PlainTextResponse(b64_sub)
