#!/usr/bin/env python3
"""
Asia Decor Samarkand — Foydalanuvchi Telegram Bot
Mijozlar xizmatlarni ko'rib buyurtma berishi mumkin.
Django DB bilan to'liq integratsiya.
"""
import os
import sys
import logging
import requests
from datetime import datetime
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
BOT_TOKEN = os.environ.get('USER_BOT_TOKEN', '')
ADMIN_BOT_TOKEN = os.environ.get('ADMIN_BOT_TOKEN', '')
ADMIN_CHAT_ID = os.environ.get('ADMIN_CHAT_ID', '')
SITE_URL = os.environ.get('SITE_URL', 'http://localhost:8000').rstrip('/')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s — %(levelname)s — %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('user_bot.log', encoding='utf-8'),
    ]
)
logger = logging.getLogger(__name__)

bot = TeleBot(BOT_TOKEN, parse_mode='HTML')

# ===== STATES =====
user_states = {}

S_MENU = 'menu'
S_ORDER_NAME = 'order_name'
S_ORDER_PHONE = 'order_phone'
S_ORDER_ADDR = 'order_address'
S_ORDER_BNAME = 'order_bname'
S_ORDER_BAGE = 'order_bage'
S_ORDER_DATE = 'order_date'
S_ORDER_NOTES = 'order_notes'
S_ORDER_PAY = 'order_payment'


def state(uid): return user_states.get(uid, {}).get('state', S_MENU)
def data(uid): return user_states.get(uid, {})


# ===== DB HELPERS =====
def get_agency():
    from core.models import AgencySettings
    a = AgencySettings.objects.first()
    if not a:
        a = AgencySettings.objects.create()
    return a

def get_services(stype):
    from core.models import ServiceItem
    return list(ServiceItem.objects.filter(service_type=stype, is_active=True).order_by('sort_order'))

def save_order(d):
    from core.models import Order, ServiceItem
    try:
        svc = ServiceItem.objects.filter(id=d.get('service_id')).first()
        o = Order.objects.create(
            service=svc,
            service_title=d.get('service_title', ''),
            service_price=d.get('service_price', 0),
            customer_name=d.get('customer_name', ''),
            customer_phone=d.get('customer_phone', ''),
            delivery_address=d.get('delivery_address', ''),
            birthday_person_name=d.get('birthday_person_name', ''),
            birthday_person_age=d.get('birthday_person_age', 0),
            event_date=d.get('event_date') or None,
            payment_type=d.get('payment_type', 'full'),
            amount_paid=d.get('amount_paid', 0),
            notes=d.get('notes', ''),
            telegram_notified=True,
        )
        return o
    except Exception as e:
        logger.error(f"DB save error: {e}")
        return None


def notify_admin(order, d):
    """Admin botga yangi buyurtma haqida xabar yuborish"""
    try:
        if not ADMIN_BOT_TOKEN:
            return
        pay_lbl = "To'liq to'lov" if d.get('payment_type') == 'full' else "Zaklad (oldindan)"
        msg = (
            f"🔔 <b>YANGI BUYURTMA #{order.id if order else '?'}</b> (Bot orqali)\n\n"
            f"📦 <b>{d.get('service_title', '')}</b>\n"
            f"💵 Narxi: {int(d.get('service_price',0)):,} so'm\n\n"
            f"👤 <b>Buyurtmachi:</b>\n"
            f"• Ism: <b>{d.get('customer_name','')}</b>\n"
            f"• 📱 Tel: <code>{d.get('customer_phone','')}</code>\n"
            f"• 📍 Manzil: {d.get('delivery_address','')}\n\n"
            f"🎂 <b>Tabriklanuvchi:</b>\n"
            f"• {d.get('birthday_person_name','')} ({d.get('birthday_person_age','')} yosh)\n"
        )
        if d.get('event_date'):
            msg += f"• Sana: {d['event_date']}\n"
        msg += (
            f"\n💳 <b>{pay_lbl}</b>\n"
            f"💰 To'langan: <b>{int(d.get('amount_paid',0)):,} so'm</b>\n"
        )
        if d.get('notes'):
            msg += f"📝 Izoh: {d['notes']}\n"
        msg += f"\n⏰ {datetime.now().strftime('%d.%m.%Y %H:%M')}"

        url = f"https://api.telegram.org/bot{ADMIN_BOT_TOKEN}/sendMessage"
        requests.post(url, json={
            'chat_id': ADMIN_CHAT_ID,
            'text': msg,
            'parse_mode': 'HTML'
        }, timeout=10)
        logger.info(f"Admin notified for order #{order.id if order else '?'}")
    except Exception as e:
        logger.error(f"Admin notify error: {e}")


