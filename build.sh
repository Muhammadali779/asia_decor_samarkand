#!/bin/bash
# ============================================================
# Render.com Build Script
# Render dashboard > Build Command: ./build.sh
# ============================================================
set -e

echo "📦 Pip packages o'rnatilmoqda..."
pip install -r requirements.txt

echo "🗑 Eski staticfiles tozalanmoqda..."
rm -rf staticfiles/

echo "📁 Static fayllar yig'ilmoqda..."
python manage.py collectstatic --noinput --clear

echo "🗄 Database migratsiyalar..."
python manage.py migrate --noinput

echo "✅ Build muvaffaqiyatli!"
