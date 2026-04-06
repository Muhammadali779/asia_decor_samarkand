"""
Render.com yoki CI/CD da superuser yaratish uchun.
Foydalanish:
  python manage.py create_superuser_env

Environment variables (.env yoki Render dashboard):
  DJANGO_SUPERUSER_USERNAME=admin
  DJANGO_SUPERUSER_PASSWORD=yourpassword
  DJANGO_SUPERUSER_EMAIL=admin@example.com
"""
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "ENV o'zgaruvchilardan superuser yaratadi (Render uchun)"

    def handle(self, *args, **options):
        User = get_user_model()
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', '')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')

        if not password:
            self.stderr.write("❌ DJANGO_SUPERUSER_PASSWORD env o'zgaruvchisi topilmadi!")
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(f"ℹ️  '{username}' allaqachon mavjud — o'tkazib yuborildi.")
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )
        self.stdout.write(self.style.SUCCESS(f"✅ Superuser '{username}' yaratildi!"))
