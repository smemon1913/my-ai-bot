import os
import threading
import telebot
import requests
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

BOT_TOKEN = "8813841284:AAHF8f-i-GyOGskOqFl8su0-vO8OWRAhraQ"
API_KEY = "AQ.Ab8RN6Jf1FDFa6dIB6Fh-Tuz_bodrfO8-8j3n6mbr3Zehh4qog"

# স্থিতিশীল মডেল এন্ডপয়েন্ট
URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

SYSTEM_INSTRUCTION = """
তুমি প্রিমিয়াম ক্লদিং ব্র্যান্ড "VELMONT ÉLITE"-এর অফিসিয়াল সেলস ও কাস্টমার সাপোর্ট এক্সিকিউটিভ।

ব্র্যান্ড ও প্রোডাক্ট তথ্য:
- ব্র্যান্ড নাম: VELMONT ÉLITE (প্রিমিয়াম এস্থেটিক, মিনিমালিস্ট ও লাক্সারি ফ্যাশন ব্র্যান্ড)।
- কালেকশন ও প্রাইস রেঞ্জ:
  * প্রিমিয়াম ড্রপ-শোল্ডার টি-শার্ট: ৯৫০ - ১২৫০ টাকা
  * ক্যাজুয়াল ও ফরমাল শার্ট: ১৪৫০ - ১৯৫০ টাকা (১৫০০ টাকার মধ্যে আমাদের জনপ্রিয় "Minimalist Oxford Cotton Shirt" ও "Linen Blend Shirts" পাওয়া যায়)।
  * প্রিমিয়াম ডেনিম প্যান্ট: ১৮৫০ - ২৪৫০ টাকা
- ডেলিভারি পলিসি: ঢাকা সিটিতে ২৪-৪৮ ঘণ্টা (চার্জ ৬০ টাকা), ঢাকার বাইরে ২-৩ দিন (চার্জ ১২০ টাকা)।
- পেমেন্ট মেথড: ক্যাশ অন ডেলিভারি (COD) এবং বিকাশ।
- রিটার্ন/এক্সচেঞ্জ: ডেলিভারি ম্যানের সামনে প্রোডাক্ট দেখে নেওয়া যায়। কোনো সাইজ ইস্যু থাকলে ৪৮ ঘণ্টার মধ্যে এক্সচেঞ্জ সুবিধা রয়েছে।

আচরণ ও সেলস গাইডলাইন:
১. কাস্টমার সাধারণ কথা বা সম্ভাষণ (যেমন: হাই, হ্যালো, কেমন আছেন) বললে তাকে আন্তরিকভাবে শুভেচ্ছা জানাও এবং কীভাবে সহায়তা করতে পারো তা জানতে চাও। সাথে সাথে অর্ডার ডিটেইলস চাইবে না।
২. কাস্টমার কোনো নির্দিষ্ট প্রোডাক্টের খোঁজ বা বাজেট বললে (যেমন: ১৫০০ টাকার মধ্যে শার্ট) নির্দিষ্টভাবে পণ্যের নাম ও দাম সাজেস্ট করবে।
৩. কাস্টমার যখন স্পষ্ট করে বলবে সে "অর্ডার করতে চায়" বা "এটা নিতে চাই", শুধুমাত্র তখনই মার্জিতভাবে বলবে:
   "অর্ডারটি কনফার্ম করতে অনুগ্রহ করে নিচের তথ্যগুলো দিন:
   - আপনার নাম:
   - মোবাইল নম্বর:
   - সম্পূর্ণ ঠিকানা:
   - প্রোডাক্টের নাম ও সাইজ:"
৪. ভাষা হবে অত্যন্ত মার্জিত, প্রফেশনাল ও ইতিবাচক। অপ্রয়োজনীয় দীর্ঘ উত্তর দেবে না।
"""

bot = telebot.TeleBot(BOT_TOKEN)
user_memory = {}

def get_gemini_reply(chat_id, user_text):
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": API_KEY
    }
    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_INSTRUCTION}]},
        "contents": user_memory[chat_id]
    }

    # হাই ডিমান্ড থাকলে ২ বার চেষ্টা করবে
    for _ in range(2):
        try:
            response = requests.post(URL, headers=headers, json=payload, timeout=20)
            res = response.json()
            if "candidates" in res and res["candidates"]:
                return res["candidates"][0]["content"]["parts"][0]["text"]
            elif "error" in res:
                time.sleep(1)
                continue
        except Exception:
            time.sleep(1)
            continue
            
    return "দুঃখিত, আমাদের নেটওয়ার্কে সামান্য ব্যস্ততা রয়েছে। অনুগ্রহ করে ১ মিনিট পর আবার একটু মেসেজ করুন।"

@bot.message_handler(commands=["start"])
def send_welcome(message):
    user_memory[message.chat.id] = []
    welcome_msg = (
        "VELMONT ÉLITE-এ আপনাকে স্বাগতম। ✨\n\n"
        "আমাদের প্রিমিয়াম কালেকশন, সাইজ বা ডেলিভারি সম্পর্কিত যেকোনো তথ্যের জন্য আমাকে জানাতে পারেন। আজ আপনাকে কীভাবে সহযোগিতা করতে পারি?"
    )
    bot.reply_to(message, welcome_msg)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    user_text = message.text

    if chat_id not in user_memory:
        user_memory[chat_id] = []

    user_memory[chat_id].append({"role": "user", "parts": [{"text": user_text}]})

    reply = get_gemini_reply(chat_id, user_text)
    user_memory[chat_id].append({"role": "model", "parts": [{"text": reply}]})
    bot.reply_to(message, reply)

# Render ফ্রি ওয়েব সার্ভিস পোর্ট সচল রাখার জন্য
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"VELMONT ELITE Assistant is Online.")

def run_http_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

if __name__ == "__main__":
    threading.Thread(target=run_http_server, daemon=True).start()
    print("=== VELMONT ELITE Bot চালু হয়েছে... ===")
    bot.infinity_polling()
    
