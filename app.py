from flask import Flask, render_template, request, jsonify, send_file
import base64, json, math, os, re, secrets, tempfile, time
from Crypto.Cipher import AES, DES, DES3
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Util.Padding import pad, unpad

app = Flask(__name__)

TEMP_FILE_TTL = 180
TEMP_FILE_DIR = os.path.join(tempfile.gettempdir(), 'crepto-aes-files')
os.makedirs(TEMP_FILE_DIR, exist_ok=True)
RSA_KEY = RSA.generate(2048)


def is_ascii_letter(char):
    return ('A' <= char <= 'Z') or ('a' <= char <= 'z')

# --- منطق خوارزمية قيصر ---
def caesar_logic(text, key, mode):
    res, steps = "", []
    shift = int(key) if mode == 'encrypt' else -int(key)
    for char in text:
        if is_ascii_letter(char):
            start = ord('A') if char.isupper() else ord('a')
            p = ord(char) - start
            c = (p + shift) % 26
            new_char = chr(c + start)
            res += new_char
            op = '+' if mode == 'encrypt' else '-'
            steps.append(f"'{char}'({p}) {op} {abs(int(key))} mod 26 = {c} → '{new_char}'")
        else: res += char
    return res, steps

# --- منطق خوارزمية فيجنير ---
def vigenere_logic(text, key_str, mode):
    res, steps = "", []
    key = str(key_str).upper()
    if not key or not key.isascii() or not key.isalpha():
        return None, ["يجب إدخال كلمة مفتاحية إنجليزية فقط"]
    k_idx = 0
    for char in text:
        if is_ascii_letter(char):
            start = ord('A') if char.isupper() else ord('a')
            p = ord(char) - start
            k_char = key[k_idx % len(key)]
            k_val = ord(k_char) - ord('A')
            c = (p + k_val) % 26 if mode == 'encrypt' else (p - k_val) % 26
            new_char = chr(c + start)
            res += new_char
            op = '+' if mode == 'encrypt' else '-'
            steps.append(f"'{char}'({p}) {op} '{k_char}'({k_val}) mod 26 = {c} → '{new_char}'")
            k_idx += 1
        else: res += char
    return res, steps

# --- منطق خوارزمية أفاين ---
def affine_logic(text, a, b, mode):
    res, steps = "", []
    try:
        a, b = int(a), int(b)
        if math.gcd(a, 26) != 1: return None, ["خطأ رياضي: يجب أن يكون gcd(a, 26) = 1"]
        a_inv = pow(a, -1, 26) if mode == 'decrypt' else None
        
        for char in text:
            if is_ascii_letter(char):
                start = ord('A') if char.isupper() else ord('a')
                x = ord(char) - start
                if mode == 'encrypt':
                    c = (a * x + b) % 26
                    steps.append(f"({a}*{x} + {b}) mod 26 = {c} → '{chr(c+start)}'")
                else:
                    c = (a_inv * (x - b)) % 26
                    steps.append(f"{a_inv}*({x}-{b}) mod 26 = {c} → '{chr(c+start)}'")
                res += chr(c + start)
            else: res += char
        return res, steps
    except ValueError: return None, ["تأكد من إدخال قيم عددية صحيحة"]

# --- منطق Atbash (عكس الحروف) ---
def atbash_logic(text):
    # A->Z, B->Y ...
    res, steps = "", []
    lookup = "ZYXWVUTSRQPONMLKJIHGFEDCBA"
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    for char in text:
        if is_ascii_letter(char):
            is_upper = char.isupper()
            idx = alphabet.find(char.upper())
            new_char = lookup[idx]
            res += new_char if is_upper else new_char.lower()
            steps.append(f"Reverse: {char} ↔ {new_char}")
        else:
            res += char
    return res, steps

# --- منطق ROT13 ---
def rot13_logic(text):
    # Caesar shift 13, self-inverse
    res, steps = "", []
    shift = 13
    for char in text:
        if is_ascii_letter(char):
            start = ord('A') if char.isupper() else ord('a')
            c = (ord(char) - start + shift) % 26
            new_char = chr(c + start)
            res += new_char
            steps.append(f"ROT13: {char} → {new_char}")
        else:
            res += char
    return res, steps


def monoalphabetic_logic(text, key_str, mode):
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    key = str(key_str).upper()
    if len(key) != 26 or set(key) != set(alphabet):
        return None, ["مفتاح Monoalphabetic يجب أن يحتوي على 26 حرفًا إنجليزيًا مختلفة"]
    mapping = dict(zip(alphabet, key))
    if mode == 'decrypt':
        mapping = {value: source for source, value in mapping.items()}
    result, steps = [], []
    for char in text:
        upper = char.upper()
        if upper in mapping:
            converted = mapping[upper]
            result.append(converted if char.isupper() else converted.lower())
            steps.append(f"'{char}' → '{converted if char.isupper() else converted.lower()}'")
        else:
            result.append(char)
    return ''.join(result), steps

