# AlkhalilFa

منصة تعليمية تفاعلية لشرح خوارزميات التشفير وتجربتها عمليًا.

## البنية

```text
Alkhalil_FA/
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
