import requests
from bs4 import BeautifulSoup
import time
import os
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# 🔥 Fake web server (required for Render free)
def run_server():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'Bot is running')

    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), Handler)
    server.serve_forever()

threading.Thread(target=run_server).start()

# 🔐 Telegram config
BOT_TOKEN = os.getenv("8791908596:AAF-uJ0gYGDqF4Mt6GgwYpOVC4ypXoABXxM")
CHAT_ID = os.getenv("884402268")

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# 🔎 Categories
URLS = [
    "https://www.flipkart.com/search?q=mobiles",
    "https://www.flipkart.com/search?q=laptops",
    "https://www.flipkart.com/search?q=headphones"
]

SEEN_FILE = "seen.json"

# Load seen products
try:
    with open(SEEN_FILE, "r") as f:
        seen = set(json.load(f))
except:
    seen = set()

def save_seen():
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)

def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.get(url, params={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

def fetch(url):
    try:
        return requests.get(url, headers=HEADERS, timeout=10).text
    except:
        return None

def parse(html):
    soup = BeautifulSoup(html, "html.parser")
    items = soup.select("div._1AtVbE")

    deals = []

    for item in items:
        try:
            name = item.select_one("div._4rR01T") or item.select_one("a.s1Q9rs")
            price = item.select_one("div._30jeq3")
            mrp = item.select_one("div._3I9_wc")
            link_tag = item.select_one("a")

            if not (name and price and mrp and link_tag):
                continue

            link = link_tag.get("href")

            name = name.text.strip()
            price = int(price.text.replace("₹","").replace(",",""))
            mrp = int(mrp.text.replace("₹","").replace(",",""))

            discount = ((mrp - price) / mrp) * 100

            if discount >= 50:
                full_link = "https://www.flipkart.com" + link
                deals.append((name, price, mrp, discount, full_link))

        except:
            continue

    return deals

def check():
    global seen

    for url in URLS:
        html = fetch(url)
        if not html:
            continue

        deals = parse(html)

        for name, price, mrp, discount, link in deals:
            if link in seen:
                continue

            msg = f"""🔥 {discount:.0f}% OFF
{name}
💰 ₹{price} (MRP ₹{mrp})
🔗 {link}
"""
            send(msg)

            seen.add(link)
            save_seen()

            time.sleep(2)

while True:
    check()
    time.sleep(900)  # every 15 min            continue

    return deals

def check():
    global seen

    for url in URLS:
        html = fetch(url)
        if not html:
            continue

        deals = parse(html)

        for name, price, mrp, discount, link in deals:
            if link in seen:
                continue

            msg = f"""🔥 {discount:.0f}% OFF
{name}
💰 ₹{price} (MRP ₹{mrp})
🔗 {link}
"""
            send(msg)

            seen.add(link)
            save_seen()

            time.sleep(2)  # avoid spam

while True:
    check()
    time.sleep(900)  # every 15 minutes
