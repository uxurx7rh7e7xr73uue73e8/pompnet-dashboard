from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import psutil
import os
import datetime
import config

app = FastAPI(title=config.PANEL_TITLE)

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    stats = {
        "cpu": psutil.cpu_percent(interval=None),
        "ram": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent,
        "services_count": len(config.SERVICES)
    }
    return templates.TemplateResponse("panel_view.html", {
        "request": request,
        "title": config.PANEL_TITLE,
        "stats": stats,
        "services": config.SERVICES,
        "repos": config.REPOSITORIES,
        "domains": config.DOMAINS
    })

@app.get("/api/stats")
async def get_stats():
    return {
        "cpu": psutil.cpu_percent(interval=None),
        "ram": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent,
        "time": datetime.datetime.now().strftime("%H:%M:%S")
    }

@app.post("/api/service/{service_id}/restart")
async def restart_service(service_id: int):
    for service in config.SERVICES:
        if service["id"] == service_id:
            service["status"] = "Active"
            return {"status": "success", "message": f"Service {service['name']} restarted successfully."}
    raise HTTPException(status_code=404, detail="Service not found")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("server:app", host="0.0.0.0", port=port)
