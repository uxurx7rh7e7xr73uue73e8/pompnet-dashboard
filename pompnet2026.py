import os
import json
import secrets
import sqlite3
import urllib.request
from datetime import datetime, timezone

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware


VERSION = "2026.10.05"
BRAND = "MR:Mohammad Pomp Net"
DB = "pompnet2026.db"

ADMIN_PASSWORD = os.getenv("POMPNET_ADMIN_PASSWORD", "")
SESSION_SECRET = os.getenv(
    "POMPNET_SESSION_SECRET",
    secrets.token_hex(32)
)

app = FastAPI(
    title=BRAND,
    version=VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    same_site="lax"
)


def database():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():

    conn = database()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS clients(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        protocol TEXT NOT NULL,
        link TEXT NOT NULL,
        token TEXT UNIQUE NOT NULL,
        created_at TEXT NOT NULL
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS bots(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        token TEXT NOT NULL,
        username TEXT DEFAULT '',
        enabled INTEGER DEFAULT 1,
        created_at TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()


init_database()


def now():
    return datetime.now(timezone.utc).isoformat()


def detect_protocol(link):

    link = link.strip().lower()

    if link.startswith("vless://"):
        return "VLESS"

    if link.startswith("vmess://"):
        return "VMESS"

    if link.startswith("trojan://"):
        return "Trojan"

    if link.startswith("ss://"):
        return "Shadowsocks"

    if link.startswith("hysteria2://"):
        return "Hysteria2"

    if link.startswith("hy2://"):
        return "Hysteria2"

    if link.startswith("tuic://"):
        return "TUIC"

    return "Unknown"


def telegram_get(token, method):

    url = f"https://api.telegram.org/bot{token}/{method}"

    try:

        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "PompNet/2026"
            }
        )

        with urllib.request.urlopen(
            request,
            timeout=15
        ) as response:

            return json.loads(
                response.read().decode()
            )

    except Exception as error:

        return {
            "ok": False,
            "error": str(error)
        }


def is_login(request):

    return request.session.get("admin") is True


# -----------------------------
# LOGIN
# -----------------------------

@app.get("/login", response_class=HTMLResponse)
async def login_page():

    return HTMLResponse("""
<!DOCTYPE html>
<html lang="fa" dir="rtl">

<head>

<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width,initial-scale=1">

<title>PompNet Login</title>

<style>

body{
margin:0;
min-height:100vh;
display:flex;
align-items:center;
justify-content:center;
background:#050509;
color:white;
font-family:Tahoma;
}

.box{
width:90%;
max-width:400px;
padding:30px;
background:#11111d;
border:1px solid #743cff;
border-radius:25px;
box-shadow:0 0 40px #743cff44;
text-align:center;
}

input{
width:100%;
box-sizing:border-box;
padding:15px;
margin:15px 0;
border-radius:12px;
border:1px solid #393950;
background:#07070d;
color:white;
}

button{
width:100%;
padding:15px;
border:0;
border-radius:12px;
background:linear-gradient(90deg,#743cff,#168cff);
color:white;
font-weight:bold;
font-size:16px;
}

small{
color:#888;
}

</style>

</head>

<body>

<div class="box">

<h1>🚀 PompNet</h1>

<h3>MR:Mohammad Pomp Net</h3>

<form method="post" action="/login">

<input
type="password"
name="password"
placeholder="رمز ورود پنل"
required>

<button>
ورود
</button>

</form>

<br>

<small>
نسخه پنل: 2026.10.05
</small>

</div>

</body>

</html>
""")


@app.post("/login")
async def login(
    request: Request,
    password: str = Form(...)
):

    if not ADMIN_PASSWORD:

        return HTMLResponse(
            "POMPNET_ADMIN_PASSWORD در Railway تنظیم نشده است.",
            status_code=500
        )

    if secrets.compare_digest(
        password,
        ADMIN_PASSWORD
    ):

        request.session["admin"] = True

        return RedirectResponse(
            "/",
            status_code=303
        )

    return HTMLResponse(
        "رمز ورود اشتباه است.",
        status_code=401
    )


@app.get("/logout")
async def logout(request: Request):

    request.session.clear()

    return RedirectResponse("/login")


# -----------------------------
# MAIN PANEL
# -----------------------------

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    if not is_login(request):

        return RedirectResponse("/login")

    try:

        with open(
            "pompnet2026.html",
            "r",
            encoding="utf-8"
        ) as file:

            return HTMLResponse(
                file.read()
            )

    except FileNotFoundError:

        return HTMLResponse(
            "فایل pompnet2026.html پیدا نشد.",
            status_code=500
        )