# ===== KEYBOARDS =====
def main_menu_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(
        types.KeyboardButton("🎁 Tabriklar"),
        types.KeyboardButton("💐 To'y bezaklari"),
        types.KeyboardButton("💍 Sarpo-sandiq"),
        types.KeyboardButton("🌐 Veb sayt"),
        types.KeyboardButton("📞 Kontaktlar"),
        types.KeyboardButton("📋 Buyurtma berish"),
    )
    return kb


# ===== /start =====
@bot.message_handler(commands=['start', 'menu'])
def cmd_start(msg):
    uid = msg.from_user.id
    user_states[uid] = {'state': S_MENU}
    agency = get_agency()
    text = (
        f"✨ <b>{agency.name}</b> botiga xush kelibsiz!\n\n"
        f"🌹 {agency.tagline}\n\n"
        "Kerakli bo'limni tanlang 👇"
    )
    bot.send_message(msg.chat.id, text, reply_markup=main_menu_kb())


# ===== WEBSITE =====
@bot.message_handler(func=lambda m: m.text == "🌐 Veb sayt")
def handle_website(msg):
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🌐 Saytga o'tish", url=SITE_URL))
    bot.send_message(msg.chat.id, "Veb saytimiz:", reply_markup=kb)


# ===== CONTACTS =====
@bot.message_handler(func=lambda m: m.text == "📞 Kontaktlar")
def handle_contacts(msg):
    agency = get_agency()
    text = "📞 <b>Aloqa ma'lumotlari</b>\n\n"
    if agency.phone1: text += f"📱 <code>{agency.phone1}</code>\n"
    if agency.phone2: text += f"📱 <code>{agency.phone2}</code>\n"
    if agency.email: text += f"📧 {agency.email}\n"
    if agency.address: text += f"📍 {agency.address}\n"
    text += "\n<b>Ijtimoiy tarmoqlar:</b>\n"
    if agency.telegram_link: text += f"✈️ <a href='{agency.telegram_link}'>Telegram</a>\n"
    if agency.instagram_link: text += f"📸 <a href='{agency.instagram_link}'>Instagram</a>\n"
    if agency.youtube_link: text += f"▶️ <a href='{agency.youtube_link}'>YouTube</a>\n"
    if agency.tiktok_link: text += f"🎵 <a href='{agency.tiktok_link}'>TikTok</a>\n"
    kb = types.InlineKeyboardMarkup()
    if agency.phone1:
        kb.add(types.InlineKeyboardButton(f"📞 {agency.phone1}", url=f"tel:{agency.phone1}"))
    bot.send_message(msg.chat.id, text, reply_markup=kb, disable_web_page_preview=True)


# ===== CATEGORIES =====
CAT_MAP = {
    "🎁 Tabriklar": ("tabrik", "Tabriklar"),
    "💐 To'y bezaklari": ("bezak", "To'y bezaklari"),
    "💍 Sarpo-sandiq": ("sarpo", "Sarpo-sandiq"),
}

