# News Bot - بوت أخبار الأنمي والألعاب

بوت ينشر أخبار الأنمي والألعاب تلقائياً كل 15 دقيقة إلى قناة تيليجرام.

## طريقة الرفع إلى GitHub

### 1. سجل في GitHub
- روح https://github.com/signup
- سو حساب جديد

### 2. سو مستودع (Repository) جديد
- اضغط على "+" فوق 👆
- اسم المستودع: `news-bot`
- خلّيه **Public**
- لا تختار anything else, اضغط "Create repository"

### 3. ارفع الملفات
افتح PowerShell والصق الأوامر:

```powershell
cd C:\Users\iraq\Desktop\news-bot-py
git init
git add .
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/your-username/news-bot.git
git push -u origin main
```

(غيّر `your-username` لاسم مستخدمك في GitHub)

### 4. ضيف توكن البوت
في صفحة المستودع على GitHub:
- Settings → Secrets and variables → Actions
- New repository secret
- Name: `TELEGRAM_BOT_TOKEN`
- Value: `8387787315:AAHVhFQt7Wv9J9JsCA_CchdwKY21fg6XTCU`
- Add secret

### 5. فعّل الـ Actions
روح لـ Actions tab ✅
رح يشتغل تلقائياً كل 15 دقيقة
