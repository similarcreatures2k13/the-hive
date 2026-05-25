```text
████████╗██╗  ██╗███████╗    ██╗  ██╗██╗██╗   ██╗███████╗
╚══╝██╔══╝██║  ██║██╔════╝    ██║  ██║██║██║   ██║██╔════╝
    ██║   ███████║█████╗      ███████║██║██║   ██║█████╗  
    ██║   ██╔══██║██╔══╝      ██╔══██║██║╚██╗ ██╔╝██╔══╝  
    ██║   ██║  ██║███████╗    ██║  ██║██║ ╚████╔╝ ███████╗
    ╚═╝   ╚═╝  ╚═╝╚══════╝    ╚═╝  ╚═╝╚═╝  ╚═══╝  ╚══════╝
              [ MULTI-AGENT DEPLOYMENT SYSTEM v1.0 ]
```

> *"Every business has dead hours. Every dead hour is a lost customer. The Hive doesn't sleep."*

---

## SYSTEM OVERVIEW

The Hive is a multi-industry AI agent arsenal built for real businesses. Not a demo. Not a chatbot template. Working agents that qualify leads, book appointments on real calendars, handle payments, and speak your customer's language.

Two frameworks. Every messaging platform. Deploy in 30 minutes.

```text
   THE HIVE
   ├── skills/
   │   ├── restaurant-agent ────── Bookings, menu, upselling
   │   ├── real-estate-agent ───── Lead qualification, multilingual
   │   └── restaurant-agent-openclaw ── Cross-platform proof
   ├── tools/
   │   ├── calendar_tool.py ────── Google Calendar integration
   │   └── paywall/app.py ─────── Stripe subscription billing
   └── references/
       └── universe.json ──────── Sector intelligence (coming)
```

---

## AGENT ROSTER

### `SKILL:restaurant-agent`
*Framework: Hermes Agent*

Front-of-house AI that handles the entire reservation flow. Asks for party size, date, time, name, phone — then books it directly on Google Calendar. No human touches the booking.

- Reservation management with real calendar events
- Menu and dietary inquiries (halal, vegan, gluten-free)
- Natural upselling (sharing platters for groups, weekend specials)
- Complaint escalation to human manager
- 24/7 on WhatsApp + Telegram

```text
CUSTOMER: Hi, table for 4 Saturday at 7pm
AGENT:    Perfect. Name and phone number?
CUSTOMER: Johnson, 050-123-4567
AGENT:    Booked. Saturday 7pm, party of 4.
          Our sharing platters are great for groups — ask your server.
          [✓ Calendar event created]
```

### `SKILL:real-estate-agent`
*Framework: Hermes Agent*

Lead qualification engine that speaks English, Arabic, and French. Captures budget, timeline, area preference, and pre-approval status. Scores every lead as hot, warm, or cold.

- Buyer and seller qualification
- Multi-language (EN / AR / FR)
- Viewing bookings with calendar integration
- Automatic lead scoring
- Property matching against active listings

```text
CUSTOMER: مرحبا، أبحث عن شقة غرفتين نوم بميزانية 250 ألف
AGENT:    مرحبا! ما المنطقة المفضلة؟ وما الجدول الزمني للانتقال؟
          هل لديك موافقة مبدئية على التمويل؟
```

### `SKILL:restaurant-agent-openclaw`
*Framework: OpenClaw*

Same skill, different framework. Proves cross-platform deployment — one skill definition works on both Hermes and OpenClaw without rewriting.

---

## TOOLS

### `calendar_tool.py`
Direct Google Calendar API integration. No MCP middleware, no timeouts. Creates, lists, and deletes calendar events from the command line or agent skill.

```bash
python3 tools/calendar_tool.py create "Reservation - Smith, party of 4" "2026-06-01T19:00:00" 120
```

### `paywall/app.py`
Stripe subscription paywall for freemium AI chatbots. One free question, then $19.95/month unlimited access. Full Checkout + webhook flow.

```bash
STRIPE_SECRET_KEY=sk_test_xxx python3 tools/paywall/app.py
# → http://localhost:8080
# Test card: 4242 4242 4242 4242
```

```text
FREE QUESTION ──→ AI RESPONDS ──→ PAYWALL ──→ STRIPE CHECKOUT ──→ UNLIMITED
```

---

## DEPLOYMENT

```bash
# Install Hermes Agent
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash

# Copy skills into Hermes
cp -r skills/restaurant-agent ~/.hermes/skills/
cp -r skills/real-estate-agent ~/.hermes/skills/

# Install OpenClaw
npm install -g openclaw@latest

# Copy OpenClaw skill
openclaw skills install skills/restaurant-agent-openclaw/

# Set up Google Calendar
pip3 install google-api-python-client google-auth-oauthlib
python3 tools/calendar_tool.py list-calendars

# Launch
hermes chat
```

---

## STACK

```text
FRAMEWORKS    Hermes Agent · OpenClaw
INTELLIGENCE  Claude Sonnet 4 (Anthropic)
MESSAGING     WhatsApp · Telegram
CALENDAR      Google Calendar API (direct)
PAYMENTS      Stripe Checkout + Subscriptions
LANGUAGES     English · Arabic · French
```

---

## ROADMAP

- [ ] Voice agent integration (VAPI)
- [ ] CRM auto-sync (HubSpot, Airtable)
- [ ] Self-evolving skills via DSPy + GEPA
- [ ] Sector intelligence engine
- [ ] Band multi-agent orchestration

---

*Built by [@similarcreatures2k13](https://github.com/similarcreatures2k13) · Powered by terminal, coffee, and refusing to sleep.*
