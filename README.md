# Asia Decor Samarkand

Django web application + Telegram bots.

## Render Deploy

**Build Command:** `./build.sh`

**Start Command (web + botlar birga):**
```
gunicorn asia_decor.wsgi:application & python admin_bot.py & python user_bot.py & wait
```

## Environment Variables (Render dashboard da sozlang)

- `DATABASE_URL` — PostgreSQL internal URL
- `SECRET_KEY` — Django secret key
- `USER_BOT_TOKEN` — Foydalanuvchi bot tokeni
- `ADMIN_BOT_TOKEN` — Admin bot tokeni
- `ADMIN_CHAT_ID` — Admin chat ID
- `ALLOWED_ADMIN_IDS` — Vergul bilan ajratilgan admin Telegram ID'lari
- `SITE_URL` — Sayt URL
- `DEBUG` — False (production)
