import os

BRAND_NAME = "MR:Mohammad GhostCore"
PANEL_TITLE = "MR:Mohammad GhostCore - Ultimate Panel"
LOGO_URL = "https://cdn-icons-png.flaticon.com/512/9438/9438883.png"

RAILWAY_PUBLIC_DOMAIN = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "ghostcore.up.railway.app")

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
        "name": "Ghost-VLESS-WS-TLS",
        "protocol": "VLESS",
        "type": "WebSocket CDN",
        "path": "/ghost-vless-ws",
        "port": 443,
        "uuid": "8f3c9a12-4b2e-4e5a-8212-9c3f1e8a1001",
        "status": "Active"
    },
    {
        "id": "2",
        "name": "Ghost-VMess-WS-CDN",
        "protocol": "VMess",
        "type": "WebSocket CDN",
        "path": "/ghost-vmess-ws",
        "port": 8443,
        "uuid": "7b2a8d11-3c1e-4f6a-9101-8b2f0d7a2002",
        "status": "Active"
    },
    {
        "id": "3",
        "name": "Ghost-Trojan-WS-TLS",
        "protocol": "Trojan",
        "type": "WebSocket CDN",
        "path": "/ghost-trojan-ws",
        "port": 2096,
        "uuid": "ghost-trojan-secret-pass",
        "status": "Active"
    },
    {
        "id": "4",
        "name": "Ghost-Shadowsocks-2022",
        "protocol": "Shadowsocks",
        "type": "TCP / AEAD",
        "path": "/ghost-ss",
        "port": 8388,
        "uuid": "ghost-ss-key-2026-v1",
        "status": "Active"
    },
    {
        "id": "5",
        "name": "Ghost-Hysteria2-QUIC",
        "protocol": "Hysteria2",
        "type": "UDP / QUIC",
        "path": "/ghost-hy2",
        "port": 8443,
        "uuid": "ghost-hy2-pass-99",
        "status": "Active"
    },
    {
        "id": "6",
        "name": "Ghost-TUIC-v5",
        "protocol": "TUIC",
        "type": "UDP / QUIC",
        "path": "/ghost-tuic",
        "port": 8443,
        "uuid": "ghost-tuic-token-77",
        "status": "Active"
    }
]
