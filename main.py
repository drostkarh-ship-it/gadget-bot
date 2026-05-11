import requests
from bs4 import BeautifulSoup
import time
import schedule
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

# ===== تنظیمات =====
TELEGRAM_TOKEN = "8696520314:AAFjtIJFJuiEeF0jwovCzJz5XZFLsQs10fo"
CHAT_ID = "113256700"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

# ===== وب سرور ساده (برای Render رایگان) =====
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Gadget Bot is running!")
    def log_message(self, format, *args):
        pass

def start_server():
    server = HTTPServer(("0.0.0.0", 10000), Handler)
    server.serve_forever()

# ===== ارسال پیام تلگرام =====
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        r = requests.post(url, data=data, timeout=10)
        print(f"Telegram: {r.status_code}")
    except Exception as e:
        print(f"Telegram error: {e}")

# ===== جستجوی ترند =====
def get_trending_gadgets():
    print("جستجوی گجت‌های ترند...")
    trending = []
    queries = [
        "tiktok viral gadgets 2026 trending products",
        "instagram reels trending tech gadgets 2026",
    ]
    for query in queries:
        try:
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}&num=10"
            r = requests.get(url, headers=HEADERS, timeout=15)
            soup = BeautifulSoup(r.text, "html.parser")
            for result in soup.select("h3")[:5]:
                title = result.get_text(strip=True)
                if title and len(title) > 10:
                    trending.append(title)
            time.sleep(2)
        except Exception as e:
            print(f"Search error: {e}")
    return extract_gadget_names(trending)[:5]

def extract_gadget_names(titles):
    keywords = ["LED","projector","speaker","earbuds","headphone","watch","camera","drone","ring light","keyboard","charger","powerbank","lamp","massager","tracker","glasses","mini"]
    found = []
    for title in titles:
        for kw in keywords:
            if kw.lower() in title.lower():
                words = title.split()
                for i, word in enumerate(words):
                    if kw.lower() in word.lower():
                        name = " ".join(words[max(0,i-2):min(len(words),i+3)])
                        if name not in found:
                            found.append(name)
                        break
    if not found:
        found = ["Mini Projector","LED Ring Light","Bluetooth Earbuds","Portable Massager","Smart LED Lamp"]
    return found[:5]

# ===== جستجوی قیمت =====
def search_amazon(product):
    try:
        r = requests.get(f"https://www.amazon.com/s?k={product.replace(' ', '+')}", headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        results = []
        for item in soup.select("[data-component-type='s-search-result']")[:2]:
            price_el = item.select_one(".a-price-whole")
            rating_el = item.select_one(".a-icon-alt")
            if price_el:
                results.append({"price": f"${price_el.get_text(strip=True)}", "rating": rating_el.get_text(strip=True)[:10] if rating_el else "N/A"})
        return results
    except:
        return []

def search_alibaba(product):
    try:
        r = requests.get(f"https://www.alibaba.com/trade/search?SearchText={product.replace(' ', '+')}", headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        results = []
        for item in soup.select(".organic-gallery-offer-outter")[:2]:
            price_el = item.select_one(".elements-offer-price-normal__price")
            if price_el:
                results.append({"price": price_el.get_text(strip=True)})
        return results
    except:
        return []

def search_1688(product):
    try:
        r = requests.get(f"https://s.1688.com/selloffer/offer_search.htm?keywords={requests.utils.quote(product)}", headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        results = []
        for item in soup.select(".offer-item")[:2]:
            price_el = item.select_one(".price")
            if price_el:
                results.append({"price": f"¥{price_el.get_text(strip=True)}"})
        return results
    except:
        return []

def search_temu(product):
    try:
        r = requests.get(f"https://www.temu.com/search_result.html?search_key={product.replace(' ', '+')}", headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        results = []
        for item in soup.select("._2Csua4")[:2]:
            price_el = item.select_one("._2HRlMi")
            if price_el:
                results.append({"price": price_el.get_text(strip=True)})
        return results
    except:
        return []

# ===== ساخت گزارش =====
def build_report(gadget, amazon, alibaba, a1688, temu):
    msg = f"🔥 <b>{gadget}</b>\n─────────────────\n\n"
    msg += "🛒 <b>Amazon:</b>\n"
    msg += "".join([f"  • {i['price']} ⭐{i['rating']}\n" for i in amazon]) if amazon else "  ❌ یافت نشد\n"
    msg += "\n🏭 <b>Alibaba:</b>\n"
    msg += "".join([f"  • {i['price']}\n" for i in alibaba]) if alibaba else "  ❌ یافت نشد\n"
    msg += "\n🇨🇳 <b>1688:</b>\n"
    msg += "".join([f"  • {i['price']}\n" for i in a1688]) if a1688 else "  ❌ یافت نشد\n"
    msg += "\n🛍️ <b>Temu:</b>\n"
    msg += "".join([f"  • {i['price']}\n" for i in temu]) if temu else "  ❌ یافت نشد\n"
    msg += "\n💡 <b>توصیه:</b> "
    if a1688: msg += "1688 ارزان‌ترین قیمت عمده رو داره\n"
    elif alibaba: msg += "Alibaba برای خرید عمده بهتره\n"
    elif temu: msg += "Temu برای خرید تکی مناسبه\n"
    else: msg += "Amazon برای خرید سریع بهتره\n"
    return msg

# ===== اجرای اصلی =====
def run_report():
    print(f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    send_telegram(f"🚀 <b>گزارش گجت‌های ترند</b>\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}\nدر حال جستجو...")
    time.sleep(2)
    gadgets = get_trending_gadgets()
    send_telegram("✅ <b>گجت‌های ترند:</b>\n" + "\n".join([f"• {g}" for g in gadgets]))
    time.sleep(3)
    for gadget in gadgets:
        amazon = search_amazon(gadget); time.sleep(2)
        alibaba = search_alibaba(gadget); time.sleep(2)
        a1688 = search_1688(gadget); time.sleep(2)
        temu = search_temu(gadget); time.sleep(2)
        send_telegram(build_report(gadget, amazon, alibaba, a1688, temu))
        time.sleep(3)
    send_telegram("✅ <b>گزارش تموم شد!</b>\nیک ساعت دیگه گزارش بعدی میاد 🕐")

if __name__ == "__main__":
    print("🤖 ربات شروع به کار کرد!")
    threading.Thread(target=start_server, daemon=True).start()
    run_report()
    schedule.every(1).hours.do(run_report)
    while True:
        schedule.run_pending()
        time.sleep(60)
