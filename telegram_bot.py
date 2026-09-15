import os
import threading
import telebot
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler

BOT_TOKEN = "8813841284:AAHF8f-i-GyOGskOqFl8su0-vO8OWRAhraQ"
API_KEY = "AQ.Ab8RN6Jf1FDFa6dIB6Fh-Tuz_bodrfO8-8j3n6mbr3Zehh4qog"
URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"

SYSTEM_INSTRUCTION = """
তুমি একটি প্রিমিয়াম পোশাক ব্র্যান্ডের অফিসিয়াল এআই কাস্টমার সাপোর্ট সহকারী।

ব্যবসার তথ্য ও পলিসি:
১. ডেলিভারি সময়: ঢাকা সিটির ভেতরে ২৪ থেকে ৪৮ ঘণ্টা, ঢাকার বাইরে ২ থেকে ৩ দিন।
২. ডেলিভারি চার্জ: ঢাকার ভেতরে ৬০ টাকা, ঢাকার বাইরে ১২০ টাকা।
৩. রিটার্ন পলিসি: ডেলিভারি ম্যান থাকা অবস্থায় প্রোডাক্ট দেখে নিতে হবে। সাইজ বা অন্য কোনো সমস্যা হলে সাথে সাথে এক্সচেঞ্জ করা যাবে।
৪. পেমেন্ট মেথড: ক্যাশ অন ডেলিভারি (COD) এবং বিকাশ প্রযোজ্য।

কথা বলার নিয়ম:
- কাস্টমারের সাথে অত্যন্ত বিনয়ী ও মার্জিত ভাষায় বাংলায় কথা বলবে।
- উত্তর অপ্রয়োজনীয় লম্বা করবে না, ২-৩ বাক্যে স্পষ্ট রাখবে।
- কাস্টমার অর্ডার করতে চাইলে তার নাম, ফোন নম্বর, সম্পূর্ণ ঠিকানা এবং সাইজ জানতে চাইবে।
"""

bot = telebot.TeleBot(BOT_TOKEN)
user_memory = {}

@bot.message_handler(commands=["start"])
def send_welcome(message):
    user_memory[message.chat.id] = []
    bot.reply_to(message, "স্বাগতম! আমাদের ব্র্যান্ডে আপনাকে স্বাগতম। সাইজ, অর্ডার বা ডেলিভারি বিষয়ে কীভাবে সাহায্য করতে পারি?")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    user_text = message.text

    if chat_id not in user_memory:
        user_memory[chat_id] = []

    user_memory[chat_id].append({"role": "user", "parts": [{"text": user_text}]})

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": API_KEY
    }

    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_INSTRUCTION}]},
        "contents": user_memory[chat_id]
    }

    try:
        response = requests.post(URL, headers=headers, json=payload)
        res = response.json()

        if "candidates" in res and res["candidates"]:
            reply = res["candidates"][0]["content"]["parts"][0]["text"]
            user_memory[chat_id].append({"role": "model", "parts": [{"text": reply}]})
            bot.reply_to(message, reply)
        elif "error" in res:
            bot.reply_to(message, f"API Error: {res['error'].get('message', 'Unknown error')}")
        else:
            bot.reply_to(message, "দুঃখিত, কোনো উত্তর পাওয়া যায়নি।")
    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_http_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

if __name__ == "__main__":
    threading.Thread(target=run_http_server, daemon=True).start()
    print("=== Telegram Bot চালু হয়েছে... ===")
    bot.infinity_polling()
    
