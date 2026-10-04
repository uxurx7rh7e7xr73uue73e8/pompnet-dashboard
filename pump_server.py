import os
import json
import base64
import uuid
import io
import subprocess
import urllib.request
from datetime import datetime
import zoneinfo
import jdatetime
import psutil
import qrcode

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates

import pump_config as config

os.environ['TZ'] = 'Asia/Tehran'

app = FastAPI(title=config.PANEL_TITLE)
templates = Jinja2Templates(directory="templates")

XRAY_BINARY_PATH = "/tmp/xray"
XRAY_CONFIG_PATH = "/tmp/config.json"

def download_and_setup_xray():
    if not os.path.exists(XRAY_BINARY_PATH):
        try:
            url = "https://github.com/XTLS/Xray-core/releases/latest/download/Xray-linux-64.zip"
            zip_path = "/tmp/xray.zip"
            urllib.request.urlretrieve(url, zip_path)
            subprocess.run(["unzip", "-o", zip_path, "xray", "-d", "/tmp/"], check=True)
            subprocess.run(["chmod", "+x", XRAY_BINARY_PATH], check=True)
        except Exception as e:
            print(f"Xray Setup Exception: {e}")

def generate_xray_config(port: int):
    inbounds = []
    for item in config.INITIAL_INBOUNDS:
        proto = item["protocol"].lower()
        uid = item["uuid"]
        path = item["path"]

        if proto in ["vless", "vmess", "trojan"]:
            inbounds.append({
                "port": port,
                "protocol": proto,
                "settings": {"clients": [{"id": uid, "password": uid}]},
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

@app.on_event("startup")
async def startup_event():
    port = int(os.environ.get("PORT", 8080))
    download_and_setup_xray()
    generate_xray_config(port)
    if os.path.exists(XRAY_BINARY_PATH):
        try:
            subprocess.Popen([XRAY_BINARY_PATH, "run", "-c", XRAY_CONFIG_PATH])
        except Exception as e:
            print(f"Xray launch error: {e}")

def build_client_link(item, domain):
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
    elif proto == "shadowsocks":
        cipher_pass = base64.b64encode(f"2022-blake3-aes-128-gcm:{uid}".encode()).decode()
        return f"ss://{cipher_pass}@{domain}:443#{name}"
    elif proto == "hysteria2":
        return f"hy2://{uid}@{domain}:443?insecure=1&sni={domain}#{name}"
    elif proto == "tuic":
        return f"tuic://{uid}:{uid}@{domain}:443?congestion_control=bbr&alpn=h3#{name}"
    return ""

def is_vpn_client(user_agent: str) -> bool:
    user_agent_lower = user_agent.lower()
    vpn_keywords = ["v2ray", "v2rayng", "v2rayn", "streisand", "shadowrocket", "sing-box", "clash", "nekobox", "surge"]
    return any(keyword in user_agent_lower for keyword in vpn_keywords)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    domain = request.headers.get("host", config.RAILWAY_PUBLIC_DOMAIN)
    sub_link = f"https://{domain}/sub"
    
    inbounds_with_links = []
    for item in config.INITIAL_INBOUNDS:
        item_copy = item.copy()
        item_copy["link"] = build_client_link(item, domain)
        inbounds_with_links.append(item_copy)

    stats = {
        "cpu": psutil.cpu_percent(interval=None),
        "ram": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent,
        "total_active": len(config.INITIAL_INBOUNDS)
    }

    return templates.TemplateResponse("panel_home.html", {
        "request": request,
        "title": config.PANEL_TITLE,
        "brand": config.BRAND_NAME,
        "logo": config.LOGO_URL,
        "stats": stats,
        "inbounds": inbounds_with_links,
        "sub_link": sub_link,
        "social": config.SOCIAL_LINKS
    })

@app.get("/sub")
async def get_subscription(request: Request):
    user_agent = request.headers.get("user-agent", "")
    domain = request.headers.get("host", config.RAILWAY_PUBLIC_DOMAIN)
    
    links = [build_client_link(item, domain) for item in config.INITIAL_INBOUNDS]
    raw_sub = "\n".join(links)
    b64_sub = base64.b64encode(raw_sub.encode('utf-8')).decode('utf-8')

    if is_vpn_client(user_agent):
        return PlainTextResponse(b64_sub)

    tehran_tz = zoneinfo.ZoneInfo("Asia/Tehran")
    now_tehran = datetime.now(tehran_tz)
    shamsi_date = jdatetime.datetime.fromgregorian(datetime=now_tehran).strftime("%Y/%m/%d - %H:%M")
    sub_url = f"https://{domain}/sub"

    return templates.TemplateResponse("user_sub.html", {
        "request": request,
        "brand": config.BRAND_NAME,
        "logo": config.LOGO_URL,
        "sub_url": sub_url,
        "shamsi_date": shamsi_date,
        "links": links,
        "social": config.SOCIAL_LINKS,
        "used_gb": 12.4,
        "total_gb": 100,
        "days_left": 24
    })

@app.get("/qr")
async def generate_qr(text: str):
    img = qrcode.make(text)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return Response(content=buf.getvalue(), media_type="image/png")

@app.post("/add-inbound")
async def add_inbound(
    name: str = Form(...),
    protocol: str = Form(...),
    transport: str = Form(...)
):
    new_id = str(len(config.INITIAL_INBOUNDS) + 1)
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
    config.INITIAL_INBOUNDS.append(new_item)
    
    port = int(os.environ.get("PORT", 8080))
    generate_xray_config(port)
    return RedirectResponse(url="/", status_code=303)