# -----------------------------
# HEALTH
# -----------------------------

@app.get("/health")
async def health():

    return {
        "status": "ok",
        "panel": BRAND,
        "version": VERSION,
        "time": now()
    }


# -----------------------------
# OVERVIEW
# -----------------------------

@app.get("/api/overview")
async def overview(request: Request):

    if not is_login(request):

        return JSONResponse(
            {"error": "unauthorized"},
            status_code=401
        )

    conn = database()

    clients = conn.execute(
        "SELECT COUNT(*) AS c FROM clients"
    ).fetchone()["c"]

    bots = conn.execute(
        "SELECT COUNT(*) AS c FROM bots"
    ).fetchone()["c"]

    conn.close()

    return {
        "brand": BRAND,
        "version": VERSION,
        "clients": clients,
        "bots": bots
    }


# -----------------------------
# VPN CLIENTS
# -----------------------------

@app.get("/api/clients")
async def get_clients(request: Request):

    if not is_login(request):

        return JSONResponse(
            {"error": "unauthorized"},
            status_code=401
        )

    conn = database()

    rows = conn.execute("""
        SELECT id,name,protocol,link,token,created_at
        FROM clients
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return [
        dict(row)
        for row in rows
    ]


@app.post("/api/clients")
async def create_client(
    request: Request,
    name: str = Form(...),
    link: str = Form(...)
):

    if not is_login(request):

        return JSONResponse(
            {"error": "unauthorized"},
            status_code=401
        )

    protocol = detect_protocol(link)

    if protocol == "Unknown":

        return JSONResponse(
            {
                "error":
                "پروتکل ناشناخته است."
            },
            status_code=400
        )

    token = secrets.token_urlsafe(24)

    conn = database()

    conn.execute("""
        INSERT INTO clients
        (name,protocol,link,token,created_at)
        VALUES(?,?,?,?,?)
    """, (
        name,
        protocol,
        link,
        token,
        now()
    ))

    conn.commit()
    conn.close()

    return {
        "ok": True,
        "protocol": protocol,
        "subscription":
        f"/sub/{token}"
    }


@app.delete("/api/clients/{client_id}")
async def delete_client(
    client_id: int,
    request: Request
):

    if not is_login(request):

        return JSONResponse(
            {"error": "unauthorized"},
            status_code=401
        )

    conn = database()

    conn.execute(
        "DELETE FROM clients WHERE id=?",
        (client_id,)
    )

    conn.commit()
    conn.close()

    return {"ok": True}


# -----------------------------
# SUBSCRIPTION
# -----------------------------

@app.get("/sub/{token}")
async def subscription(token: str):

    conn = database()

    row = conn.execute(
        """
        SELECT link
        FROM clients
        WHERE token=?
        """,
        (token,)
    ).fetchone()

    conn.close()

    if not row:

        return HTMLResponse(
            "Subscription not found",
            status_code=404
        )

    return HTMLResponse(
        row["link"],
        media_type="text/plain"
    )


# -----------------------------
# TELEGRAM BOTS
# -----------------------------

@app.get("/api/bots")
async def get_bots(request: Request):

    if not is_login(request):

        return JSONResponse(
            {"error": "unauthorized"},
            status_code=401
        )

    conn = database()

    rows = conn.execute("""
        SELECT id,name,username,enabled,created_at
        FROM bots
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return [
        dict(row)
        for row in rows
    ]


@app.post("/api/bots")
async def create_bot(
    request: Request,
    name: str = Form(...),
    token: str = Form(...)
):

    if not is_login(request):

        return JSONResponse(
            {"error": "unauthorized"},
            status_code=401
        )

    telegram = telegram_get(
        token,
        "getMe"
    )

    if not telegram.get("ok"):

        return JSONResponse(
            {
                "error":
                "Bot Token معتبر نیست."
            },
            status_code=400
        )

    username = telegram[
        "result"
    ].get(
        "username",
        ""
    )

    conn = database()

    conn.execute("""
        INSERT INTO bots
        (name,token,username,enabled,created_at)
        VALUES(?,?,?,?,?)
    """, (
        name,
        token,
        username,
        1,
        now()
    ))

    conn.commit()
    conn.close()

    return {
        "ok": True,
        "username": username
    }


@app.post("/api/bots/{bot_id}/test")
async def test_bot(
    bot_id: int,
    request: Request
):

    if not is_login(request):

        return JSONResponse(
            {"error": "unauthorized"},
            status_code=401
        )

    conn = database()

    row = conn.execute(
        """
        SELECT token
        FROM bots
        WHERE id=?
        """,
        (bot_id,)
    ).fetchone()

    conn.close()

    if not row:

        return JSONResponse(
            {"error": "Bot not found"},
            status_code=404
        )

    return telegram_get(
        row["token"],
        "getMe"
    )


@app.delete("/api/bots/{bot_id}")
async def delete_bot(
    bot_id: int,
    request: Request
):

    if not is_login(request):

        return JSONResponse(
            {"error": "unauthorized"},
            status_code=401
        )

    conn = database()

    conn.execute(
        "DELETE FROM bots WHERE id=?",
        (bot_id,)
    )

    conn.commit()
    conn.close()

    return {"ok": True}


# -----------------------------
# CLOUDFLARE
# -----------------------------

@app.get("/api/cloudflare")
async def cloudflare(
    request: Request
):

    if not is_login(request):

        return JSONResponse(
            {"error": "unauthorized"},
            status_code=401
        )

    token = os.getenv(
        "CLOUDFLARE_API_TOKEN"
    )

    zone = os.getenv(
        "CLOUDFLARE_ZONE_ID"
    )

    if not token or not zone:

        return {
            "configured": False,
            "message":
            "Cloudflare Token یا Zone ID تنظیم نشده."
        }

    req = urllib.request.Request(
        f"https://api.cloudflare.com/client/v4/zones/{zone}",
        headers={
            "Authorization":
            f"Bearer {token}",
            "Content-Type":
            "application/json"
        }
    )

    try:

        with urllib.request.urlopen(
            req,
            timeout=15
        ) as response:

            return {
                "configured": True,
                "data":
                json.loads(
                    response.read().decode()
                )
            }

    except Exception as error:

        return {
            "configured": True,
            "error": str(error)
        }


# -----------------------------
# GITHUB
# -----------------------------

@app.get("/api/github")
async def github(
    request: Request
):

    if not is_login(request):

        return JSONResponse(
            {"error": "unauthorized"},
            status_code=401
        )

    token = os.getenv(
        "GITHUB_TOKEN"
    )

    repo = os.getenv(
        "GITHUB_REPO",
        "uxurx7rh7e7xr73uue73e8/pompnet-dashboard"
    )

    if not token:

        return {
            "configured": False,
            "repo": repo
        }

    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo}",
        headers={
            "Authorization":
            f"Bearer {token}",
            "Accept":
            "application/vnd.github+json"
        }
    )

    try:

        with urllib.request.urlopen(
            req,
            timeout=15
        ) as response:

            return {
                "configured": True,
                "repo": repo,
                "data":
                json.loads(
                    response.read().decode()
                )
            }

    except Exception as error:

        return {
            "configured": True,
            "repo": repo,
            "error": str(error)
        }


