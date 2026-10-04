import os
import json
import base64
import uuid
import subprocess
import urllib.request
from fastapi import FastAPI, Request, Form, Response
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import psutil
import app_config

app = FastAPI(title=app_config.PANEL_TITLE)
templates = Jinja2Templates(directory="templates")

XRAY_BINARY_PATH = "/tmp/xray"
XRAY_CONFIG_PATH = "/tmp/config.json"

def download_and_setup_xray():
    """دانلود و تنظیم باینری واقعی Xray-core در صورت عدم وجود"""
    if not os.path.exists(XRAY_BINARY_PATH):
        print("Downloading Xray-core binary...")
        url = "https://github.com/XTLS/Xray-core/releases/latest/download/Xray-linux-64.zip"
        zip_path = "/tmp/xray.zip"
        urllib.request.urlretrieve(url, zip_path)
        subprocess.run(["unzip", "-o", zip_path, "xray", "-d", "/tmp/"], check=True)
        subprocess.run(["chmod", "+x", XRAY_BINARY_PATH], check=True)
        print("Xray-core installed successfully.")

def generate_xray_config(port: int):
    """تولید کانفیگ JSON واقعی برای اجرا در Xray-core"""
    inbounds = []
    for item in app_config.INITIAL_INBOUNDS:
        path = item["path"]
        uid = item["uuid"]
        proto = item["protocol"].lower()

        if proto == "vless":
            inbounds.append({
                "port": port,
                "protocol": "vless",
                "settings": {
                    "clients": [{"id": uid, "level": 0}],
                    "decryption": "none"
                },
                "streamSettings": {
                    "network": "ws" if "WebSocket" in item["type"] else "httpupgrade",
                    "wsSettings": {"path": path} if "WebSocket" in item["type"] else None,
                    "httpupgradeSettings": {"path": path} if "HTTPUpgrade" in item["type"] else None
                }
            })
        elif proto == "vmess":
            inbounds.append({
                "port": port,
                "protocol": "vmess",
                "settings": {
                    "clients": [{"id": uid, "alterId": 0}]
                },
                "streamSettings": {
                    "network": "ws",
                    "wsSettings": {"path": path}
                }
            })
        elif proto == "trojan":
            inbounds.append({
                "port": port,
                "protocol": "trojan",
                "settings": {
                    "clients": [{"password": uid}]
                },
                "streamSettings": {
                    "network": "ws",
                    "wsSettings": {"path": path}
                }
            })

    xray_json = {
        "log": {"loglevel": "warning"},
        "inbounds": inbounds,
        "outbounds": [{"protocol": "freedom"}]
    }

    with open(XRAY_CONFIG_PATH, "w") as f:
        json.dump(xray_json, f, indent=2)

def start_xray_process(port: int):
    """راه‌اندازی فرایند Xray در پس‌زمینه"""
    try:
        download_and_setup_xray()
        generate_xray_config(port)
        subprocess.Popen([XRAY_BINARY_PATH, "run", "-c", XRAY_CONFIG_PATH])
        print("Xray engine started successfully!")
    except Exception as e:
        print(f"Xray startup notice: {e}")

@app.on_event("startup")
async def startup_event():
    port = int(os.environ.get("PORT", 8080))
    start_xray_process(port)

def build_client_link(item, domain):
    """ساخت لینک‌های استاندارد و واقعی VLESS / VMess / Trojan"""
    proto = item["protocol"].lower()
    uid = item["uuid"]
    path = item["path"]
    name = item["name"]

    if proto == "vless":
        return f"vless://{uid}@{domain}:443?type=ws&security=tls&path={path}&host={domain}#{name}"
    elif proto == "vmess":
        vmess_data = {
            "v": "2", "ps": name, "add": domain, "port": "443",
            "id": uid, "aid": "0", "scy": "auto", "net": "ws",
            "type": "none", "host": domain, "path": path, "tls": "tls"
        }
        return "vmess://" + base64.b64encode(json.dumps(vmess_data).encode()).decode()
    elif proto == "trojan":
        return f"trojan://{uid}@{domain}:443?type=ws&security=tls&path={path}&host={domain}#{name}"
    return ""

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    domain = request.headers.get("host", app_config.RAILWAY_PUBLIC_DOMAIN)
    sub_link = f"https://{domain}/sub"
    
    inbounds_with_links = []
    for item in app_config.INITIAL_INBOUNDS:
        item_copy = item.copy()
        item_copy["link"] = build_client_link(item, domain)
        inbounds_with_links.append(item_copy)

    stats = {
        "cpu": psutil.cpu_percent(interval=None),
        "ram": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent,
        "total_active": len(app_config.INITIAL_INBOUNDS)
    }

    return templates.TemplateResponse("panel_view.html", {
        "request": request,
        "title": app_config.PANEL_TITLE,
        "brand": app_config.BRAND_NAME,
        "logo": app_config.LOGO_URL,
        "stats": stats,
        "inbounds": inbounds_with_links,
        "sub_link": sub_link
    })

@app.post("/add-inbound")
async def add_inbound(
    name: str = Form(...),
    protocol: str = Form(...),
    transport: str = Form(...)
):
    """ساخت آنلاین و آنی کانفیگ جدید درون پنل"""
    new_id = str(len(app_config.INITIAL_INBOUNDS) + 1)
    new_uuid = str(uuid.uuid4())
    path = f"/pompnet-{protocol.lower()}-{new_id}"
    
    new_item = {
        "id": new_id,
        "name": name,
        "protocol": protocol,
        "type": transport,
        "path": path,
        "port": 443,
        "uuid": new_uuid,
        "status": "Active"
    }
    app_config.INITIAL_INBOUNDS.append(new_item)
    
    port = int(os.environ.get("PORT", 8080))
    generate_xray_config(port)
    return RedirectResponse(url="/", status_code=303)

@app.get("/sub", response_class=PlainTextResponse)
async def get_subscription(request: Request):
    domain = request.headers.get("host", app_config.RAILWAY_PUBLIC_DOMAIN)
    links = [build_client_link(item, domain) for item in app_config.INITIAL_INBOUNDS]
    return "\n".join(links)

@app.get("/sub/b64", response_class=PlainTextResponse)
async def get_subscription_b64(request: Request):
    domain = request.headers.get("host", app_config.RAILWAY_PUBLIC_DOMAIN)
    links = "\n".join([build_client_link(item, domain) for item in app_config.INITIAL_INBOUNDS])
    return base64.b64encode(links.encode('utf-8')).decode('utf-8')

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main_engine:app", host="0.0.0.0", port=port)
