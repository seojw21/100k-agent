import os
import json
import sqlite3
import httpx
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import anthropic
from bs4 import BeautifulSoup

# ─── Config ───────────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
PAYPAL_CLIENT_ID = os.environ.get("PAYPAL_CLIENT_ID", "")
PAYPAL_CLIENT_SECRET = os.environ.get("PAYPAL_CLIENT_SECRET", "")
PAYPAL_MODE = os.environ.get("PAYPAL_MODE", "sandbox")  # "sandbox" or "live"
BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")

PAYPAL_API = (
    "https://api-m.sandbox.paypal.com"
    if PAYPAL_MODE == "sandbox"
    else "https://api-m.paypal.com"
)

FREE_QUOTA = 5          # free emails per account
PRO_MONTHLY_PRICE = 19  # USD
PRO_QUOTA = 300         # emails per month on pro plan

# ─── DB ───────────────────────────────────────────────────────────────────────
DB_PATH = "coldcraft.db"

def init_db():
    con = sqlite3.connect(DB_PATH)
    con.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            plan TEXT DEFAULT 'free',
            usage_count INTEGER DEFAULT 0,
            plan_expires TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            order_id TEXT PRIMARY KEY,
            email TEXT,
            status TEXT,
            amount REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    con.commit()
    con.close()

def get_user(email: str) -> dict:
    con = sqlite3.connect(DB_PATH)
    row = con.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    con.close()
    if not row:
        return None
    return dict(zip(["email","plan","usage_count","plan_expires","created_at"], row))

def upsert_user(email: str, **kwargs):
    con = sqlite3.connect(DB_PATH)
    user = con.execute("SELECT email FROM users WHERE email=?", (email,)).fetchone()
    if user:
        sets = ", ".join(f"{k}=?" for k in kwargs)
        con.execute(f"UPDATE users SET {sets} WHERE email=?", (*kwargs.values(), email))
    else:
        con.execute("INSERT INTO users (email) VALUES (?)", (email,))
        if kwargs:
            sets = ", ".join(f"{k}=?" for k in kwargs)
            con.execute(f"UPDATE users SET {sets} WHERE email=?", (*kwargs.values(), email))
    con.commit()
    con.close()

def increment_usage(email: str):
    con = sqlite3.connect(DB_PATH)
    con.execute("UPDATE users SET usage_count=usage_count+1 WHERE email=?", (email,))
    con.commit()
    con.close()

# ─── PayPal helpers ───────────────────────────────────────────────────────────
async def paypal_token() -> str:
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{PAYPAL_API}/v1/oauth2/token",
            auth=(PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET),
            data={"grant_type": "client_credentials"},
        )
        r.raise_for_status()
        return r.json()["access_token"]

async def create_paypal_order(email: str) -> dict:
    token = await paypal_token()
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{PAYPAL_API}/v2/checkout/orders",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={
                "intent": "CAPTURE",
                "purchase_units": [{
                    "amount": {"currency_code": "USD", "value": str(PRO_MONTHLY_PRICE)},
                    "description": "ColdCraft Pro - 300 AI emails/month",
                    "custom_id": email,
                }],
                "application_context": {
                    "return_url": f"{BASE_URL}/payment/success",
                    "cancel_url": f"{BASE_URL}/payment/cancel",
                    "brand_name": "ColdCraft",
                    "user_action": "PAY_NOW",
                },
            },
        )
        r.raise_for_status()
        return r.json()

async def capture_paypal_order(order_id: str) -> dict:
    token = await paypal_token()
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{PAYPAL_API}/v2/checkout/orders/{order_id}/capture",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        )
        r.raise_for_status()
        return r.json()

# ─── AI helpers ───────────────────────────────────────────────────────────────
async def scrape_url(url: str) -> str:
    if not url.startswith("http"):
        url = "https://" + url
    try:
        async with httpx.AsyncClient(timeout=8, follow_redirects=True) as client:
            r = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(r.text, "html.parser")
            for tag in soup(["script","style","nav","footer","header"]):
                tag.decompose()
            text = " ".join(soup.get_text(separator=" ").split())
            return text[:3000]
    except Exception:
        return ""

