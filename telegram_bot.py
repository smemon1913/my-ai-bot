import os
import json
import threading
import telebot
from google import genai
from http.server import HTTPServer, BaseHTTPRequestHandler

BOT_TOKEN = "8813841284:AAHF8f-i-GyOGskOqFl8su0-vO8OWRAhraQ"
API_KEY = "AQ.Ab8RN6Kp0jgiJu5oIKsoaCEQjDed3l1tzSl82k8Jq65UHrhDkg"

# অফিসিয়াল SDK ক্লায়েন্ট (যা নতুন ফরম্যাটের সব কী সঠিকভাবে হ্যান্ডেল করে)
client = genai.Client(api_key=API_KEY)

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
তুমি প্রিমিয়াম ক্লদিং ব্র্যান্ড "VELMONT ÉLITE"-এর অফিসিয়াল এআই কাস্টমার সাপোর্ট ও সেলস কনসালট্যান্ট।

আমাদের বর্তমান প্রোডাক্ট ক্যাটালগ:
{json.dumps(CATALOG, ensure_ascii=False, indent=2)}

ব্যবসার পলিসি:
- ডেলিভারি চার্জ: ঢাকা সিটিতে ৬০ টাকা, ঢাকার বাইরে ১২০ টাকা।
- ডেলিভারি সময়: ঢাকায় ২৪-৪৮ ঘণ্টা, ঢাকার বাইরে ২-৩ দিন।
- রিটার্ন/এক্সচেঞ্জ: ডেলিভারিম্যানের সামনে চেক করা যাবে। সাইজ মিসম্যাচ হলে ৪৮ ঘণ্টার মধ্যে ফ্রি এক্সচেঞ্জ।
- পেমেন্ট: ক্যাশ অন ডেলিভারি (COD) এবং বিকাশ।

কাস্টমার হ্যান্ডলিং ও রেসপন্স রুলস:
১. কাস্টমার সাধারণ হাই/হ্যালো বললে মার্জিতভাবে সম্ভাষণ জানাও এবং কীভাবে সহযোগিতা করতে পারো তা জানতে চাও। সাথে সাথে অর্ডার ডিটেইলস চাইবে না।
২. কাস্টমার বাজেট বা কালার উল্লেখ করে প্রোডাক্ট দেখতে চাইলে (যেমন: "১৫০০ টাকার মধ্যে শার্ট দেখাও" বা "ব্ল্যাক কালারের টি শার্টের পিক দাও"):
   - ক্যাটালগ খুঁজে পণ্যের নাম, বিবরণ ও দাম জানাবে।
   - ছবি পাঠাতে উত্তরের মধ্যে অবশ্যই ট্যাগ দেবে: `[SEND_IMAGE: প্রোডাক্টের_ID]`
৩. ক্যাটালগে নেই এমন কিছু (যেমন জুতো) চাইলে বিনয়ের সাথে জানাবে যে এটি খুব শীঘ্রই কালেকশনে যুক্ত হবে।
৪. কাস্টমার নিশ্চিতভাবে "অর্ডার করতে চাই" বললে নাম, মোবাইল নম্বর, ঠিকানা ও সাইজ জানতে চাইবে।
৫. ভাষা হবে প্রফেশনাল ও ইতিবাচক বাংলা।
"""

bot = telebot.TeleBot(BOT_TOKEN)

# প্রতিটি ইউজারের জন্য চ্যাট সেশন ট্র্যাক করা
user_chats = {}

def get_or_create_chat(chat_id):
    if chat_id not in user_chats:
        user_chats[chat_id] = client.chats.create(
            model="gemini-2.5-flash",
            config={"system_instruction": SYSTEM_INSTRUCTION}
        )
    return user_chats[chat_id]

@bot.message_handler(commands=["start"])
def send_welcome(message):
    user_chats[message.chat.id] = client.chats.create(
        model="gemini-2.5-flash",
        config={"system_instruction": SYSTEM_INSTRUCTION}
    )
    welcome_text = (
        "VELMONT ÉLITE-এ আপনাকে স্বাগতম! ✨\n\n"
        "আমাদের প্রিমিয়াম শার্ট, ডেনিম প্যান্ট ও টি-শার্টের কালেকশন দেখতে পারেন।\n"
        "যেকোনো কালার, সাইজ, প্রাইস বা ছবি দেখতে চাইলে নির্দ্বিধায় আমাকে জানান।"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    user_text = message.text

    try:
        chat = get_or_create_chat(chat_id)
        response = chat.send_message(user_text)
        reply = response.text

        # ইমেজ কমান্ড হ্যান্ডলিং
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

    except Exception as e:
        print(f"Chat error: {e}")
        bot.reply_to(message, f"এরর হয়েছে: {str(e)}")

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
    print("=== Bot Started with Official SDK ===")
    bot.infinity_polling()
    
