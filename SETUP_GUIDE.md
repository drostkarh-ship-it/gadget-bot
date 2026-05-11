# 🤖 راهنمای کامل راه‌اندازی ربات گجت ترند

## چیزی که این ربات انجام میده:
- هر روز ساعت ۹ صبح گجت‌های ترند TikTok و Instagram رو پیدا میکنه
- قیمت‌ها رو در Amazon، Alibaba، 1688، Temu مقایسه میکنه
- گزارش کامل رو به تلگرامت میفرسته

---

## قدم ۱: آپلود فایل‌ها به GitHub

1. برو به **github.com** و Sign Up کن (رایگانه)
2. یه Repository جدید بساز → اسمش بذار `gadget-bot`
3. این ۳ فایل رو آپلود کن:
   - `main.py`
   - `requirements.txt`
   - `render.yaml`

---

## قدم ۲: راه‌اندازی روی Render.com

1. برو به **render.com** و Sign Up کن (با GitHub اکانتت)
2. روی **"New +"** کلیک کن
3. **"Background Worker"** رو انتخاب کن
4. Repository ات رو وصل کن
5. این تنظیمات رو بده:
   - **Name:** gadget-trend-bot
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python main.py`
6. روی **"Create Background Worker"** کلیک کن

---

## قدم ۳: تست

بعد از Deploy، ربات فوری یه گزارش میفرسته به تلگرامت!
بعدش هر روز ساعت ۹ صبح به طور خودکار گزارش میده.

---

## نکات مهم:
- پلن رایگان Render.com کافیه
- اگه ربات بعد از ۱۵ دقیقه بیکار موند، ممکنه sleep کنه - نگران نباش
- لاگ‌ها رو در Render.com داشبورد میتونی ببینی