# --- منطق Playfair (مصفوفة 5x5) ---
def playfair_logic(text, key, mode):
    key = str(key).upper()
    if not key or not key.isascii() or not key.isalpha():
        return None, ["يجب إدخال كلمة مفتاحية إنجليزية فقط"]
    key = "".join(dict.fromkeys(key.replace("J", "I") + "ABCDEFGHIKLMNOPQRSTUVWXYZ"))
    matrix = [key[i:i+5] for i in range(0, 25, 5)]

    original_text = ''.join(char for char in text if is_ascii_letter(char))
    case_flags = [char.isupper() for char in original_text]
    text = original_text.upper().replace("J", "I")
    if not text:
        return None, ["يجب إدخال نص إنجليزي يحتوي على حروف"]

    if mode == 'encrypt':
        pairs = []
        i = 0
        while i < len(text):
            first = text[i]
            if i + 1 >= len(text):
                pairs.append((first, 'Q' if first == 'X' else 'X'))
                i += 1
            elif first == text[i + 1]:
                pairs.append((first, 'Q' if first == 'X' else 'X'))
                i += 1
            else:
                pairs.append((first, text[i + 1]))
                i += 2
    else:
        if len(text) % 2:
            return None, ["النص المشفر في Playfair يجب أن يحتوي على عدد زوجي من الحروف"]
        pairs = [(text[i], text[i + 1]) for i in range(0, len(text), 2)]
        
    res, steps = "", ["Generate 5x5 Matrix from Key"]
    
    def find_pos(c):
        idx = key.find(c)
        if idx == -1:
            raise ValueError(f"الحرف غير مدعوم في Playfair: {c}")
        return idx // 5, idx % 5

    for a, b in pairs:
        r1, c1 = find_pos(a)
        r2, c2 = find_pos(b)
        
        if r1 == r2: # Same Row
            shift = 1 if mode == 'encrypt' else -1
            na = matrix[r1][(c1 + shift) % 5]
            nb = matrix[r2][(c2 + shift) % 5]
        elif c1 == c2: # Same Column
            shift = 1 if mode == 'encrypt' else -1
            na = matrix[(r1 + shift) % 5][c1]
            nb = matrix[(r2 + shift) % 5][c2]
        else: # Rectangle
            na = matrix[r1][c2]
            nb = matrix[r2][c1]
            
        res += na + nb
        steps.append(f"Pair ({a},{b}) → ({na},{nb})")
        
    res = ''.join(
        char.upper() if index >= len(case_flags) or case_flags[index] else char.lower()
        for index, char in enumerate(res)
    )
    return res, steps

# --- منطق خوارزمية DES (النصوص) ---
def des_logic(text, key_str, mode):
    key_str = str(key_str)
    if len(key_str) != 8 or not key_str.isascii():
        raise ValueError("مفتاح DES يجب أن يتكون من 8 رموز إنجليزية أو أرقام")
    key = key_str.encode('ascii')
    if mode == 'encrypt':
        cipher = DES.new(key, DES.MODE_CBC)
        padded = pad(text.encode('utf-8'), DES.block_size)
        encrypted = cipher.iv + cipher.encrypt(padded)
        return base64.b64encode(encrypted).decode('utf-8'), ["تحويل لكتل 64-بت", "تطبيق شبكة فايستل", "16 دورة تبديل"]
    else:
        raw = base64.b64decode(text, validate=True)
        if len(raw) <= 8 or len(raw[8:]) % DES.block_size:
            raise ValueError("النص المشفر غير صالح")
        iv, data = raw[:8], raw[8:]
        cipher = DES.new(key, DES.MODE_CBC, iv=iv)
        return unpad(cipher.decrypt(data), DES.block_size).decode('utf-8'), ["عكس جولات S-Boxes"]


def des3_logic(text, key_str, mode):
    key = str(key_str).encode('ascii') if str(key_str).isascii() else b''
    if len(key) != 24:
        raise ValueError("مفتاح 3DES يجب أن يتكون من 24 رمزًا إنجليزيًا أو رقمًا")
    try:
        key = DES3.adjust_key_parity(key)
        if mode == 'encrypt':
            cipher = DES3.new(key, DES3.MODE_CBC)
            encrypted = cipher.iv + cipher.encrypt(pad(text.encode('utf-8'), DES3.block_size))
            return base64.b64encode(encrypted).decode('ascii'), ["تقسيم إلى كتل 64-بت", "تشفير DES ثلاثي", "CBC مع IV عشوائي"]
        raw = base64.b64decode(text, validate=True)
        if len(raw) <= DES3.block_size or len(raw[8:]) % DES3.block_size:
            raise ValueError("النص المشفر 3DES غير صالح")
        cipher = DES3.new(key, DES3.MODE_CBC, iv=raw[:8])
        return unpad(cipher.decrypt(raw[8:]), DES3.block_size).decode('utf-8'), ["عكس مراحل DES الثلاثية", "إزالة الحشو"]
    except (ValueError, UnicodeDecodeError) as error:
        raise ValueError("النص أو مفتاح 3DES غير صالح") from error


