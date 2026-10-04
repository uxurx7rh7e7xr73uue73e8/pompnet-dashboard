# PompNet Panel Configuration

PANEL_TITLE = "PompNet Deploy & Control Panel"

SERVICES = [
    {"id": 1, "name": "V2Ray / Xray Core", "type": "Proxy Node", "status": "Active", "port": 443, "uptime": "99.9%"},
    {"id": 2, "name": "PompNet Telegram Bot", "type": "Python Bot", "status": "Active", "port": 8080, "uptime": "100%"},
    {"id": 3, "name": "Cloudflare DNS Manager", "type": "Networking", "status": "Active", "port": 8443, "uptime": "99.8%"},
    {"id": 4, "name": "ParsPack & VPS Monitor", "type": "Server Check", "status": "Active", "port": 9090, "uptime": "99.5%"},
]

REPOSITORIES = [
    {"name": "pompnet-panel", "branch": "main", "status": "Synced", "last_commit": "Fix layout & dark theme"},
    {"name": "azadnet-android", "branch": "main", "status": "Synced", "last_commit": "Jetpack Compose UI update"},
    {"name": "telegram-bot-python", "branch": "master", "status": "Building", "last_commit": "Add phonenumbers parsing"}
]

DOMAINS = [
    {
        "domain": "pasargad.ir",
        "subdomain": "digitalghost",
        "ip": "185.220.101.4",
        "proxy": True,
        "ssl": "Full (Strict)"
    }
]
