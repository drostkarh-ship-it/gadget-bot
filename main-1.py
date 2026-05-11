import requests
from bs4 import BeautifulSoup
import time
import schedule
import json
import re
from datetime import datetime

# ===== تنظیمات =====
TELEGRAM_TOKEN = "8696520314:AAFjtIJFJuiEeF0jwovCzJz5XZFLsQs10fo"
CHAT_ID = "113256700"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

# ===== ارسال پیام تلگرام =====
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        r = requests.post(url, data=data, timeout=10)
        print(f"Telegram: {r.status_code}")
    except Exception as e:
        print(f"Telegram error: {e}")

# ===== جستجوی ترند از گوگل (TikTok + Instagram) =====
def get_trending_gadgets():
    print("🔍 جستجوی گجت‌های ترند...")
    trending = []
    
    queries = [
        "tiktok viral gadgets 2026 trending products",
        "instagram reels trending tech gadgets 2026",
        "most viral products tiktok shop 2026"
    ]
    
    for query in queries:
        try:
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}&num=10"
            r = requests.get(url, headers=HEADERS, timeout=15)
            soup = BeautifulSoup(r.text, "html.parser")
            
            # استخراج عنوان‌های نتایج
            for result in soup.select("h3")[:5]:
                title = result.get_text(strip=True)
                if title and len(title) > 10:
                    trending.append(title)
            
            time.sleep(2)
        except Exception as e:
            print(f"Search error: {e}")
    
    # استخراج اسم گجت‌ها از عنوان‌ها
    gadgets = extract_gadget_names(trending)
    return gadgets[:5]  # فقط ۵ تا

# ===== استخراج اسم گجت از متن =====
def extract_gadget_names(titles):
    gadget_keywords = [
        "LED", "projector", "speaker", "earbuds", "headphone",
        "watch", "camera", "drone", "ring light", "keyboard",
        "mouse", "charger", "powerbank", "lamp", "humidifier",
        "massager", "tracker", "band", "glasses", "mini"
    ]
    
    found = []
    for title in titles:
        for kw in gadget_keywords:
            if kw.lower() in title.lower():
                # استخراج عبارت اطراف کلمه کلیدی
                words = title.split()
                for i, word in enumerate(words):
                    if kw.lower() in word.lower():
                        start = max(0, i-2)
                        end = min(len(words), i+3)
                        gadget_name = " ".join(words[start:end])
                        if gadget_name not in found:
                            found.append(gadget_name)
                        break
    
    # اگه چیزی پیدا نشد، از لیست پیش‌فرض استفاده کن
    if not found:
        found = [
            "Mini Projector",
            "LED Ring Light",
            "Bluetooth Earbuds",
            "Portable Massager",
            "Smart LED Lamp"
        ]
    
    return found[:5]

# ===== جستجوی قیمت در آمازون =====
def search_amazon(product):
    try:
        query = product.replace(" ", "+")
        url = f"https://www.amazon.com/s?k={query}"
        r = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        
        results = []
        items = soup.select("[data-component-type='s-search-result']")[:3]
        
        for item in items:
            name_el = item.select_one("h2 span")
            price_el = item.select_one(".a-price-whole")
            rating_el = item.select_one(".a-icon-alt")
            sales_el = item.select_one(".a-size-base.s-underline-text")
            
            if name_el and price_el:
                results.append({
                    "name": name_el.get_text(strip=True)[:60],
                    "price": f"${price_el.get_text(strip=True)}",
                    "rating": rating_el.get_text(strip=True)[:10] if rating_el else "N/A",
                    "sales": sales_el.get_text(strip=True) if sales_el else "N/A"
                })
        
        return results
    except Exception as e:
        print(f"Amazon error: {e}")
        return []

# ===== جستجوی قیمت در Alibaba =====
def search_alibaba(product):
    try:
        query = product.replace(" ", "+")
        url = f"https://www.alibaba.com/trade/search?SearchText={query}"
        r = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        
        results = []
        items = soup.select(".organic-gallery-offer-outter")[:3]
        
        for item in items:
            name_el = item.select_one(".elements-title-normal__content")
            price_el = item.select_one(".elements-offer-price-normal__price")
            
            if name_el and price_el:
                results.append({
                    "name": name_el.get_text(strip=True)[:60],
                    "price": price_el.get_text(strip=True),
                    "sales": "N/A"
                })
        
        return results
    except Exception as e:
        print(f"Alibaba error: {e}")
        return []

