import os

BRAND_NAME = "Mohammad Panel"
PANEL_TITLE = "Mohammad - Pro Management Panel"
LOGO_URL = "https://cdn-icons-png.flaticon.com/512/9438/9438883.png"

# تنظیمات پیش‌فرض ادمین و ربات
PANEL_CONFIG = {
    "username": "admin",
    "password": "adminpassword123",
    "bot_token": os.environ.get("TELEGRAM_BOT_TOKEN", "توکن_ربات_خود_را_اینجا_بگذارید"),
    "admin_id": os.environ.get("ADMIN_USER_ID", "123456789")
}

RAILWAY_PUBLIC_DOMAIN = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "mohammad-panel.up.railway.app")

SOCIAL_LINKS = {
    "github_project": "https://github.com/uxurx7rh7e7xr73uue73e8/pompnet-dashboard",
    "admin_telegram": "https://t.me/NovaTunneli",
    "channel_telegram": "https://t.me/pompnet"
}
