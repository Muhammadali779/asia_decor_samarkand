# 🌟 Asia Decor Samarkand — To'liq Loyiha

**Black & Gold dizayn | Mobil-first | Django + Telegram Botlar**

---

## 📁 Loyiha tuzilmasi

```
asia_decor/        ← Django veb sayt
user_bot/          ← Foydalanuvchi Telegram boti
admin_bot/         ← Admin Telegram boti
```

---

## ⚡ Tez ishga tushirish

### 1. .env fayli yaratish

```bash
cd asia_decor
cp .env.example .env
nano .env   # tokenlarni to'ldiring
```

**.env mazmuni:**
```
SECRET_KEY=o'zingizning_maxfiy_kalit
DEBUG=True
SITE_URL=https://sizning-domen.uz

USER_BOT_TOKEN=1234567890:AAF...    # User bot tokeni
ADMIN_BOT_TOKEN=0987654321:AAB...   # Admin bot tokeni
ADMIN_CHAT_ID=123456789             # Admin Telegram ID
ALLOWED_ADMIN_IDS=123456789         # Admin ID(lar), vergul bilan
```

### 2. Django o'rnatish

```bash
cd asia_decor
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

**Admin panel:** http://localhost:8000/admin/

### 3. User Bot ishga tushirish (yangi terminal)

```bash
cd user_bot
source ../asia_decor/venv/bin/activate
python user_bot.py
```

### 4. Admin Bot ishga tushirish (yangi terminal)

```bash
cd admin_bot
source ../asia_decor/venv/bin/activate
python admin_bot.py
```

---

## 🤖 Telegram ID olish

Admin botga `/myid` yuboring yoki @userinfobot ga `/start` yuboring.

---

## 🎨 Veb sayt sahifalari

| Sahifa | URL | Tavsif |
|--------|-----|--------|
| Bosh sahifa | `/` | Logo + ijtimoiy tugmalar + xizmatlar |
| Tabriklar | `/tabriklar/` | Barcha tabriklar ro'yxati |
| Bezaklar | `/bezaklar/` | To'y bezaklari va sarpo-sandiq |
| Xizmat detail | `/xizmat/<id>/` | Xizmat batafsil + buyurtma modal |
| Kontaktlar | `/kontaktlar/` | Telefon, manzil, ijtimoiy |
| Admin panel | `/admin/` | Barcha boshqaruv |

---

## ⚙️ Admin paneldan boshqarish

**Agentlik sozlamalari:**
- Logo (bosh sahifada ko'rinadi)
- Telefon raqamlar (bosilganda qo'ng'iroq qiladi)
- Ijtimoiy tarmoq linklari (Telegram, Instagram, YouTube, TikTok)
- To'lov karta raqami
- Zaklad foizi

**Xizmatlar:**
- Tabriklar, bezaklar, sarpo-sandiq qo'shish
- Har bir xizmatga ko'p rasm qo'shish
- Narx, tavsif, tartib sozlash
- Faol/nofaol qilish

**Buyurtmalar:**
- Barcha buyurtmalarni ko'rish
- Holat o'zgartirish (Yangi → Tasdiqlangan → Bajarilgan)

---

## 🔗 Integratsiya sxemasi

```
Foydalanuvchi
    │
    ├── 🌐 Veb sayt ──────► Django DB ──► Admin Telegram Bot
    │                                           │
    └── 🤖 User Bot ─────► Django DB ──► Admin Telegram Bot
                                                │
                                        Admin buyurtmani
                                        ko'radi va tasdiqlaydi
```

---

## 🚀 Production (server)

```bash
pip install gunicorn
gunicorn asia_decor.wsgi:application --bind 0.0.0.0:8000

# Nginx config kerak bo'ladi
# systemd service fayllar botlar uchun
```

---

## 📞 Botlar buyruqlari

**User Bot:**
- `/start` — Bosh menyu
- Tabriklar, bezaklar ko'rish
- Buyurtma berish (to'liq flow)
- Kontaktlar va veb sayt

**Admin Bot:**
- `/start` — Admin menyu
- `/myid` — Telegram ID olish
- 📋 Barcha buyurtmalar
- 🆕 Yangi buyurtmalar
- 📊 Statistika
- ✅/🔄/✔️ Holat boshqaruvi