# ===== جستجوی قیمت در 1688 =====
def search_1688(product):
    try:
        query = requests.utils.quote(product)
        url = f"https://s.1688.com/selloffer/offer_search.htm?keywords={query}"
        r = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        
        results = []
        items = soup.select(".offer-item")[:3]
        
        for item in items:
            name_el = item.select_one(".offer-title")
            price_el = item.select_one(".price")
            
            if name_el and price_el:
                results.append({
                    "name": name_el.get_text(strip=True)[:60],
                    "price": f"¥{price_el.get_text(strip=True)}",
                    "sales": "N/A"
                })
        
        return results
    except Exception as e:
        print(f"1688 error: {e}")
        return []

# ===== جستجوی قیمت در Temu =====
def search_temu(product):
    try:
        query = product.replace(" ", "+")
        url = f"https://www.temu.com/search_result.html?search_key={query}"
        r = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        
        results = []
        items = soup.select("._2Csua4")[:3]
        
        for item in items:
            name_el = item.select_one("._3T6Odo")
            price_el = item.select_one("._2HRlMi")
            
            if name_el and price_el:
                results.append({
                    "name": name_el.get_text(strip=True)[:60],
                    "price": price_el.get_text(strip=True),
                    "sales": "N/A"
                })
        
        return results
    except Exception as e:
        print(f"Temu error: {e}")
        return []

# ===== ساخت گزارش =====
def build_report(gadget, amazon, alibaba, alibaba_1688, temu):
    msg = f"🔥 <b>{gadget}</b>\n"
    msg += "─" * 30 + "\n\n"
    
    # آمازون
    msg += "🛒 <b>Amazon:</b>\n"
    if amazon:
        for i in amazon[:2]:
            msg += f"  • {i['price']} | ⭐ {i['rating']}\n"
            if i['sales'] != 'N/A':
                msg += f"    فروش: {i['sales']}\n"
    else:
        msg += "  ❌ یافت نشد\n"
    
    # علی‌بابا
    msg += "\n🏭 <b>Alibaba:</b>\n"
    if alibaba:
        for i in alibaba[:2]:
            msg += f"  • {i['price']}\n"
    else:
        msg += "  ❌ یافت نشد\n"
    
    # ۱۶۸۸
    msg += "\n🇨🇳 <b>1688:</b>\n"
    if alibaba_1688:
        for i in alibaba_1688[:2]:
            msg += f"  • {i['price']}\n"
    else:
        msg += "  ❌ یافت نشد\n"
    
    # Temu
    msg += "\n🛍️ <b>Temu:</b>\n"
    if temu:
        for i in temu[:2]:
            msg += f"  • {i['price']}\n"
    else:
        msg += "  ❌ یافت نشد\n"
    
    # توصیه خرید
    msg += "\n💡 <b>توصیه:</b> "
    if alibaba_1688:
        msg += "1688 ارزان‌ترین قیمت عمده رو داره\n"
    elif alibaba:
        msg += "Alibaba برای خرید عمده بهتره\n"
    elif temu:
        msg += "Temu برای خرید تکی مناسبه\n"
    else:
        msg += "Amazon برای خرید سریع بهتره\n"
    
    return msg

# ===== اجرای اصلی =====
def run_daily_report():
    print(f"\n{'='*40}")
    print(f"⏰ شروع گزارش: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print('='*40)
    
    # پیام شروع
    send_telegram(f"🚀 <b>گزارش روزانه گجت‌های ترند</b>\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}\nدر حال جستجو...")
    
    time.sleep(2)
    
    # پیدا کردن گجت‌های ترند
    gadgets = get_trending_gadgets()
    
    send_telegram(f"✅ <b>گجت‌های ترند امروز:</b>\n" + "\n".join([f"• {g}" for g in gadgets]))
    
    time.sleep(3)
    
    # بررسی هر گجت
    for gadget in gadgets:
        print(f"\n🔍 بررسی: {gadget}")
        
        amazon = search_amazon(gadget)
        time.sleep(2)
        
        alibaba = search_alibaba(gadget)
        time.sleep(2)
        
        a1688 = search_1688(gadget)
        time.sleep(2)
        
        temu = search_temu(gadget)
        time.sleep(2)
        
        report = build_report(gadget, amazon, alibaba, a1688, temu)
        send_telegram(report)
        
        time.sleep(3)
    
    send_telegram("✅ <b>گزارش امروز تموم شد!</b>\nفردا ساعت ۹ صبح گزارش بعدی ارسال میشه 🕘")
    print("\n✅ گزارش ارسال شد!")

# ===== زمان‌بندی =====
if __name__ == "__main__":
    print("🤖 ربات گجت ترند شروع به کار کرد!")
    print("⏰ هر ۱ ساعت یک بار گزارش ارسال میشه")
    
    # اجرای فوری برای تست
    run_daily_report()
    
    # زمان‌بندی هر ۱ ساعت
    schedule.every(1).hours.do(run_daily_report)
    
    while True:
        schedule.run_pending()
        time.sleep(60)
