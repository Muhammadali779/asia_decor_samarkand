#!/usr/bin/env python3
"""
Asia Decor Samarkand — Admin Telegram Bot
Adminlar buyurtmalarni boshqaradi, statistika ko'radi.
Django DB bilan to'liq integratsiya.
"""
import os
import sys
import logging
from pathlib import Path

# Django setup
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asia_decor.settings')

# Load .env
env_file = BASE_DIR / '.env'
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            os.environ.setdefault(k.strip(), v.strip())

import django
django.setup()

try:
    from telebot import TeleBot, types
except ImportError:
    print("ERROR: pip install pyTelegramBotAPI")
    sys.exit(1)

# ===== CONFIG =====
ADMIN_BOT_TOKEN = os.environ.get('ADMIN_BOT_TOKEN', '')
_raw_ids = os.environ.get('ALLOWED_ADMIN_IDS', '')
ALLOWED_ADMIN_IDS = [int(x) for x in _raw_ids.split(',') if x.strip().isdigit()]

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s — %(levelname)s — %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('admin_bot.log', encoding='utf-8'),
    ]
)
logger = logging.getLogger(__name__)

bot = TeleBot(ADMIN_BOT_TOKEN, parse_mode='HTML')


def is_admin(uid):
    if not ALLOWED_ADMIN_IDS:
        return True  # Cheklov yo'q
    return uid in ALLOWED_ADMIN_IDS


def admin_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(
        types.KeyboardButton("📋 Barcha buyurtmalar"),
        types.KeyboardButton("🆕 Yangi buyurtmalar"),
        types.KeyboardButton("📊 Statistika"),
        types.KeyboardButton("✅ Tasdiqlangan"),
        types.KeyboardButton("🔄 Jarayonda"),
        types.KeyboardButton("⚙️ Sozlamalar"),
    )
    return kb


# ===== START =====
@bot.message_handler(commands=['start'])
def cmd_start(msg):
    uid = msg.from_user.id
    if not is_admin(uid):
        bot.send_message(msg.chat.id, "❌ Ruxsat yo'q.")
        return
    bot.send_message(
        msg.chat.id,
        f"👋 Xush kelibsiz, Admin!\n\n🆔 Sizning ID: <code>{uid}</code>\n\n🏢 Asia Decor Admin Bot",
        reply_markup=admin_kb()
    )


@bot.message_handler(commands=['myid'])
def cmd_myid(msg):
    bot.send_message(
        msg.chat.id,
        f"🆔 Sizning Telegram ID: <code>{msg.from_user.id}</code>\n\n.env fayliga ALLOWED_ADMIN_IDS ga qo'shing."
    )


# ===== ORDER CARD =====
STATUS_EMOJI = {
    'new': '🆕', 'confirmed': '✅', 'in_progress': '🔄',
    'completed': '✔️', 'cancelled': '❌'
}
STATUS_LABEL = {
    'new': 'Yangi', 'confirmed': 'Tasdiqlangan', 'in_progress': 'Jarayonda',
    'completed': 'Bajarilgan', 'cancelled': 'Bekor qilingan'
}


