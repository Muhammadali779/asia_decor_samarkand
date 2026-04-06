#!/bin/bash
# Asia Decor - Ishga tushirish skripti
set -e

echo "🌟 Asia Decor Samarkand - O'rnatish..."

# .env yaratish
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  .env fayli yaratildi. Iltimos tokenlarni kiriting!"
fi

# Virtual env
python3 -m venv venv
source venv/bin/activate

# Kutubxonalar
pip install -r requirements.txt

# DB migrations
python manage.py makemigrations
python manage.py migrate

# Static fayllar
python manage.py collectstatic --noinput

# Superuser
echo "👤 Admin foydalanuvchi yarating:"
python manage.py createsuperuser

echo ""
echo "✅ O'rnatish tugadi!"
echo ""
echo "Ishga tushirish:"
echo "  source venv/bin/activate"
echo "  python manage.py runserver"
echo ""
echo "Admin panel: http://localhost:8000/admin/"
