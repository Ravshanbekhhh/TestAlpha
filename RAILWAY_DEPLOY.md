# Railway Deployment Guide

## 🚂 Railway.app ga Deploy Qilish

Railway - bu zamonaviy cloud platform bo'lib, web ilovalarni oson deploy qilish imkonini beradi.

## 📋 Talab Qilinadigan Narsalar

1. **Railway Account**: [railway.app](https://railway.app) da ro'yxatdan o'ting
2. **GitHub Repository**: Kodingizni GitHub ga push qiling
3. **Telegram Bot Token**: @BotFather dan olingan token

## 🚀 Deploy Qilish Qadamlari

### 1. PostgreSQL Database Yaratish

Railway dashboard da:

1. **New Project** → **Provision PostgreSQL**
2. Database yaratiladi va `DATABASE_URL` avtomatik hosil bo'ladi
3. Database URL ni nusxalang (Variables tab da)

### 2. Backend Service Yaratish

1. **New Service** → **GitHub Repo** ni tanlang
2. Root path ni `backend` ga o'zgartiring:
   - Settings → Service Settings → Root Directory: `backend`

3. **Environment Variables** qo'shing (Variables tab):
   ```
   DATABASE_URL=postgresql://... (Railway PostgreSQL dan)
   SECRET_KEY=your-random-secret-key-min-32-characters
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=1440
   UPLOAD_DIR=uploads
   EXPORT_DIR=exports
   SESSION_DURATION_MINUTES=90
   CORS_ORIGINS=*
   ```

4. **Deploy** tugmasini bosing

5. Backend URL ni oling (Settings → Networking → Public Domain):
   - Masalan: `https://your-backend.railway.app`

### 3. Bot Service Yaratish

1. **New Service** → bir xil GitHub Repo
2. Root path ni `bot` ga o'zgartiring:
   - Settings → Service Settings → Root Directory: `bot`

3. **Environment Variables** qo'shing:
   ```
   BOT_TOKEN=your-telegram-bot-token
   BACKEND_URL=https://your-backend.railway.app
   WEB_APP_URL=https://your-backend.railway.app
   ```

4. **Deploy** tugmasini bosing

### 4. Database Initialize Qilish

Backend service deploy bo'lgandan keyin:

1. Railway dashboard → Backend service → **Variables** tab
2. Temporary variable qo'shing:
   ```
   INIT_DB=true
   ```

3. Yoki manual ravishda SQL query ishga tushiring

**Backend shell orqali** (Settings → Service → Open Shell):
```bash
python init_db.py
```

### 5. Admin User Yaratish

Backend URL orqali API call:

```bash
curl -X POST https://your-backend.railway.app/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "YourSecurePassword123",
    "role": "admin"
  }'
```

Yoki Postman/Thunder Client ishlatib:
- URL: `https://your-backend.railway.app/api/v1/auth/register`
- Method: POST
- Body (JSON):
  ```json
  {
    "username": "admin",
    "password": "YourSecurePassword123",
    "role": "admin"
  }
  ```

## 🔍 Tekshirish

### Health Check
```
https://your-backend.railway.app/health
```

Javob:
```json
{"status": "healthy"}
```

### API Docs
```
https://your-backend.railway.app/docs
```

### Admin Panel
```
https://your-backend.railway.app/static/admin/
```

### Test Student Interface
1. Telegram botni /start qiling
2. /register orqali ro'yxatdan o'ting
3. Test code kiriting
4. Link ochiladi: `https://your-backend.railway.app/static/student/...`

## 📊 Logs Ko'rish

Railway dashboard da har bir service uchun logs mavjud:
- **Backend Service** → View Logs
- **Bot Service** → View Logs
- **PostgreSQL** → View Logs

## 🔧 Troubleshooting

### Bot ishlamayapti?
Logs da tekshiring:
```
railway logs --service bot
```

Environment variables to'g'riligini tekshiring:
- `BOT_TOKEN` - to'g'ri token
- `BACKEND_URL` - backend URL (https bilan)

### Database connection error?
- `DATABASE_URL` to'g'ri formatda ekanligini tekshiring
- PostgreSQL service running ekanligini tekshiring

### Static files yuklanmayapti?
- Backend service da `static` folder borligini tekshiring
- Railway da `UPLOAD_DIR` va `EXPORT_DIR` o'rnatilganligini tekshiring

## 💡 Railway Features

### Auto Deploy
Har safar GitHub ga push qilganingizda avtomatik deploy bo'ladi.

### Environment Variables
Dashboard da Variables tab orqali boshqaring.

### Custom Domain
Settings → Networking → Custom Domain qo'shishingiz mumkin.

### Scaling
Railway avtomatik scaling qiladi trafik oshganda.

### Monitoring
Built-in metrics va logs mavjud.

## 💰 Cost

- **Free Tier**: 
  - $5/month credit (500 hours)
  - PostgreSQL included
  - Bir nechta service

- **Pro Plan**: 
  - $20/month
  - Unlimited projects
  - Priority support

## 🔐 Production Best Practices

1. **Secret Key**: Kuchli, random secret key ishlating
2. **Environment Variables**: Hech qachon kodga qo'ymang
3. **CORS**: Production da `CORS_ORIGINS` ni aniq domain ga o'zgartiring
4. **Database Backup**: Railway auto backup qiladi, lekin manual ham oling
5. **Monitoring**: Logs va metrics kuzatib turing
6. **SSL**: Railway avtomatik HTTPS beradi

## 📱 Mobile Access

Telegram bot orqali:
1. Botni /start qiling
2. Login qiling
3. Test kodini kiriting
4. Mobile browserda test ochiladi

## 🎯 Next Steps

1. Custom domain qo'shing
2. Production CORS sozlang
3. Database backup strategiya yarating
4. Monitoring va alerting sozlang
5. Rate limiting qo'shing (opsional)

---

## ❓ Yordam

Railway documentation: https://docs.railway.app

Support: Railway Discord community

---

**Muvaffaqiyatli deploy!** 🚀
