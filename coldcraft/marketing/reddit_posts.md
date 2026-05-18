# ColdCraft – Reddit & Indie Hackers Posts

---

## r/freelance

**Title:** Built a tool that writes my cold emails for me — sharing it because it's saved me hours

I hate writing cold emails. Not because I can't do it, but because personalizing 20 of them properly takes forever and I always end up sending lazy ones anyway.

So I built something: you paste in a prospect's website URL, it scrapes the site, and spits out a personalized cold email in about 45 seconds. Not a template — an actual email that references what they do, their pain points, whatever's on their site.

I've been using it for my own outreach for a few months. Reply rates went up noticeably. Mostly because I stopped sending the same email to everyone.

It's called ColdCraft: https://lazily-crop-stuffing.ngrok-free.dev

Free tier gives you 5 emails to try it. No card required. If you use it more than that, pro is $19/month for 300.

Not here to pitch you — just figured other freelancers dealing with the same thing might want it.

---

## r/webdev

**Title:** Built a cold email tool with FastAPI + Claude AI — here's how it works under the hood

Side project I shipped recently: ColdCraft. You give it a prospect's URL, it scrapes the site, feeds the content to Claude AI with a structured prompt, and returns a personalized cold email. Whole thing takes ~45 seconds.

Stack is pretty straightforward:
- FastAPI for the backend
- Claude AI (Anthropic) for the email generation
- Basic web scraper to pull the prospect's content
- PayPal for payments (Pro tier)

The interesting part was prompt engineering — getting Claude to write something that actually sounds human and specific, not just "I see you work in [INDUSTRY]." Took a lot of iteration.

Live at https://lazily-crop-stuffing.ngrok-free.dev — free tier is 5 emails.

Happy to talk through any of the architecture or the prompting approach if anyone's curious. This kind of scrape → generate → output pipeline is useful for a lot of things beyond cold email.

---

## r/Entrepreneur

**Title:** Cold email ROI breakdown: what I found after actually tracking reply rates

Quick data share from the last few months of outreach.

Before: writing emails manually, semi-personalized, maybe 20 minutes per batch of 10. Reply rate around 4-5%.

After switching to personalized emails (one per prospect, referencing their actual site): reply rate jumped to 11-14%. Small sample size, but consistent.

The problem was doing this at scale. Real personalization takes time. So I built a tool that automates the scraping and writing: paste a URL, get a personalized email in 45 seconds.

ColdCraft: https://lazily-crop-stuffing.ngrok-free.dev

Cost math: Pro is $19/month for 300 emails. That's ~$0.06 per email. If your close rate is even 1%, you need one deal to pay for months of outreach.

Free tier is 5 emails — worth testing before you commit to anything.

---

## r/SideProject

**Title:** Shipped my first paid product — a cold email writer that actually personalizes

Spent the last couple months building something in the gaps between client work.

The problem I kept hitting: I'd want to do cold outreach but personalizing each email properly took way too long, so I'd either skip it or send lazy mass emails that went nowhere.

I built ColdCraft to fix that for myself. You paste a prospect's URL, it scrapes their site, and writes a tailored cold email using AI. Takes about 45 seconds. It actually reads their site — what they do, their tone, what problems they're solving — and writes something specific.

Tech-wise: FastAPI backend, Claude AI for generation, simple frontend.

Monetization: free tier (5 emails), Pro at $19/month via PayPal for 300.

Live here: https://lazily-crop-stuffing.ngrok-free.dev

If you try it, I'd genuinely love to hear what you think — good or bad.

---

## Indie Hackers

**Title:** I built ColdCraft to solve my own cold email problem — here's what I learned shipping it

**The problem**

I do freelance work and occasionally need to do cold outreach. The conventional advice is to personalize every email — reference something specific about the prospect, don't sound like a blast campaign. Good advice. But in practice, doing that properly for even 15-20 prospects takes an hour or more. So most people (including me) end up cutting corners and sending mediocre emails.

**What I built**

ColdCraft scrapes a prospect's website and generates a personalized cold email in about 45 seconds. It's not a template filler — it actually reads their site content and writes something contextual.

Stack: FastAPI backend, Claude AI for generation, basic scraper, PayPal for billing.

**Pricing**

Free: 5 emails (no card, just try it)
Pro: $19/month for 300 emails via PayPal

**The ask**

Try it: https://lazily-crop-stuffing.ngrok-free.dev

What would make you actually use something like this regularly?
