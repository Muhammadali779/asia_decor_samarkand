#!/bin/bash
# ============================================================
# Render.com Build Script
# Render dashboard > Build Command: ./build.sh
# ============================================================
set -e

echo "📦 Pip packages o'rnatilmoqda..."
pip install -r requirements.txt

echo "📁 Static fayllar yig'ilmoqda..."
python manage.py collectstatic --noinput

echo "🗄 Database migratsiyalar..."
python manage.py migrate --noinput

echo "✅ Build muvaffaqiyatli!"