def send_order_card(chat_id, order):
    pay_lbl = "To'liq" if order.payment_type == 'full' else "Zaklad"
    text = (
        f"{STATUS_EMOJI.get(order.status, '📋')} <b>Buyurtma #{order.id}</b> — {STATUS_LABEL.get(order.status,'')}\n\n"
        f"📦 <b>{order.service_title}</b>\n"
        f"💵 Narxi: {int(order.service_price):,} so'm\n\n"
        f"👤 <b>Buyurtmachi:</b>\n"
        f"• Ism: <b>{order.customer_name}</b>\n"
        f"• 📱 Tel: <code>{order.customer_phone}</code>\n"
        f"• 📍 Manzil: {order.delivery_address}\n\n"
        f"🎂 <b>Tabriklanuvchi:</b>\n"
        f"• {order.birthday_person_name} ({order.birthday_person_age} yosh)\n"
    )
    if order.event_date:
        text += f"• 📅 Sana: {order.event_date}\n"
    text += (
        f"\n💳 {pay_lbl}: <b>{int(order.amount_paid):,} so'm</b>\n"
    )
    if order.notes:
        text += f"📝 {order.notes}\n"
    text += f"⏰ {order.created_at.strftime('%d.%m.%Y %H:%M')}"

    kb = types.InlineKeyboardMarkup(row_width=2)
    if order.status == 'new':
        kb.add(
            types.InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"confirm_{order.id}"),
            types.InlineKeyboardButton("❌ Bekor", callback_data=f"cancel_{order.id}"),
        )
    elif order.status == 'confirmed':
        kb.add(
            types.InlineKeyboardButton("🔄 Jarayonga ol", callback_data=f"progress_{order.id}"),
            types.InlineKeyboardButton("✔️ Bajarildi", callback_data=f"complete_{order.id}"),
        )
    kb.add(types.InlineKeyboardButton(f"📞 {order.customer_phone}", url=f"tel:{order.customer_phone}"))

    try:
        bot.send_message(chat_id, text, reply_markup=kb)
    except Exception as e:
        logger.error(f"Order card error: {e}")


# ===== HANDLERS =====
@bot.message_handler(func=lambda m: m.text == "📋 Barcha buyurtmalar")
def handle_all_orders(msg):
    if not is_admin(msg.from_user.id): return
    from core.models import Order
    orders = list(Order.objects.select_related('service').order_by('-created_at')[:10])
    if not orders:
        bot.send_message(msg.chat.id, "📭 Buyurtmalar yo'q."); return
    bot.send_message(msg.chat.id, f"📋 So'nggi {len(orders)} ta buyurtma:")
    for o in orders:
        send_order_card(msg.chat.id, o)


@bot.message_handler(func=lambda m: m.text == "🆕 Yangi buyurtmalar")
def handle_new_orders(msg):
    if not is_admin(msg.from_user.id): return
    from core.models import Order
    orders = list(Order.objects.filter(status='new').order_by('-created_at')[:10])
    if not orders:
        bot.send_message(msg.chat.id, "✅ Yangi buyurtmalar yo'q."); return
    bot.send_message(msg.chat.id, f"🆕 Yangi buyurtmalar: <b>{len(orders)}</b> ta")
    for o in orders:
        send_order_card(msg.chat.id, o)


@bot.message_handler(func=lambda m: m.text == "✅ Tasdiqlangan")
def handle_confirmed(msg):
    if not is_admin(msg.from_user.id): return
    from core.models import Order
    orders = list(Order.objects.filter(status='confirmed').order_by('-created_at')[:10])
    if not orders:
        bot.send_message(msg.chat.id, "📭 Tasdiqlangan buyurtmalar yo'q."); return
    for o in orders:
        send_order_card(msg.chat.id, o)


@bot.message_handler(func=lambda m: m.text == "🔄 Jarayonda")
def handle_in_progress(msg):
    if not is_admin(msg.from_user.id): return
    from core.models import Order
    orders = list(Order.objects.filter(status='in_progress').order_by('-created_at')[:10])
    if not orders:
        bot.send_message(msg.chat.id, "📭 Jarayondagi buyurtmalar yo'q."); return
    for o in orders:
        send_order_card(msg.chat.id, o)


