# ARIA – Adaptive Retail Intelligence Assistant

**AI-driven omnichannel stylist and sales assistant for ABFRL, built for EY Techathon.**

ARIA unifies conversations across **web chat**, **WhatsApp**, and future in-store touchpoints into a single, context-aware journey. It behaves like a professional ABFRL stylist: asking for occasion and budget, recommending complete outfits, and respecting realistic pricing and discount rules – all backed by an agentic AI architecture.

---

## 🔴 Live Demo Links


- **Web Chat (Next.js + Vercel):**  
  `https://aria-chat-eta.vercel.app/`
- **Analytics Dashboard (Next.js + Vercel):**  
  `https://aria-chat-eta.vercel.app/dashboard`
- **Backend API (FastAPI + Render):**  
  `https://aria-api-1o1d.onrender.com/`  
  Docs: `https://aria-api-1o1d.onrender.com/docs`
- **WhatsApp Bot (Twilio Sandbox):**  
  - Number: `+1 415 523 8886`  
  - Send the join code from Twilio sandbox, then message: `Hi ARIA`

---

## 🧩 Problem

Modern fashion customers in India don’t shop on a single channel:

- They browse ABFRL products on apps/web,
- Ask sizing/availability questions on WhatsApp,
- Finally buy in-store or in another channel.

But every channel treats them as **new**:

- Users repeat their size, budget, occasion and preferences
- Context is lost when moving from web → WhatsApp → store
- Existing chatbots handle FAQs, not real **consultative selling**

For ABFRL this means:

- High channel drop-off
- Missed upsell/cross-sell
- No centralized view of how AI impacts sales

---

## 💡 Solution – ARIA

ARIA is a **central AI “brain”** that powers:

- A **web chat experience** (Vercel)
- A **WhatsApp bot** (Twilio Sandbox)
- An **analytics dashboard** for business stakeholders

All channels talk to the **same backend** and **same AI orchestration layer**, so:

- Context (session, cart, style DNA) is preserved in Redis
- Business logic around discounts & gifting is enforced centrally
- New channels (store kiosks, staff app) are just new frontends; the brain is reused

### Key Capabilities

- **Consultative conversation**:  
  ARIA asks for occasion, budget, fit, and style before recommending.
- **Complete outfit suggestions**:  
  Shirts + trousers/jeans + shoes + accessory as product cards.
- **Realistic Indian pricing & discounts**:  
  Prompt-tuned so it never invents crazy offers – max 30% total discount, no “Super VIP 35%” nonsense.
- **Session continuity**:  
  Web and WhatsApp share the same session key for a user – channel switches are tracked in Redis.
- **Analytics dashboard**:  
  Track active users, conversation count, conversion rate, AOV, revenue uplift, channel mix, and agent status.

---

## 🏗️ Architecture Overview

```text
Channels
  - Web Chat (Next.js, Vercel)
  - WhatsApp (Twilio Sandbox)
  - (Future) Store Kiosk / Staff App
        │
        ▼
Backend API (FastAPI on Render)
  - /api/v1/chat/message       (web/app chat)
  - /api/v1/whatsapp/webhook   (WhatsApp inbound)
  - /api/v1/analytics/dashboard
        │
        ▼
Agentic AI Layer (ARIA Brain)
  - Master Sales Agent (intent, context, guardrails)
  - Worker Agents (conceptual):
      - Recommendation Agent
      - Inventory Agent (stubbed)
      - Payment Agent (stubbed)
      - Fulfilment Agent (stubbed)
      - Loyalty & Offers Agent
      - Post-Purchase Support Agent
        │
        ▼
Data & State
  - Redis (Upstash)         → sessions, carts, channel history
  - Neon PostgreSQL         → product catalog, structured data
  - MongoDB Atlas           → conversation logs, analytics events
  - Groq LLM (llama-3.1-8b-instant) → main language model
```

🤖 Agentic Design
Master Sales Agent

