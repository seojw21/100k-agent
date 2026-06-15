# ColdCraft – Deploy & Launch Guide

## 1. Get API Keys (15 min)

### Anthropic (Claude API)
1. Go to https://console.anthropic.com
2. Create API key → copy it
3. Cost: ~$0.0025 per email generated (Haiku model)

### PayPal Business
1. Go to https://developer.paypal.com
2. Log in with your PayPal business account (or create one free)
3. My Apps & Credentials → Create App
4. Copy **Client ID** and **Secret**
5. For testing: use Sandbox credentials
6. For real money: use Live credentials + set PAYPAL_MODE=live

---

## 2. Deploy to Railway (10 min, free to start)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# From the coldcraft/ directory:
railway init
railway up

# Set environment variables in Railway dashboard:
# ANTHROPIC_API_KEY = sk-ant-...
# PAYPAL_CLIENT_ID  = AY...
# PAYPAL_CLIENT_SECRET = EH...
# PAYPAL_MODE = live
# BASE_URL = https://your-app.up.railway.app
```

Railway free tier: $5/month credit (enough for ~500k requests)

---

## 3. Test Locally First

```bash
cd coldcraft
pip install -r requirements.txt

# Copy and fill .env.example → .env
cp .env.example .env

# Run
uvicorn main:app --reload
# Open http://localhost:8000
```
2
---

## 4. Go Live Checklist

- [ ] PAYPAL_MODE=live (real payments)
- [ ] BASE_URL set to your Railway URL
- [ ] Test with a real PayPal sandbox account first
- [ ] Custom domain (optional): Railway → Settings → Domain

---

## 5. Get First Customers

**Week 1 – Free traffic:**
- Post in r/freelance, r/webdev, r/forhire: "I built a free tool to personalize cold emails in 45 seconds"
- Post on Twitter/X with a screen recording demo
- Share in Indie Hackers
- ProductHunt launch (do on a Tuesday)

**Pricing reminder:**
- Free: 5 emails
- Pro: $19/month via PayPal (300 emails)

**Break-even:** 1 paying customer = $19/mo → covers Railway + API costs with profit

---

## Revenue Projections

| Customers | MRR |
|-----------|-----|
| 10        | $190 |
| 50        | $950 |
| 100       | $1,900 |
| 300       | $5,700 |

API cost per customer: ~$0.75/month (300 emails × $0.0025)
Net margin at scale: ~96%