@bot.message_handler(func=lambda m: m.text == "📊 Statistika")
def handle_stats(msg):
    if not is_admin(msg.from_user.id): return
    from core.models import Order
    from django.db.models import Sum

    total = Order.objects.count()
    new_c = Order.objects.filter(status='new').count()
    confirmed_c = Order.objects.filter(status='confirmed').count()
    in_prog = Order.objects.filter(status='in_progress').count()
    done = Order.objects.filter(status='completed').count()
    cancelled = Order.objects.filter(status='cancelled').count()
    revenue = Order.objects.filter(status='completed').aggregate(s=Sum('amount_paid'))['s'] or 0

    text = (
        f"📊 <b>Statistika</b>\n\n"
        f"📋 Jami buyurtmalar: <b>{total}</b>\n"
        f"🆕 Yangi: <b>{new_c}</b>\n"
        f"✅ Tasdiqlangan: <b>{confirmed_c}</b>\n"
        f"🔄 Jarayonda: <b>{in_prog}</b>\n"
        f"✔️ Bajarilgan: <b>{done}</b>\n"
        f"❌ Bekor: <b>{cancelled}</b>\n\n"
        f"💰 Jami tushum: <b>{int(revenue):,} so'm</b>"
    )
    bot.send_message(msg.chat.id, text)


@bot.message_handler(func=lambda m: m.text == "⚙️ Sozlamalar")
def handle_settings(msg):
    if not is_admin(msg.from_user.id): return
    from core.models import AgencySettings
    a = AgencySettings.objects.first()
    if a:
        text = (
            f"⚙️ <b>Agentlik sozlamalari</b>\n\n"
            f"🏢 Nomi: {a.name}\n"
            f"📱 Tel 1: {a.phone1 or '—'}\n"
            f"📱 Tel 2: {a.phone2 or '—'}\n"
            f"📧 Email: {a.email or '—'}\n"
            f"💳 Karta: <code>{a.payment_card}</code>\n"
            f"📊 Zaklad: {a.advance_percent}%\n\n"
            f"Sozlamalar uchun admin panel: /admin"
        )
    else:
        text = "⚙️ Sozlamalar kiritilmagan."
    bot.send_message(msg.chat.id, text)


# ===== CALLBACK (order status change) =====
ACTION_STATUS = {
    'confirm': ('confirmed', '✅ Tasdiqlandi'),
    'cancel': ('cancelled', '❌ Bekor qilindi'),
    'progress': ('in_progress', '🔄 Jarayonga olindi'),
    'complete': ('completed', '✔️ Bajarildi'),
}

@bot.callback_query_handler(func=lambda c: True)
def handle_callback(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ Ruxsat yo'q"); return

    from core.models import Order
    parts = call.data.split('_')
    action = parts[0]
    try:
        order_id = int(parts[1])
    except (IndexError, ValueError):
        bot.answer_callback_query(call.id); return

    if action in ACTION_STATUS:
        new_status, label = ACTION_STATUS[action]
        try:
            order = Order.objects.get(id=order_id)
            order.status = new_status
            order.save(update_fields=['status'])
            bot.answer_callback_query(call.id, label)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            bot.send_message(call.message.chat.id,
                f"{label}: Buyurtma #{order_id}\n👤 {order.customer_name} | 📱 {order.customer_phone}")
        except Order.DoesNotExist:
            bot.answer_callback_query(call.id, "Buyurtma topilmadi")
    else:
        bot.answer_callback_query(call.id)


@bot.message_handler(func=lambda m: True)
def handle_unknown(msg):
    if not is_admin(msg.from_user.id):
        bot.send_message(msg.chat.id, "❌ Ruxsat yo'q."); return
    bot.send_message(msg.chat.id, "Menyudan tanlang:", reply_markup=admin_kb())


if __name__ == '__main__':
    if not ADMIN_BOT_TOKEN:
        print("⚠️  ADMIN_BOT_TOKEN o'rnatilmagan!")
        print("   .env faylini to'ldiring:")
        print("   ADMIN_BOT_TOKEN=your_token")
        sys.exit(1)
    logger.info("🤖 Asia Decor Admin Bot ishga tushdi")
    print("✅ Admin Bot ishlamoqda...")
    print(f"   Ruxsatli adminlar: {ALLOWED_ADMIN_IDS if ALLOWED_ADMIN_IDS else 'Hammasi (cheklov yo\\'q)'}")
    bot.infinity_polling(logger_level=logging.WARNING, timeout=30, long_polling_timeout=30)