# -----------------------------
# RAILWAY
# -----------------------------

@app.get("/api/railway")
async def railway(
    request: Request
):

    if not is_login(request):

        return JSONResponse(
            {"error": "unauthorized"},
            status_code=401
        )

    return {
        "configured":
        bool(
            os.getenv(
                "RAILWAY_API_TOKEN"
            )
        ),
        "project":
        os.getenv(
            "RAILWAY_PROJECT_ID",
            ""
        ),
        "environment":
        os.getenv(
            "RAILWAY_ENVIRONMENT_ID",
            ""
        ),
        "service":
        os.getenv(
            "RAILWAY_SERVICE_ID",
            ""
        )
    }


# -----------------------------
# CONFIG
# -----------------------------

@app.get("/api/config")
async def config():

    return {
        "brand": BRAND,
        "version": VERSION,
        "github":
        "https://github.com/uxurx7rh7e7xr73uue73e8/pompnet-dashboard",
        "telegram":
        "https://t.me/PompNett",
        "support":
        "@NovaTunneli",
        "protocols": [
            "VLESS",
            "VMESS",
            "Trojan",
            "Shadowsocks",
            "Hysteria2",
            "TUIC"
        ]
    }


# -----------------------------
# START
# -----------------------------

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "pompnet2026:app",
        host="0.0.0.0",
        port=int(
            os.getenv(
                "PORT",
                "8080"
            )
        )
    )
