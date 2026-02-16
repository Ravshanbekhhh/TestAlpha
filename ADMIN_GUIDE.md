# ADMIN YARATISH VA KIRISH
# ========================

## Usul 1: API orqali (Eng oson)

1. Browser da oching: http://localhost:8000/docs

2. `/api/v1/auth/register` endpoint ni toping

3. "Try it out" tugmasini bosing

4. Request body ga quyidagini kiriting:
```json
{
  "username": "admin",
  "password": "admin123",
  "role": "admin"
}
```

5. "Execute" bosing

## Usul 2: Database ga to'g'ridan-to'g'ri qo'shish

PowerShell da:

```powershell
cd "C:\Users\ANUBIS PC\Desktop\Rash\backend"
python -c "import asyncio, uuid; from datetime import datetime; from app.database import AsyncSessionLocal; from app.models.admin import AdminUser; from passlib.context import CryptContext; pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto'); exec('async def create():\n async with AsyncSessionLocal() as db:\n  admin = AdminUser(id=uuid.uuid4(), username=\"admin\", password_hash=pwd_context.hash(\"admin123\"), created_at=datetime.utcnow())\n  db.add(admin)\n  await db.commit()\n  print(\"Admin created!\")\nasyncio.run(create())')"
```

## ADMIN PANEL ga Kirish

URL: http://localhost:8000/static/admin/

**Login:**
- Username: `admin`
- Password: `admin123`

## Test Yaratish

Admin panelda:

1. **"Tests" menyusini bosing**
2. **"Create New Test" tugmasini bosing**
3. Ma'lumotlarni kiriting:
   - Test Code: `MATH001` (o'quvchilar bu kodni botga kiritadi)
   - Title: "Matematika Test 1"
   - Description: "Test tavsifi"

4. **MCQ Javoblarini kiriting** (1-35 gacha):
   ```
   1: A
   2: B
   3: C
   ...
   35: D
   ```

5. **"Save Test" bosing**

## O'quvchi Test Ishlaydi

Telegram botda:
1. `/start`
2. "✅ Testni boshlash" tugmasini bosing
3. Test kodini yuboring: `MATH001`
4. Test sahifasi ochiladi - 60 daqiqa timer bilan!

## Natijalarni Ko'rish

Admin panelda:
1. "Results" sahifasiga o'ting
2. Barcha natijalar ko'rinadi
3. Yozma javoblarni qo'lda baholang
4. Excel yoki PDF export qiling
