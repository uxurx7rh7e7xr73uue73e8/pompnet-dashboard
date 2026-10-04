import os

BRAND_NAME = "MR:Mohammad Pomp Net"
PANEL_TITLE = "MR:Mohammad Pomp Net - Ultimate Core"
LOGO_URL = "https://cdn-icons-png.flaticon.com/512/9438/9438883.png"

RAILWAY_PUBLIC_DOMAIN = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "pompnet.up.railway.app")

SOCIAL_LINKS = {
    "github_project": "https://github.com/uxurx7rh7e7xr73uue73e8",
    "github_pull": "https://github.com/shanduzgil/sog_v2ryng/pull/2",
    "railway": "https://railway.com",
    "admin_telegram": "https://t.me/NovaTunneli",
    "channel_telegram": "https://t.me/pompnet",
    "group_telegram": "https://t.me/+UV34C7Ohs9hiZTc0",
    "rules_link": "http://45.74.158.48:8002/dashboard",
    "whatsapp_admin": "https://wa.me/message/LRTDKAYCT6IMN1"
}

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
        "name": "PompNet-Shadowsocks-2022",
        "protocol": "Shadowsocks",
        "type": "TCP / AEAD",
        "path": "/pompnet-ss",
        "port": 8388,
        "uuid": "pompnet-ss-key-2026-v1",
        "status": "Active"
    },
    {
        "id": "5",
        "name": "PompNet-Hysteria2-QUIC",
        "protocol": "Hysteria2",
        "type": "UDP / QUIC",
        "path": "/pompnet-hy2",
        "port": 8443,
        "uuid": "pompnet-hy2-pass-99",
        "status": "Active"
    },
    {
        "id": "6",
        "name": "PompNet-TUIC-v5",
        "protocol": "TUIC",
        "type": "UDP / QUIC",
        "path": "/pompnet-tuic",
        "port": 8443,
        "uuid": "pompnet-tuic-token-77",
        "status": "Active"
    }
]