Class: ARIABrain in backend/src/services/aria_brain.py
Responsibilities:
Load session & history from Redis
Append rich system prompt with:
Role & tone
Pricing/discount guardrails
Behavior & safety rules
Call Groq LLM with user message + history
Save response back to session and MongoDB (if connected)
Behavior Guardrails (examples):

Max 30% discount in total
No infinite discount bargaining (after 2 “discount” attempts, it holds the line)
Disallows unrealistic free gifts (no jackets/shoes for free)
Soft, human-sounding refusals instead of “cannot comply with that request”
Handles flirting / emotional manipulation politely but firmly
Worker agents (Recommendation, Inventory, etc.) are modeled in code and design to be pluggable; current prototype focuses on Recommendation + Context + Pricing behavior to prove the agentic pattern.

🧪 Features
✅ Web chat SPA built with Next.js 14 + Tailwind

Typing indicator
Quick reply chips (“Formal wear”, “Trending”, “Style DNA”)
Product cards with image, brand, name, price, CTA
Session info bar (channel, Style DNA flag, etc.)
✅ WhatsApp integration via Twilio Sandbox

Same LLM & brain as web chat
Full request/response flow verified in logs
✅ Analytics dashboard (/dashboard)

Active users
Conversations today
Conversion rate (%)
Average Order Value (₹)
Revenue today (₹)
Satisfaction score (/5)
Channel mix (WhatsApp, Web, Mobile, Kiosk)
Agent mesh status (“active” / “degraded”)
✅ Zero-cost cloud setup

Render (backend), Vercel (frontend), Groq (LLM), Neon PG, MongoDB Atlas, Upstash, Twilio sandbox
🛠️ Tech Stack
Backend & Orchestration

Python 3.11
FastAPI
Redis (Upstash)
Neon PostgreSQL
MongoDB Atlas (motor)
Groq Python SDK (LLM)
AI & Prompting

Groq LLM: llama-3.1-8b-instant
Carefully designed SYSTEM_PROMPT with:
Brand positioning
Pricing & discount constraints
Behavioral rules (flirting, abuse, bargaining)
Conversational style guidelines
Frontend

Next.js 14 (App Router)
TypeScript
Tailwind CSS
Deployed to Vercel
Messaging

Twilio WhatsApp Sandbox → FastAPI webhook
Infra & DevOps

Render.com Web Service for API
Vercel for frontend
Sentry (optional) for error tracking
GitHub for version control
🚀 Running Locally
Prerequisites
Python 3.11
Node.js 18+
A Groq API key
Twilio sandbox credentials (optional, for local WhatsApp testing)
Backend
Bash

cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
# source venv/bin/activate

pip install -r requirements.txt

# create .env based on .env.example and fill secrets
python -m uvicorn src.main:app --reload --port 8000
The backend will be available at http://localhost:8000
Docs at: http://localhost:8000/docs

Frontend (web chat + dashboard)
Bash

cd web-chat
npm install
# create .env.local with:
# NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
Open:

Chat: http://localhost:3000/
Dashboard: http://localhost:3000/dashboard
📈 Limitations & Future Work
Inventory, payment, and fulfilment agents are conceptually modeled but not fully integrated with real ABFRL systems yet.
Style DNA via selfie color analysis is designed and partially implemented in backend, but UI integration can be deepened.
WhatsApp is currently through Twilio sandbox, not a production WhatsApp Business number.
Analytics are partially based on simulated data for the demo; in production this would be backed by event streams.
Future extensions:

Plug in real ABFRL product/inventory APIs
Build store staff tablet UI that uses same backend
Full Style DNA flow with image upload + color analysis model
Use real sales data to train recommendation agent
🧑‍💻 Author
Aryan Ranjan
B.Tech CSE (E‑Commerce Technologies), VIT Bhopal University

Architect & full-stack developer of ARIA
Built for EY Techathon (ABFRL Retail Problem)
