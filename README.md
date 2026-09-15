# AlkhalilFa Crypto

منصة تعليمية تفاعلية باللغة العربية لشرح خوارزميات التشفير وتجربتها عمليًا من خلال واجهة ويب مبنية باستخدام Flask.

## المزايا

- موسوعة تعليمية للخوارزميات الكلاسيكية والحديثة.
- مختبر عملي للتشفير وفك التشفير مع عرض خطوات المعالجة.
- دعم Caesar وVigenere وAffine وAtbash وROT13 وPlayfair وMonoalphabetic.
- أمثلة تعليمية على DES و3DES وRSA وAES لتشفير الملفات.
- واجهة عربية متجاوبة مع عدة سمات بصرية.

## المتطلبات

- Python 3.10 أو أحدث.
- Flask.
- PyCryptodome.
- Gunicorn (للتشغيل على Linux والاستضافات السحابية).

## التثبيت والتشغيل

### Windows PowerShell

```powershell
git clone https://github.com/AlKhalilFA/crypto.git
cd crypto
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

### Linux أو macOS

```bash
git clone https://github.com/AlKhalilFA/crypto.git
cd crypto
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

بعد التشغيل افتح `http://127.0.0.1:5001/` في المتصفح.

### التشغيل على استضافة Linux

استخدم أمر التشغيل التالي في خدمات مثل Render:

```bash
gunicorn app:app
```

## المسارات

- `/` الموسوعة التعليمية.
- `/tool` المختبر العملي.
- `/about` صفحة التعريف بالمشروع.

## بنية المشروع

```text
crypto/
├── app.py                 # تطبيق Flask ومسارات الواجهة وواجهات المعالجة
├── requirements.txt       # اعتمادات Python
├── templates/
│   ├── index.html         # الموسوعة التعليمية
│   ├── tool.html          # المختبر العملي
│   └── about.html         # صفحة التعريف
├── static/
│   └── style.css          # التنسيقات المشتركة
├── .gitignore             # ملفات مستثناة من Git
└── README.md              # توثيق المشروع
```

## تنبيه أمني

هذا المشروع تعليمي. لا تستخدم DES أو 3DES أو مفاتيح RSA الموجودة داخل التطبيق لحماية بيانات حقيقية. يتم إنشاء مفتاح RSA جديد عند تشغيل التطبيق، كما أن الملفات المشفرة المؤقتة مخصصة للتجربة المحلية فقط.

## الترخيص

لم تتم إضافة ملف ترخيص إلى المستودع بعد. أضف ترخيصًا مناسبًا قبل إعادة استخدام المشروع أو توزيعه رسميًا.
