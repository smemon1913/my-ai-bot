import os
import json
import threading
import telebot
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler

BOT_TOKEN = "8813841284:AAHF8f-i-GyOGskOqFl8su0-vO8OWRAhraQ"
API_KEY = "AQ.Ab8RN6JBwkKG_7Vq412cXaShXvigI7ulVf5GpymPrub0WSNUQg"
URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"

CATALOG = [
    {
        "id": "TSHIRT_BLK",
        "name": "Velmont Elite Heavyweight Minimalist T-Shirt (Black)",
        "category": "tshirt",
        "color": "black",
        "price": 1050,
        "sizes": ["M", "L", "XL"],
        "stock": "In Stock",
        "image_url": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=800"
    },
    {
        "id": "TSHIRT_WHT",
        "name": "Velmont Elite Premium Drop-Shoulder Tee (White)",
        "category": "tshirt",
        "color": "white",
        "price": 1150,
        "sizes": ["M", "L", "XL", "XXL"],
        "stock": "In Stock",
        "image_url": "https://images.unsplash.com/photo-1581655353564-df123a1eb820?w=800"
    },
    {
        "id": "SHIRT_OXFORD_BLK",
        "name": "Signature Oxford Cotton Casual Shirt (Black)",
        "category": "shirt",
        "color": "black",
        "price": 1650,
        "sizes": ["M", "L", "XL"],
        "stock": "In Stock",
        "image_url": "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=800"
    },
    {
        "id": "SHIRT_LINEN_WHT",
        "name": "Relaxed Fit Linen Blend Shirt (White)",
        "category": "shirt",
        "color": "white",
        "price": 1550,
        "sizes": ["M", "L", "XL"],
        "stock": "In Stock",
        "image_url": "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=800"
    },
    {
        "id": "DENIM_RAW",
        "name": "Velmont Elite Raw Indigo Streetwear Denim",
        "category": "pant",
        "color": "deep blue / indigo",
        "price": 2150,
        "sizes": ["30", "32", "34", "36"],
        "stock": "In Stock",
        "image_url": "https://images.unsplash.com/photo-1542272604-787c3835535d?w=800"
    },
    {
        "id": "DENIM_BLK",
        "name": "Washed Aesthetic Straight Cut Denim (Faded Black)",
        "category": "pant",
        "color": "black",
        "price": 2250,
        "sizes": ["30", "32", "34", "36"],
        "stock": "In Stock",
        "image_url": "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=800"
    }
]

SYSTEM_INSTRUCTION = f"""
তুমি প্রিমিয়াম ক্লদিং ব্র্যান্ড "VELMONT ÉLITE"-এর অফিসিয়াল সেলস ও কাস্টমার সাপোর্ট কনসালট্যান্ট।

আমাদের প্রোডাক্ট ক্যাটালগ:
{json.dumps(CATALOG, ensure_ascii=False, indent=2)}

ব্যবসার পলিসি:
- ডেলিভারি চার্জ: ঢাকা সিটিতে ৬০ টাকা, ঢাকার বাইরে ১২০ টাকা।
- ডেলিভারি সময়: ঢাকায় ২৪-৪৮ ঘণ্টা, ঢাকার বাইরে ২-৩ দিন।
- রিটার্ন/এক্সচেঞ্জ: ডেলিভারিম্যানের সামনে চেক করা যাবে। সাইজ সমস্যা হলে ৪৮ ঘণ্টার মধ্যে এক্সচেঞ্জ সুবিধা রয়েছে।
- পেমেন্ট: ক্যাশ অন ডেলিভারি (COD) এবং বিকাশ।

কাস্টমার হ্যান্ডলিং নিয়মাবলী:
১. কাস্টমার সাধারণ হাই/হ্যালো বললে তাকে আন্তরিকভাবে শুভেচ্ছা জানাও এবং কীভাবে সহায়তা করতে পারো তা জানতে চাও। সাথে সাথে অর্ডার ডিটেইলস চাইবে না।
২. বাজেট বা পছন্দের রঙের কথা বললে (যেমন: "১৫০০ টাকার মধ্যে শার্ট দেখাও" বা "ব্ল্যাক কালারের টি শার্টের পিক দাও") ক্যাটালগ খুঁজে নির্দিষ্ট পণ্যের নাম, সাইজ ও দাম জানাবে।
৩. কাস্টমার ছবি দেখতে চাইলে টেক্সট উত্তরের ভেতর অবশ্যই ইমেজ ট্যাগটি যোগ করবে: `[SEND_IMAGE: প্রোডাক্টের_ID]`।
৪. ক্যাটালগে নেই এমন কিছু (যেমন জুতো) চাইলে বিনয়ের সাথে জানাবে যে জুতো কালেকশন শীঘ্রই আসবে।
৫. শুধুমাত্র কাস্টমার যখন স্পষ্ট বলবে "অর্ডার করব" বা "নিতে চাই", তখনই তার নাম, মোবাইল নম্বর, ডেলিভারি ঠিকানা ও সাইজ জানতে চাইবে।
৬. ভাষা মার্জিত ও সংক্ষেপ রাখবে।
"""

bot = telebot.TeleBot(BOT_TOKEN)
user_memory = {}

def call_gemini(chat_id, user_text):
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": API_KEY
    }
    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_INSTRUCTION}]},
        "contents": user_memory[chat_id]
    }

    try:
        response = requests.post(URL, headers=headers, json=payload, timeout=25)
        res = response.json()
        print(f"API Response: {res}")

        if "candidates" in res and res["candidates"]:
            return res["candidates"][0]["content"]["parts"][0]["text"]
        elif "error" in res:
            return f"API Error: {res['error'].get('message', 'Server error')}"
        return "দুঃখিত, কোনো উত্তর পাওয়া যায়নি।"
    except Exception as e:
        return f"Error: {str(e)}"

@bot.message_handler(commands=["start"])
def send_welcome(message):
    user_memory[message.chat.id] = []
    welcome_text = (
        "VELMONT ÉLITE-এ আপনাকে স্বাগতম! ✨\n\n"
        "আমাদের প্রিমিয়াম শার্ট, ডেনিম প্যান্ট ও টি-শার্টের কালেকশন দেখতে পারেন।\n"
        "যেকোনো কালার, সাইজ, প্রাইস বা ছবি দেখতে চাইলে আমাকে জানান।"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    user_text = message.text

    if chat_id not in user_memory:
        user_memory[chat_id] = []

    user_memory[chat_id].append({"role": "user", "parts": [{"text": user_text}]})

    reply = call_gemini(chat_id, user_text)
    user_memory[chat_id].append({"role": "model", "parts": [{"text": reply}]})

    # ছবি পাঠানো যাচাই
    if "[SEND_IMAGE:" in reply:
        clean_reply = reply
        for item in CATALOG:
            tag = f"[SEND_IMAGE: {item['id']}]"
            if tag in reply:
                clean_reply = clean_reply.replace(tag, "").strip()
                try:
                    caption = f"💎 {item['name']}\n💰 মূল্য: {item['price']} ৳\n📏 সাইজ: {', '.join(item['sizes'])}"
                    bot.send_photo(chat_id, item["image_url"], caption=caption)
                except Exception as img_err:
                    print(f"Image error: {img_err}")

        if clean_reply:
            bot.send_message(chat_id, clean_reply)
    else:
        bot.reply_to(message, reply)

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"VELMONT ELITE Agent is Live.")

def run_http_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

if __name__ == "__main__":
    threading.Thread(target=run_http_server, daemon=True).start()
    print("=== VELMONT ELITE Bot Live ===")
    bot.infinity_polling()
    
