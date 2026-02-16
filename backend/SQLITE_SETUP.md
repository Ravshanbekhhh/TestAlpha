# SQLite bilan Localhost Setup

PostgreSQL o'rnatmasdan SQLite ishlatamiz!

## 1. Dependencies O'rnatish

```powershell
cd "C:\Users\ANUBIS PC\Desktop\Rash\backend"
pip install -r requirements.txt
```

## 2. Database Yaratish

```powershell
python init_db.py
```

Database fayl yaratiladi: `testing_platform.db`

## 3. Backend Ishga Tushirish

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend: http://localhost:8000 ✅

## 4. Bot Ishga Tushirish (Yangi Terminal)

```powershell
cd "C:\Users\ANUBIS PC\Desktop\Rash\bot"
pip install -r requirements.txt
python bot.py
```

## 5. Admin Yaratish

Browser: http://localhost:8000/docs

`/api/v1/auth/register` endpoint:
```json
{
  "username": "admin",
  "password": "admin123",
  "role": "admin"
}
```

## ✅ Tayyor!

- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Admin Panel: http://localhost:8000/static/admin/
- Bot: @IntervIew21_bot