def rsa_logic(text, mode):
    try:
        if mode == 'encrypt':
            if len(text.encode('utf-8')) > 190:
                raise ValueError("RSA-OAEP يدعم نصًا يصل إلى 190 بايت فقط؛ استخدم AES أو 3DES للنصوص الكبيرة")
            cipher = PKCS1_OAEP.new(RSA_KEY.publickey(), hashAlgo=SHA256)
            encrypted = cipher.encrypt(text.encode('utf-8'))
            return base64.b64encode(encrypted).decode('ascii'), ["استخدام المفتاح العام", "RSA-OAEP مع SHA-256", "تحويل الناتج إلى Base64"]
        raw = base64.b64decode(text, validate=True)
        cipher = PKCS1_OAEP.new(RSA_KEY, hashAlgo=SHA256)
        return cipher.decrypt(raw).decode('utf-8'), ["استخدام المفتاح الخاص", "التحقق من OAEP", "استعادة النص الأصلي"]
    except (ValueError, UnicodeDecodeError, base64.binascii.Error) as error:
        raise ValueError("نص RSA غير صالح أو يتجاوز الحد المسموح") from error

# --- منطق AES للملفات: تخزين مؤقت على القرص ومعالجة على دفعات ---
def get_aes_key(key_str):
    key = str(key_str).encode('utf-8')
    if len(key) != 16:
        raise ValueError("يجب أن يكون مفتاح AES بطول 16 بايت")
    return key


def cleanup_temp_files():
    cutoff = time.time() - TEMP_FILE_TTL
    for name in os.listdir(TEMP_FILE_DIR):
        path = os.path.join(TEMP_FILE_DIR, name)
        try:
            if os.path.isfile(path) and os.path.getmtime(path) < cutoff:
                os.remove(path)
        except OSError:
            app.logger.warning("Could not remove temporary file: %s", path)


def temp_paths(token):
    return (
        os.path.join(TEMP_FILE_DIR, f'{token}.bin'),
        os.path.join(TEMP_FILE_DIR, f'{token}.json')
    )