@bot.message_handler(func=lambda m: m.text in CAT_MAP)
def handle_category(msg):
    stype, label = CAT_MAP[msg.text]
    services = get_services(stype)
    if not services:
        bot.send_message(msg.chat.id, "❌ Hozircha bu bo'limda xizmatlar yo'q.")
        return
    kb = types.InlineKeyboardMarkup(row_width=1)
    for s in services:
        kb.add(types.InlineKeyboardButton(
            f"{s.title} — {int(s.price):,} {s.price_label}",
            callback_data=f"svc_{s.id}"
        ))
    bot.send_message(msg.chat.id, f"✨ <b>{label}</b>\n\nXizmatni tanlang:", reply_markup=kb)


# ===== SERVICE SELECT =====
@bot.callback_query_handler(func=lambda c: c.data.startswith('svc_'))
def handle_svc_select(call):
    from core.models import ServiceItem
    svc_id = int(call.data.split('_')[1])
    svc = ServiceItem.objects.filter(id=svc_id, is_active=True).first()
    if not svc:
        bot.answer_callback_query(call.id, "Xizmat topilmadi")
        return
    desc = f"\n📝 {svc.description}" if svc.description else ""
    text = (
        f"✨ <b>{svc.title}</b>\n"
        f"💵 Narxi: <b>{int(svc.price):,} {svc.price_label}</b>"
        f"{desc}\n\nBuyurtma berish uchun tugmani bosing:"
    )
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("📋 Buyurtma berish", callback_data=f"order_{svc.id}"),
        types.InlineKeyboardButton("🌐 Saytda ko'rish", url=f"{SITE_URL}/xizmat/{svc.id}/"),
    )
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=kb)
    bot.answer_callback_query(call.id)


# ===== ORDER START =====
@bot.callback_query_handler(func=lambda c: c.data.startswith('order_'))
def handle_order_start(call):
    from core.models import ServiceItem
    svc_id = int(call.data.split('_')[1])
    svc = ServiceItem.objects.filter(id=svc_id, is_active=True).first()
    if not svc:
        bot.answer_callback_query(call.id, "Xizmat topilmadi")
        return
    uid = call.from_user.id
    user_states[uid] = {
        'state': S_ORDER_NAME,
        'service_id': svc.id,
        'service_title': svc.title,
        'service_price': int(svc.price),
    }
    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        "📝 <b>Buyurtma berish</b>\n\n1️⃣ Ismingiz va familiyangizni kiriting:",
        reply_markup=types.ForceReply()
    )


@bot.message_handler(func=lambda m: m.text == "📋 Buyurtma berish")
def handle_order_menu(msg):
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("🎁 Tabrik buyurtmasi", callback_data="cat_tabrik"),
        types.InlineKeyboardButton("💐 To'y bezak buyurtmasi", callback_data="cat_bezak"),
        types.InlineKeyboardButton("💍 Sarpo-sandiq buyurtmasi", callback_data="cat_sarpo"),
        types.InlineKeyboardButton("🌐 Sayt orqali buyurtma", url=SITE_URL),
    )
    bot.send_message(msg.chat.id, "📋 <b>Qaysi xizmat bo'yicha buyurtma?</b>", reply_markup=kb)


@bot.callback_query_handler(func=lambda c: c.data.startswith('cat_'))
def handle_cat_for_order(call):
    stype = call.data.split('_')[1]
    services = get_services(stype)
    if not services:
        bot.answer_callback_query(call.id, "Hozircha mavjud emas")
        return
    kb = types.InlineKeyboardMarkup(row_width=1)
    for s in services:
        kb.add(types.InlineKeyboardButton(f"{s.title} — {int(s.price):,} so'm", callback_data=f"order_{s.id}"))
    bot.edit_message_text("Xizmatni tanlang:", call.message.chat.id, call.message.message_id, reply_markup=kb)
    bot.answer_callback_query(call.id)


