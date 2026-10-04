from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import psutil
import os
import datetime

app = FastAPI(title="PompNet Pro Panel")

# تنظیم مسیر قالب‌های HTML
templates = Jinja2Templates(directory="templates")

# لیست سرویس‌های نمونه
SERVICES = [
    {"id": 1, "name": "V2Ray / Xray Core", "type": "Proxy Node", "status": "Active", "port": 443},
    {"id": 2, "name": "Telegram Bot", "type": "Python Bot", "status": "Active", "port": 8080},
    {"id": 3, "name": "Cloudflare DNS Manager", "type": "Networking", "status": "Active", "port": 8443},
]

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    stats = {
        "cpu": psutil.cpu_percent(interval=None),
        "ram": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent,
        "services_count": len(SERVICES)
    }
    return templates.TemplateResponse("index.html", {
        "request": request,
        "stats": stats,
        "services": SERVICES
    })

@app.get("/api/stats")
async def get_stats():
    return {
        "cpu": psutil.cpu_percent(interval=None),
        "ram": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent,
        "time": datetime.datetime.now().strftime("%H:%M:%S")
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
