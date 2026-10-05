import os
import time
import platform
import socket
from pathlib import Path

import psutil
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

APP_START = time.time()

app = FastAPI(
    title="PompNet Live Panel",
    version="2026.1"
)


def safe_hostname():
    try:
        return socket.gethostname()
    except Exception:
        return "unknown"


def get_stats():
    vm = psutil.virtual_memory()

    try:
        disk = psutil.disk_usage("/")
        disk_percent = disk.percent
        disk_total = disk.total
        disk_used = disk.used
        disk_free = disk.free
    except Exception:
        disk_percent = 0
        disk_total = 0
        disk_used = 0
        disk_free = 0

    return {
        "cpu": round(psutil.cpu_percent(interval=0.15), 1),
        "ram": round(vm.percent, 1),
        "ram_total": vm.total,
        "ram_used": vm.used,
        "ram_free": vm.available,
        "disk": round(disk_percent, 1),
        "disk_total": disk_total,
        "disk_used": disk_used,
        "disk_free": disk_free,
        "hostname": safe_hostname(),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "pid": os.getpid(),
        "uptime": int(time.time() - APP_START),
        "port": os.environ.get("PORT", "unknown"),
        "railway": bool(
            os.environ.get("RAILWAY_ENVIRONMENT")
            or os.environ.get("RAILWAY_PROJECT_ID")
        )
    }


def get_processes():
    result = []

    try:
        for proc in psutil.process_iter(
            ["pid", "name", "status", "cpu_percent", "memory_percent"]
        ):
            try:
                info = proc.info

                result.append({
                    "pid": info.get("pid"),
                    "name": info.get("name") or "unknown",
                    "status": info.get("status") or "unknown",
                    "cpu": round(info.get("cpu_percent") or 0, 1),
                    "ram": round(info.get("memory_percent") or 0, 1)
                })
            except Exception:
                continue

    except Exception:
        pass

    result.sort(
        key=lambda x: x["cpu"],
        reverse=True
    )

    return result[:30]


@app.get("/", response_class=HTMLResponse)
async def home():
    html_path = Path(__file__).with_name(
        "pompnet_live_ui_2026.html"
    )

    if not html_path.exists():
        return HTMLResponse(
            "<h1>PompNet UI file not found</h1>",
            status_code=500
        )

    return HTMLResponse(
        html_path.read_text(
            encoding="utf-8"
        )
    )


@app.get("/api/live")
async def live():
    return JSONResponse(get_stats())


@app.get("/api/processes")
async def processes():
    return JSONResponse({
        "processes": get_processes()
    })


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "pompnet-live-panel"
    }


@app.get("/api/info")
async def info():
    data = get_stats()

    return {
        "hostname": data["hostname"],
        "platform": data["platform"],
        "python": data["python"],
        "pid": data["pid"],
        "port": data["port"],
        "railway": data["railway"]
    }
