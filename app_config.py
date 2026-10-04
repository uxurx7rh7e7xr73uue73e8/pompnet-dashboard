import os

PANEL_TITLE = "PompNet Ultimate Core | پنل واقعی پمپ نت"
BRAND_NAME = "PompNet Pasargad Engine"
SUB_PORT = 2096
LOGO_URL = "https://cdn-icons-png.flaticon.com/512/9438/9438883.png"

# دامنه رسمی Railway
RAILWAY_PUBLIC_DOMAIN = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "pompnet.up.railway.app")
CUSTOM_SUBDOMAIN = "digitalghost.pasargad.ir"

# پورت‌های CDN کلادفلر که پشتیبانی می‌شوند
ALLOWED_PORTS = [2096, 443, 8443, 2053, 2083, 80, 8080, 8880]

# نمونه اینباندهای کاملاً عملیاتی و هماهنگ با CDN ریلوی
INITIAL_INBOUNDS = [
    {
        "id": "1",
        "name": "PompNet-VLESS-WS-TLS",
        "protocol": "VLESS",
        "type": "WebSocket CDN",
        "path": "/pompnet-vless-ws",
        "port": 443,
        "uuid": "8f3c9a12-4b2e-4e5a-8212-9c3f1e8a1001",
        "status": "Active"
    },
    {
        "id": "2",
        "name": "PompNet-VMess-WS-CDN",
        "protocol": "VMess",
        "type": "WebSocket CDN",
        "path": "/pompnet-vmess-ws",
        "port": 8443,
        "uuid": "7b2a8d11-3c1e-4f6a-9101-8b2f0d7a2002",
        "status": "Active"
    },
    {
        "id": "3",
        "name": "PompNet-Trojan-WS-TLS",
        "protocol": "Trojan",
        "type": "WebSocket CDN",
        "path": "/pompnet-trojan-ws",
        "port": 2096,
        "uuid": "pompnet-trojan-secret-pass",
        "status": "Active"
    },
    {
        "id": "4",
        "name": "PompNet-VLESS-HTTPUpgrade",
        "protocol": "VLESS",
        "type": "HTTPUpgrade",
        "path": "/pompnet-vless-hup",
        "port": 2053,
        "uuid": "9a1b2c3d-4e5f-6a7b-8c9d-0e1f2a3b4c5d",
        "status": "Active"
    }
]
