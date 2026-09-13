# Alkhalil_FA

هذا المستودع يحتوي على أكثر من مشروع مستقل. كل مشروع موجود داخل مجلد منفصل تحت `projects/`، وله ملف متطلبات وتوثيق خاص به حتى لا تتداخل الملفات أو المكتبات بين المشاريع.

## المشاريع

### 1. مشروع التشفير

المسار: `projects/crypto/`

منصة Flask تعليمية لتجربة خوارزميات التشفير وتشفير الملفات باستخدام AES.

التشغيل من جذر المستودع:

```powershell
.\.venv\Scripts\python.exe -m pip install -r projects\crypto\requirements.txt
.\.venv\Scripts\python.exe projects\crypto\app.py
```

ثم افتح: `http://127.0.0.1:5001/`

### 2. مشروع معالجة الصور

المسار: `projects/image-processing/`

هذا مجلد مستقل مخصص لإضافة مشروع معالجة الصور. ضع داخله ملف التشغيل، مجلد القوالب، الملفات الثابتة، وملف `requirements.txt` الخاص به فقط.

## قاعدة تنظيم المشاريع

- لا تضع ملفات مشروع جديد في جذر المستودع.
- أنشئ مجلدًا جديدًا داخل `projects/` لكل مشروع مستقل.
- اجعل لكل مشروع `README.md` و`requirements.txt` خاصين به.
- استخدم أسماء مجلدات واضحة باللغة الإنجليزية لتفادي مشاكل المسارات.
- نفّذ أوامر Git من جذر المستودع، ثم ارفع التغييرات بــ commit مستقل.

## بنية المستودع

```text
Alkhalil_FA/
├── projects/
│   ├── crypto/
│   └── image-processing/
├── .gitignore
└── README.md
```# AlkhalilFa

منصة تعليمية تفاعلية لشرح خوارزميات التشفير وتجربتها عمليًا.

## البنية

```text
crepto/
├── app.py                 # تطبيق Flask ومسارات API
├── requirements.txt       # الاعتمادات
├── templates/
│   ├── index.html         # الموسوعة التعليمية
│   ├── tool.html          # المختبر العملي
│   └── about.html         # صفحة من نحن
├── static/
│   └── style.css          # التنسيقات المشتركة
├── .gitignore
└── README.md
```

## التشغيل

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

ثم افتح:

- `http://127.0.0.1:5001/` للموسوعة.
- `http://127.0.0.1:5001/tool` للمختبر.
- `http://127.0.0.1:5001/about` لصفحة من نحن.

## الخوارزميات المتاحة

Caesar، Vigenere، Affine، Atbash، ROT13، Playfair، DES، 3DES، Monoalphabetic، RSA، وAES لخزنة الملفات.

> DES و3DES وRSA في هذا المشروع موجهة للتعلم. لا تستخدم DES أو 3DES لحماية بيانات حقيقية.
