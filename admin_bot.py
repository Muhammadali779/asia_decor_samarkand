#!/usr/bin/env python3
import os
import sys
import logging
from pathlib import Path

# ===== DJANGO SETUP =====
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asia_decor.settings')

# .env load (SAFE)
env_file = BASE_DIR / '.env'
if env_file.exists():
    for line in env_file.read_text().splitlines():
        if '=' in line and not line.strip().startswith('#'):
            k, v = line.split('=', 1)
            os.environ[k.strip()] = v.strip()

import django
django.setup()

from telebot import TeleBot, types

# ===== CONFIG =====
ADMIN_BOT_TOKEN = os.getenv('ADMIN_BOT_TOKEN')

_raw_ids = os.getenv('ALLOWED_ADMIN_IDS', '')
ALLOWED_ADMIN_IDS = [
    int(x.strip()) for x in _raw_ids.split(',') if x.strip().isdigit()
]

# ===== LOGGING =====
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)

bot = TeleBot(ADMIN_BOT_TOKEN, parse_mode='HTML')

# ===== HELPERS =====
def is_admin(uid: int) -> bool:
    if not ALLOWED_ADMIN_IDS:
        return True
    return uid in ALLOWED_ADMIN_IDS


def admin_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("📋 Barcha buyurtmalar", "🆕 Yangi buyurtmalar")
    kb.row("📊 Statistika", "✅ Tasdiqlangan")
    kb.row("🔄 Jarayonda", "⚙️ Sozlamalar")
    return kb


# ===== START =====
@bot.message_handler(commands=['start'])
def start(msg):
    uid = msg.from_user.id

    print(f"ADMIN LOGIN: {uid}")  # DEBUG

    if not is_admin(uid):
        bot.send_message(msg.chat.id, "❌ Ruxsat yo'q")
        return

    bot.send_message(
        msg.chat.id,
        f"👋 Admin panelga xush kelibsiz\n\n🆔 <code>{uid}</code>",
        reply_markup=admin_kb()
    )


# ===== GET ID =====
@bot.message_handler(commands=['myid'])
def myid(msg):
    bot.send_message(
        msg.chat.id,
        f"🆔 ID: <code>{msg.from_user.id}</code>"
    )


# ===== ORDER CARD =====
def send_order(chat_id, o):
    text = f"""
📦 <b>Buyurtma #{o.id}</b>

👤 {o.customer_name}
📱 {o.customer_phone}
📍 {o.delivery_address}

💰 {int(o.amount_paid):,} so'm
📅 {o.created_at.strftime('%d.%m.%Y')}
"""

    kb = types.InlineKeyboardMarkup()

    kb.add(
        types.InlineKeyboardButton("✅", callback_data=f"confirm_{o.id}"),
        types.InlineKeyboardButton("❌", callback_data=f"cancel_{o.id}")
    )

    bot.send_message(chat_id, text, reply_markup=kb)


# ===== ALL ORDERS =====
@bot.message_handler(func=lambda m: m.text == "📋 Barcha buyurtmalar")
def all_orders(msg):
    if not is_admin(msg.from_user.id):
        return

    from core.models import Order

    orders = Order.objects.all().order_by('-id')[:5]

    if not orders:
        bot.send_message(msg.chat.id, "Bo'sh")
        return

    for o in orders:
        send_order(msg.chat.id, o)


# ===== STATS =====
@bot.message_handler(func=lambda m: m.text == "📊 Statistika")
def stats(msg):
    if not is_admin(msg.from_user.id):
        return

    from core.models import Order

    total = Order.objects.count()

    bot.send_message(
        msg.chat.id,
        f"📊 Jami buyurtmalar: {total}"
    )


# ===== CALLBACK =====
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌")
        return

    from core.models import Order

    action, oid = call.data.split('_')

    try:
        order = Order.objects.get(id=int(oid))
    except:
        bot.answer_callback_query(call.id, "Topilmadi")
        return

    if action == "confirm":
        order.status = "confirmed"
    elif action == "cancel":
        order.status = "cancelled"

    order.save()

    bot.answer_callback_query(call.id, "OK")
    bot.send_message(call.message.chat.id, f"Yangilandi #{order.id}")


# ===== UNKNOWN =====
@bot.message_handler(func=lambda m: True)
def unknown(msg):
    if not is_admin(msg.from_user.id):
        return
    bot.send_message(msg.chat.id, "Menu tanlang", reply_markup=admin_kb())


# ===== RUN =====
if __name__ == "__main__":
    if not ADMIN_BOT_TOKEN:
        print("TOKEN YO'Q")
        sys.exit()

    print("BOT ISHLADI")
    bot.infinity_polling()