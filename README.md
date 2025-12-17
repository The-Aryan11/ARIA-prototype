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
