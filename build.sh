#!/bin/bash
# ============================================================
# Render.com Build Script
# Render dashboard > Build Command: bash build.sh
# ============================================================
set -e

echo "📦 Pip packages o'rnatilmoqda..."
pip install -r requirements.txt

echo "🗑 Eski staticfiles tozalanmoqda..."
rm -rf staticfiles/

echo "📁 Static fayllar yig'ilmoqda..."
python manage.py collectstatic --noinput --clear

echo "📋 Yig'ilgan fayllar tekshirilmoqda..."
ls -la staticfiles/css/ 2>/dev/null && echo "✅ css/main.css topildi" || echo "⚠️ css papkasi topilmadi"

echo "🗄 Database migratsiyalar..."
python manage.py migrate --noinput

echo "✅ Build muvaffaqiyatli!"
