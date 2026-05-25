"""
Stripe Subscription Paywall Demo
- User gets 1 free question
- After that, paywall triggers
- $19.95/month subscription via Stripe Checkout
- Webhook confirms payment and unlocks access

This is the pattern the RV chatbot job (and every SaaS chatbot listing) needs.
"""

import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import stripe

# Use test key — no real charges
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "sk_test_YOUR_KEY_HERE")

# In production this would be a database. For demo, in-memory.
users = {}

# Create a Stripe product and price on first run
PRICE_ID = None


def ensure_product_exists():
    """Create the subscription product if it doesn't exist."""
    global PRICE_ID
    if PRICE_ID:
        return PRICE_ID

    # Check if product already exists
    products = stripe.Product.list(limit=1, active=True)
    for p in products.data:
        if p.name == "RV Expert AI - Unlimited Access":
            prices = stripe.Price.list(product=p.id, active=True, limit=1)
            if prices.data:
                PRICE_ID = prices.data[0].id
                return PRICE_ID

    # Create product and price
    product = stripe.Product.create(
        name="RV Expert AI - Unlimited Access",
        description="Unlimited AI-powered RV repair, maintenance, and buying advice. Cancel anytime.",
    )
    price = stripe.Price.create(
        product=product.id,
        unit_amount=1995,  # $19.95
        currency="usd",
        recurring={"interval": "month"},
    )
    PRICE_ID = price.id
    return PRICE_ID


class PaywallHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/":
            self.send_html(CHAT_PAGE)

        elif path == "/subscribe":
            # Create Stripe Checkout session
            price_id = ensure_product_exists()
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{"price": price_id, "quantity": 1}],
                mode="subscription",
                success_url="http://localhost:8080/success?session_id={CHECKOUT_SESSION_ID}",
                cancel_url="http://localhost:8080/",
            )
            self.send_response(303)
            self.send_header("Location", session.url)
            self.end_headers()

        elif path == "/success":
            self.send_html(SUCCESS_PAGE)

        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        path = urlparse(self.path).path
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode()

        if path == "/ask":
            data = json.loads(body)
            user_id = data.get("user_id", "anonymous")
            question = data.get("question", "")

            # Track free questions
            if user_id not in users:
                users[user_id] = {"questions": 0, "subscribed": False}

            user = users[user_id]

            if user["subscribed"]:
                # Unlimited access
                response = {"answer": f"[AI Response to: {question}] — In production, this calls Claude/OpenAI API.", "status": "subscribed"}
            elif user["questions"] < 1:
                # Free question
                user["questions"] += 1
                response = {"answer": f"[AI Response to: {question}] — In production, this calls Claude/OpenAI API.", "status": "free", "remaining": 0}
            else:
                # Paywall
                response = {"answer": None, "status": "paywall", "message": "Subscribe for unlimited access — $19.95/month, cancel anytime."}

            self.send_json(response)

        elif path == "/webhook":
            # Stripe webhook — confirms subscription
            event = json.loads(body)
            if event["type"] == "checkout.session.completed":
                # In production, match to user via customer email or metadata
                print(f"New subscription! Session: {event['data']['object']['id']}")

            self.send_json({"received": True})

    def send_html(self, html):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def send_json(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {args[0]}")


CHAT_PAGE = """<!DOCTYPE html>
<html>
<head>
    <title>RV Expert AI</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, sans-serif; background: #0f172a; color: #e2e8f0; min-height: 100vh; display: flex; flex-direction: column; align-items: center; padding: 2rem; }
        .container { max-width: 600px; width: 100%; }
        h1 { font-size: 1.8rem; margin-bottom: 0.5rem; color: #38bdf8; }
        .subtitle { color: #94a3b8; margin-bottom: 2rem; }
        .chat-box { background: #1e293b; border-radius: 12px; padding: 1.5rem; min-height: 300px; margin-bottom: 1rem; }
        .message { padding: 0.75rem 1rem; border-radius: 8px; margin-bottom: 0.75rem; max-width: 85%; }
        .user-msg { background: #334155; margin-left: auto; text-align: right; }
        .bot-msg { background: #0f4c81; }
        .input-row { display: flex; gap: 0.5rem; }
        input { flex: 1; padding: 0.75rem 1rem; border-radius: 8px; border: 1px solid #334155; background: #1e293b; color: #e2e8f0; font-size: 1rem; }
        button { padding: 0.75rem 1.5rem; border-radius: 8px; border: none; background: #38bdf8; color: #0f172a; font-weight: 600; cursor: pointer; font-size: 1rem; }
        button:hover { background: #7dd3fc; }
        .paywall { background: #1e293b; border: 2px solid #38bdf8; border-radius: 12px; padding: 2rem; text-align: center; margin-top: 1rem; }
        .paywall h2 { color: #38bdf8; margin-bottom: 1rem; }
        .paywall .price { font-size: 2rem; font-weight: 700; color: #f8fafc; }
        .paywall .period { color: #94a3b8; }
        .paywall a { display: inline-block; margin-top: 1rem; padding: 0.75rem 2rem; background: #38bdf8; color: #0f172a; text-decoration: none; border-radius: 8px; font-weight: 600; }
        .free-badge { background: #065f46; color: #6ee7b7; padding: 0.25rem 0.75rem; border-radius: 999px; font-size: 0.8rem; display: inline-block; margin-bottom: 1rem; }
        #messages { display: flex; flex-direction: column; }
    </style>
</head>
<body>
    <div class="container">
        <h1>RV Expert AI</h1>
        <p class="subtitle">Ask anything about RV repair, maintenance, and buying advice.</p>
        <span class="free-badge" id="badge">1 free question</span>
        <div class="chat-box" id="chatbox">
            <div id="messages">
                <div class="message bot-msg">Hi! I'm your RV expert. Ask me anything about repairs, maintenance, buying tips, or troubleshooting. Your first question is free!</div>
            </div>
        </div>
        <div class="input-row">
            <input type="text" id="input" placeholder="Ask about your RV..." onkeypress="if(event.key==='Enter')ask()">
            <button onclick="ask()">Ask</button>
        </div>
        <div class="paywall" id="paywall" style="display:none">
            <h2>Unlock Unlimited RV Advice</h2>
            <div class="price">$19.95<span class="period">/month</span></div>
            <p style="color:#94a3b8;margin-top:0.5rem">Unlimited questions. Cancel anytime.</p>
            <a href="/subscribe">Subscribe Now</a>
        </div>
    </div>
    <script>
        const userId = 'user_' + Math.random().toString(36).substr(2, 9);
        async function ask() {
            const input = document.getElementById('input');
            const q = input.value.trim();
            if (!q) return;
            input.value = '';
            addMsg(q, 'user-msg');
            const res = await fetch('/ask', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({user_id: userId, question: q})
            });
            const data = await res.json();
            if (data.status === 'paywall') {
                document.getElementById('paywall').style.display = 'block';
                document.getElementById('badge').textContent = 'Free question used';
                document.getElementById('badge').style.background = '#7f1d1d';
                document.getElementById('badge').style.color = '#fca5a5';
                addMsg('To continue getting expert RV advice, subscribe for unlimited access below.', 'bot-msg');
            } else {
                addMsg(data.answer, 'bot-msg');
                if (data.status === 'free') {
                    document.getElementById('badge').textContent = '0 free questions left';
                    document.getElementById('badge').style.background = '#78350f';
                    document.getElementById('badge').style.color = '#fcd34d';
                }
            }
        }
        function addMsg(text, cls) {
            const div = document.createElement('div');
            div.className = 'message ' + cls;
            div.textContent = text;
            document.getElementById('messages').appendChild(div);
            document.getElementById('chatbox').scrollTop = 99999;
        }
    </script>
</body>
</html>""" 

SUCCESS_PAGE = """<!DOCTYPE html>
<html>
<head><title>Subscribed!</title>
<style>
    body { font-family: -apple-system, sans-serif; background: #0f172a; color: #e2e8f0; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
    .box { text-align: center; }
    h1 { color: #38bdf8; }
    a { color: #38bdf8; }
</style>
</head>
<body><div class="box">
    <h1>You're subscribed!</h1>
    <p>Unlimited RV expert advice is now unlocked.</p>
    <p><a href="/">Back to chat</a></p>
</div></body>
</html>"""


if __name__ == "__main__":
    ensure_product_exists()
    print("RV Expert AI running at http://localhost:8080")
    print("Test card: 4242 4242 4242 4242 (any future date, any CVC)")
    HTTPServer(("", 8080), PaywallHandler).serve_forever()