def encrypt_file_to_path(file_storage, output_path, key):
    cipher = AES.new(key, AES.MODE_CBC)
    pending = b''
    with open(output_path, 'wb') as output:
        output.write(cipher.iv)
        while True:
            chunk = file_storage.stream.read(1024 * 1024)
            if not chunk:
                break
            pending += chunk
            writable_length = max(0, (len(pending) - AES.block_size) // AES.block_size * AES.block_size)
            if writable_length:
                output.write(cipher.encrypt(pending[:writable_length]))
                pending = pending[writable_length:]
        output.write(cipher.encrypt(pad(pending, AES.block_size)))


def decrypt_file_to_path(input_path, output_path, key):
    with open(input_path, 'rb') as source:
        iv = source.read(AES.block_size)
        if len(iv) != AES.block_size:
            raise ValueError("الملف المشفر غير صالح")
        cipher = AES.new(key, AES.MODE_CBC, iv=iv)
        pending = b''
        with open(output_path, 'wb') as output:
            while True:
                chunk = source.read(1024 * 1024)
                if not chunk:
                    break
                pending += chunk
                writable_length = max(0, (len(pending) - AES.block_size) // AES.block_size * AES.block_size)
                if writable_length:
                    output.write(cipher.decrypt(pending[:writable_length]))
                    pending = pending[writable_length:]
            if not pending or len(pending) % AES.block_size:
                raise ValueError("الملف المشفر غير صالح")
            output.write(unpad(cipher.decrypt(pending), AES.block_size))

@app.route('/')
def index(): return render_template('index.html')

@app.route('/tool')
def tool(): return render_template('tool.html')

@app.route('/about')
def about(): return render_template('about.html')

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    try:
        if not isinstance(data, dict):
            return jsonify({'error': "بيانات الطلب غير صحيحة"}), 400

        algo, mode, text = str(data['algo']).lower(), data['mode'], data['text']
        if algo == '3des':
            algo = 'des3'
        if mode not in ('encrypt', 'decrypt'):
            return jsonify({'error': "وضع التشغيل غير صحيح"}), 400
        if not isinstance(text, str) or not text:
            return jsonify({'error': "يجب إدخال نص لمعالجته"}), 400

        if algo == 'caesar': res, steps = caesar_logic(text, data['key1'], mode)
        elif algo == 'vigenere': res, steps = vigenere_logic(text, data['key1_str'], mode)
        elif algo == 'affine': res, steps = affine_logic(text, data['key1'], data['key2'], mode)
        elif algo == 'atbash': res, steps = atbash_logic(text)
        elif algo == 'rot13': res, steps = rot13_logic(text)
        elif algo == 'playfair': res, steps = playfair_logic(text, data['key1_str'], mode)
        elif algo == 'des': res, steps = des_logic(text, data['key1_str'], mode)
        elif algo == 'monoalphabetic': res, steps = monoalphabetic_logic(text, data['key1_str'], mode)
        elif algo == 'des3': res, steps = des3_logic(text, data['key1_str'], mode)
        elif algo == 'rsa': res, steps = rsa_logic(text, mode)
        else:
            return jsonify({'error': "الخوارزمية غير مدعومة"}), 400
        if res is None: return jsonify({'error': steps[0]}), 400
        return jsonify({'result': res, 'steps': steps})
    except (KeyError, TypeError, ValueError, base64.binascii.Error) as e:
        return jsonify({'error': f"تأكد من صحة المدخلات: {e}"}), 400
    except Exception:
        app.logger.exception("Error while processing encryption request")
        return jsonify({'error': "حدث خطأ أثناء معالجة الطلب"}), 500

@app.route('/encrypt-file', methods=['POST'])
def handle_file():
    cleanup_temp_files()
    file = request.files.get('file')
    key = request.form.get('key', '')
    mode = request.form.get('mode')
    if mode not in ('encrypt', 'decrypt'):
        return jsonify({'error': "وضع التشغيل غير صحيح"}), 400

    try:
        aes_key = get_aes_key(key)
        token = request.form.get('token', '')
        if mode == 'encrypt':
            if file is None or not file.filename:
                return jsonify({'error': "يجب اختيار ملف"}), 400
            if not re.fullmatch(r'[a-f0-9]{32}', token or ''):
                token = secrets.token_hex(16)
            encrypted_path, metadata_path = temp_paths(token)
            encrypt_file_to_path(file, encrypted_path, aes_key)
            with open(metadata_path, 'w', encoding='utf-8') as metadata:
                json.dump({'filename': os.path.basename(file.filename)}, metadata)
            return jsonify({
                'token': token,
                'download_url': f'/download-temp/{token}',
                'filename': f'encrypted_{os.path.basename(file.filename)}',
                'expires_in': TEMP_FILE_TTL
            })

        if not re.fullmatch(r'[a-f0-9]{32}', token or ''):
            return jsonify({'error': "لا يوجد ملف مشفر محفوظ لفك تشفيره"}), 400
        encrypted_path, metadata_path = temp_paths(token)
        if not os.path.isfile(encrypted_path):
            return jsonify({'error': "انتهت صلاحية الملف المشفر، يرجى تشفيره من جديد"}), 410
        with open(metadata_path, 'r', encoding='utf-8') as metadata:
            original_filename = os.path.basename(json.load(metadata)['filename'])
        decrypted_path = os.path.join(TEMP_FILE_DIR, f'{secrets.token_hex(16)}.decrypted')
        decrypt_file_to_path(encrypted_path, decrypted_path, aes_key)
    except (OSError, ValueError, KeyError, json.JSONDecodeError):
        return jsonify({'error': "الملف أو المفتاح غير صالح"}), 400

    def remove_temporary_files():
        for path in (encrypted_path, metadata_path, decrypted_path):
            try:
                if os.path.exists(path):
                    os.remove(path)
            except OSError:
                app.logger.warning("Could not remove temporary file: %s", path)

    response = send_file(decrypted_path, download_name=f'decrypted_{original_filename}', as_attachment=True)
    response.call_on_close(remove_temporary_files)
    return response


@app.route('/download-temp/<token>')
def download_temp_file(token):
    cleanup_temp_files()
    if not re.fullmatch(r'[a-f0-9]{32}', token):
        return jsonify({'error': "رابط الملف غير صالح"}), 400
    encrypted_path, metadata_path = temp_paths(token)
    if not os.path.isfile(encrypted_path):
        return jsonify({'error': "انتهت صلاحية الملف المشفر"}), 410
    try:
        with open(metadata_path, 'r', encoding='utf-8') as metadata:
            original_filename = os.path.basename(json.load(metadata)['filename'])
    except (OSError, KeyError, json.JSONDecodeError):
        return jsonify({'error': "بيانات الملف غير صالحة"}), 410
    return send_file(encrypted_path, download_name=f'encrypted_{original_filename}', as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', '5001'))
    app.run(host='127.0.0.1', port=port, debug=True, use_reloader=False)