# ===== ORDER FLOW =====
@bot.message_handler(func=lambda m: state(m.from_user.id) == S_ORDER_NAME)
def step_name(msg):
    uid = msg.from_user.id
    if not msg.text or len(msg.text.strip()) < 2:
        bot.send_message(msg.chat.id, "❌ To'liq ism kiriting."); return
    user_states[uid]['customer_name'] = msg.text.strip()
    user_states[uid]['state'] = S_ORDER_PHONE
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(types.KeyboardButton("📱 Raqamimni yuborish", request_contact=True))
    bot.send_message(msg.chat.id, "2️⃣ Telefon raqamingiz:\n(Masalan: +998901234567)", reply_markup=kb)


@bot.message_handler(content_types=['contact'], func=lambda m: state(m.from_user.id) == S_ORDER_PHONE)
def step_phone_contact(msg):
    uid = msg.from_user.id
    phone = msg.contact.phone_number
    if not phone.startswith('+'): phone = '+' + phone
    user_states[uid]['customer_phone'] = phone
    user_states[uid]['state'] = S_ORDER_ADDR
    bot.send_message(msg.chat.id, "3️⃣ Yetkazish manzili:", reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(func=lambda m: state(m.from_user.id) == S_ORDER_PHONE)
def step_phone_text(msg):
    uid = msg.from_user.id
    phone = (msg.text or '').strip()
    if len(phone) < 9:
        bot.send_message(msg.chat.id, "❌ Raqam noto'g'ri. Qayta kiriting:"); return
    user_states[uid]['customer_phone'] = phone
    user_states[uid]['state'] = S_ORDER_ADDR
    bot.send_message(msg.chat.id, "3️⃣ Yetkazish manzili:", reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(func=lambda m: state(m.from_user.id) == S_ORDER_ADDR)
def step_addr(msg):
    uid = msg.from_user.id
    user_states[uid]['delivery_address'] = (msg.text or '').strip()
    user_states[uid]['state'] = S_ORDER_BNAME
    bot.send_message(msg.chat.id, "4️⃣ Tabriklanuvchining ismi:")


@bot.message_handler(func=lambda m: state(m.from_user.id) == S_ORDER_BNAME)
def step_bname(msg):
    uid = msg.from_user.id
    user_states[uid]['birthday_person_name'] = (msg.text or '').strip()
    user_states[uid]['state'] = S_ORDER_BAGE
    bot.send_message(msg.chat.id, "5️⃣ Tabriklanuvchining yoshi:")


@bot.message_handler(func=lambda m: state(m.from_user.id) == S_ORDER_BAGE)
def step_bage(msg):
    uid = msg.from_user.id
    try:
        age = int((msg.text or '').strip())
        if not 1 <= age <= 120: raise ValueError
    except:
        bot.send_message(msg.chat.id, "❌ Yoshni to'g'ri raqam bilan kiriting:"); return
    user_states[uid]['birthday_person_age'] = age
    user_states[uid]['state'] = S_ORDER_DATE
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(types.KeyboardButton("⏭ O'tkazib yuborish"))
    bot.send_message(msg.chat.id, "6️⃣ Tadbir sanasi (Masalan: 25.12.2024)\nYoki o'tkazib yuborish:", reply_markup=kb)


@bot.message_handler(func=lambda m: state(m.from_user.id) == S_ORDER_DATE)
def step_date(msg):
    uid = msg.from_user.id
    text = (msg.text or '').strip()
    user_states[uid]['event_date'] = None if "O'tkazib" in text else text
    user_states[uid]['state'] = S_ORDER_NOTES
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(types.KeyboardButton("⏭ O'tkazib yuborish"))
    bot.send_message(msg.chat.id, "7️⃣ Qo'shimcha xohishlar yoki izoh:", reply_markup=kb)


@bot.message_handler(func=lambda m: state(m.from_user.id) == S_ORDER_NOTES)
def step_notes(msg):
    uid = msg.from_user.id
    text = (msg.text or '').strip()
    user_states[uid]['notes'] = '' if "O'tkazib" in text else text
    user_states[uid]['state'] = S_ORDER_PAY

    d = user_states[uid]
    price = d.get('service_price', 0)
    agency = get_agency()
    pct = agency.advance_percent
    advance = int(price * pct / 100)
    card = agency.payment_card
    card_owner = agency.payment_card_owner

    user_states[uid]['advance_amount'] = advance
    user_states[uid]['payment_card'] = card

    summary = (
        f"📋 <b>Buyurtma xulosasi</b>\n\n"
        f"🎁 {d.get('service_title')}\n"
        f"💵 Narxi: <b>{price:,} so'm</b>\n"
        f"👤 {d.get('customer_name')}\n"
        f"📱 {d.get('customer_phone')}\n"
        f"📍 {d.get('delivery_address')}\n"
        f"🎂 {d.get('birthday_person_name')} ({d.get('birthday_person_age')} yosh)\n"
        f"\n💳 Karta: <code>{card}</code>\n"
    )
    if card_owner:
        summary += f"👤 {card_owner}\n"
    summary += "\n<b>To'lov turini tanlang:</b>"

    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton(f"💳 To'liq: {price:,} so'm", callback_data="pay_full"),
        types.InlineKeyboardButton(f"💰 Zaklad {pct}%: {advance:,} so'm", callback_data="pay_advance"),
    )
    kb.add(types.InlineKeyboardButton("❌ Bekor qilish", callback_data="pay_cancel"))

    bot.send_message(msg.chat.id, summary, parse_mode='HTML', reply_markup=kb)


@bot.callback_query_handler(func=lambda c: c.data.startswith('pay_'))
def handle_payment(call):
    uid = call.from_user.id
    action = call.data.split('_')[1]

    if action == 'cancel':
        user_states.pop(uid, None)
        bot.edit_message_text("❌ Buyurtma bekor qilindi.", call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "Asosiy menyu:", reply_markup=main_menu_kb())
        bot.answer_callback_query(call.id)
        return

    d = user_states.get(uid, {})
    price = d.get('service_price', 0)
    advance = d.get('advance_amount', 0)
    amount = price if action == 'full' else advance
    d['payment_type'] = 'full' if action == 'full' else 'advance'
    d['amount_paid'] = amount

    order = save_order(d)
    notify_admin(order, d)

    card = d.get('payment_card', '')
    success = (
        f"✅ <b>Buyurtmangiz qabul qilindi!</b>\n\n"
        f"🆔 Buyurtma #{order.id if order else '?'}\n"
        f"💳 Karta: <code>{card}</code>\n"
        f"💰 To'lash kerak: <b>{amount:,} so'm</b>\n\n"
        f"To'lovdan so'ng admin siz bilan bog'lanadi.\n"
        f"⏰ Bog'lanish vaqti: 30 daqiqa ichida\n\n"
        f"Rahmat! 🌹"
    )
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🌐 Saytga o'tish", url=SITE_URL))

    bot.edit_message_text(success, call.message.chat.id, call.message.message_id,
                          parse_mode='HTML', reply_markup=kb)
    bot.send_message(call.message.chat.id, "Asosiy menyu:", reply_markup=main_menu_kb())

    user_states.pop(uid, None)
    bot.answer_callback_query(call.id, "✅ Qabul qilindi!")


@bot.message_handler(func=lambda m: True)
def handle_unknown(msg):
    bot.send_message(msg.chat.id, "Pastdagi menyudan tanlang 👇", reply_markup=main_menu_kb())


if __name__ == '__main__':
    if not BOT_TOKEN:
        print("⚠️  USER_BOT_TOKEN o'rnatilmagan!")
        print("   .env faylini to'ldiring:")
        print("   USER_BOT_TOKEN=your_token")
        sys.exit(1)
    logger.info("🤖 Asia Decor User Bot ishga tushdi")
    print("✅ User Bot ishlamoqda...")
    print(f"   Site URL: {SITE_URL}")
    bot.infinity_polling(logger_level=logging.WARNING, timeout=30, long_polling_timeout=30)