def generate_email(company_info: str, your_service: str, your_name: str, tone: str) -> str:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    prompt = f"""You are an expert cold email copywriter. Write a short, highly personalized cold email.

Company/prospect info scraped from their website:
{company_info or "(no info available — write based on service fit)"}

Your service: {your_service}
Your name: {your_name}
Tone: {tone}

Rules:
- Max 120 words in the body
- First sentence must reference something SPECIFIC about the company (not generic)
- One clear CTA (15-minute call or reply)
- No buzzwords ("synergy", "leverage", "world-class")
- Subject line + body only
- Sound human, not like AI wrote it

Format:
Subject: [subject line]

[email body]"""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text.strip()

# ─── App ──────────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="ColdCraft", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ─── Routes ───────────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

class GenerateRequest(BaseModel):
    email: str
    target_url: str
    your_service: str
    your_name: str
    tone: str = "professional"

@app.post("/generate")
async def generate(req: GenerateRequest):
    if not req.email or "@" not in req.email:
        raise HTTPException(400, "Valid email required")

    user = get_user(req.email)
    if not user:
        upsert_user(req.email, plan="free", usage_count=0)
        user = get_user(req.email)

    # Check quota
    quota = PRO_QUOTA if user["plan"] == "pro" else FREE_QUOTA
    if user["plan"] == "pro" and user["plan_expires"]:
        if datetime.fromisoformat(user["plan_expires"]) < datetime.utcnow():
            upsert_user(req.email, plan="free")
            quota = FREE_QUOTA

    if user["usage_count"] >= quota:
        return JSONResponse({"error": "quota_exceeded", "plan": user["plan"]}, status_code=402)

    # Scrape + generate
    company_info = await scrape_url(req.target_url)
    email_text = generate_email(company_info, req.your_service, req.your_name, req.tone)
    increment_usage(req.email)

    return {"email": email_text, "usage": user["usage_count"] + 1, "quota": quota}

@app.post("/checkout")
async def checkout(request: Request):
    body = await request.json()
    email = body.get("email", "")
    if not email or "@" not in email:
        raise HTTPException(400, "Valid email required")

    order = await create_paypal_order(email)
    approve_url = next(l["href"] for l in order["links"] if l["rel"] == "approve")

    # Save pending payment
    con = sqlite3.connect(DB_PATH)
    con.execute(
        "INSERT OR REPLACE INTO payments (order_id, email, status, amount) VALUES (?,?,?,?)",
        (order["id"], email, "pending", PRO_MONTHLY_PRICE),
    )
    con.commit()
    con.close()

    return {"approve_url": approve_url, "order_id": order["id"]}

@app.get("/payment/success")
async def payment_success(request: Request, token: str = None):
    if not token:
        return RedirectResponse("/")

    try:
        result = await capture_paypal_order(token)
    except Exception:
        return templates.TemplateResponse("success.html", {"request": request, "success": False})

    if result.get("status") == "COMPLETED":
        unit = result["purchase_units"][0]
        email = unit.get("custom_id", "")

        if email:
            expires = (datetime.utcnow() + timedelta(days=31)).isoformat()
            upsert_user(email, plan="pro", usage_count=0, plan_expires=expires)
            con = sqlite3.connect(DB_PATH)
            con.execute("UPDATE payments SET status='completed' WHERE order_id=?", (token,))
            con.commit()
            con.close()

    return templates.TemplateResponse("success.html", {"request": request, "success": True, "email": email})

@app.get("/payment/cancel")
async def payment_cancel(request: Request):
    return RedirectResponse("/?cancelled=1")

@app.get("/status")
async def status(email: str):
    user = get_user(email)
    if not user:
        return {"plan": "free", "usage": 0, "quota": FREE_QUOTA}
    quota = PRO_QUOTA if user["plan"] == "pro" else FREE_QUOTA
    return {"plan": user["plan"], "usage": user["usage_count"], "quota": quota, "expires": user["plan_expires"]}
