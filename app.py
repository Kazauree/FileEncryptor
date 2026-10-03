from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash, after_this_request
import os
import base64
import secrets
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, db

load_dotenv()

app = Flask(__name__)
app.secret_key = 'your-super-secret-key-change-in-production-2026'

IS_VERCEL = os.environ.get('VERCEL') == '1' or 'VERCEL_ENV' in os.environ
UPLOAD_FOLDER = '/tmp/uploads' if IS_VERCEL else 'uploads'
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ====================== FIREBASE ======================
try:
    if not firebase_admin._apps:
        if os.path.exists('firebase-key.json'):
            cred = credentials.Certificate('firebase-key.json')
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://fileencryption-69539-default-rtdb.firebaseio.com/'
            })
        elif os.environ.get('FIREBASE_KEY_JSON'):
            env_val = os.environ.get('FIREBASE_KEY_JSON').strip()
            if env_val.startswith('{'):
                key_data = json.loads(env_val)
            else:
                key_data = json.loads(base64.b64decode(env_val).decode('utf-8'))
            cred = credentials.Certificate(key_data)
            firebase_admin.initialize_app(cred, {
                'databaseURL': os.environ.get('FIREBASE_DATABASE_URL', 'https://fileencryption-69539-default-rtdb.firebaseio.com/')
            })
        else:
            print("Notice: Firebase key not found on disk or env. App running in local mode.")
except Exception as e:
    print(f"Firebase initialization warning: {e}")

# ====================== XOR ENCRYPTION ======================
def generate_key():
    return secrets.token_bytes(32)

def xor_encrypt_decrypt(data, key):
    return bytes(a ^ b for a, b in zip(data, key * (len(data) // len(key) + 1)))

import re
import json
import time
import socket as _socket

def sanitize_key(text):
    return re.sub(r'[\.\$\#\[\]\/]', '_', text)

LOCAL_DB_FILE = '/tmp/local_db.json' if IS_VERCEL else 'local_db.json'

# ====================== FAST NETWORK CHECK ======================
_firebase_status = {'online': None, 'checked_at': 0}

def is_firebase_available():
    """Quick 2-second probe cached for 30 seconds to avoid repeated slow timeouts."""
    if not firebase_admin._apps:
        return False
    now = time.time()
    if now - _firebase_status['checked_at'] < 30:
        return _firebase_status['online']
    try:
        _socket.create_connection(('fileencryption-69539-default-rtdb.firebaseio.com', 443), timeout=2).close()
        _firebase_status['online'] = True
    except (OSError, _socket.timeout, Exception):
        # On Vercel serverless, HTTPS works via Firebase Admin SDK REST even if raw sockets are sandboxed
        _firebase_status['online'] = True if IS_VERCEL else False
    _firebase_status['checked_at'] = now
    return _firebase_status['online']

def get_local_db():
    if os.path.exists(LOCAL_DB_FILE):
        try:
            with open(LOCAL_DB_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_local_db(db_data):
    try:
        with open(LOCAL_DB_FILE, 'w') as f:
            json.dump(db_data, f, indent=2)
    except Exception as e:
        print(f"Error saving local DB: {e}")

def save_file_record(user, file_node_id, record):
    # Always save locally first
    db_data = get_local_db()
    if user not in db_data:
        db_data[user] = {}
    db_data[user][file_node_id] = record
    save_local_db(db_data)
    # Try Firebase only if network is available
    if is_firebase_available():
        try:
            ref = db.reference(f'files/{user}')
            ref.child(file_node_id).set(record)
            return "Cloud & Local"
        except Exception as e:
            print(f"Firebase save failed: {e}")
    return "Local Storage"

def get_user_file_records(user):
    records = dict(get_local_db().get(user, {}))
    if is_firebase_available():
        try:
            remote_data = db.reference(f'files/{user}').get()
            if isinstance(remote_data, dict):
                records.update(remote_data)
        except Exception as e:
            print(f"Firebase query fallback: {e}")
    return records

def get_single_file_record(user, file_node_id):
    records = get_user_file_records(user)
    rec = records.get(file_node_id)
    if rec:
        return rec
    if is_firebase_available():
        try:
            remote_rec = db.reference(f'files/{user}/{file_node_id}').get()
            if isinstance(remote_rec, dict):
                return remote_rec
        except Exception as e:
            print(f"Firebase single query error: {e}")
    return None

def delete_file_record(user, file_node_id):
    # Remove from local DB
    db_data = get_local_db()
    if user in db_data and file_node_id in db_data[user]:
        del db_data[user][file_node_id]
        save_local_db(db_data)
    # Remove from Firebase only if online
    if is_firebase_available():
        try:
            db.reference(f'files/{user}/{file_node_id}').delete()
        except Exception as e:
            print(f"Firebase delete fallback: {e}")

from werkzeug.security import generate_password_hash, check_password_hash

def save_user(email, password):
    user_id = sanitize_key(email)
    password_hash = generate_password_hash(password)
    user_record = {
        'email': email,
        'password_hash': password_hash
    }
    # Always save locally first
    db_data = get_local_db()
    if 'users' not in db_data:
        db_data['users'] = {}
    db_data['users'][user_id] = user_record
    save_local_db(db_data)
    # Firebase only if online
    if is_firebase_available():
        try:
            db.reference(f'users/{user_id}').set(user_record)
        except Exception as e:
            print(f"Firebase user save fallback: {e}")

def get_user(email):
    user_id = sanitize_key(email)
    # Check local DB first (instant)
    db_data = get_local_db()
    user = db_data.get('users', {}).get(user_id)
    if user:
        return user
    # Only check Firebase if not found locally AND network is available
    if is_firebase_available():
        try:
            remote_user = db.reference(f'users/{user_id}').get()
            if remote_user and isinstance(remote_user, dict):
                if 'users' not in db_data:
                    db_data['users'] = {}
                db_data['users'][user_id] = remote_user
                save_local_db(db_data)
                return remote_user
        except Exception as e:
            print(f"Firebase get_user error: {e}")
    return None

def verify_user_password(email, password):
    user = get_user(email)
    if not user or 'password_hash' not in user:
        return False
    return check_password_hash(user['password_hash'], password)

def update_user_password(email, new_password):
    user_id = sanitize_key(email)
    new_hash = generate_password_hash(new_password)
    user_record = {
        'email': email,
        'password_hash': new_hash
    }
    # Always save locally first
    db_data = get_local_db()
    if 'users' not in db_data:
        db_data['users'] = {}
    db_data['users'][user_id] = user_record
    save_local_db(db_data)
    # Firebase only if online
    if is_firebase_available():
        try:
            db.reference(f'users/{user_id}').set(user_record)
        except Exception as e:
            print(f"Firebase update password fallback: {e}")

def delete_user(email):
    user_id = sanitize_key(email)
    db_data = get_local_db()
    if 'users' in db_data and user_id in db_data['users']:
        del db_data['users'][user_id]
        save_local_db(db_data)
    if is_firebase_available():
        try:
            db.reference(f'users/{user_id}').delete()
        except Exception as e:
            print(f"Firebase delete user fallback: {e}")

# ====================== PASSWORD STRENGTH ======================
def check_password_strength(password):
    """Returns (is_strong, message). Requires 8+ chars, upper, lower, digit, special."""
    if len(password) < 8:
        return False, 'Password must be at least 8 characters long.'
    if not any(c.isupper() for c in password):
        return False, 'Password must contain at least one uppercase letter (A-Z).'
    if not any(c.islower() for c in password):
        return False, 'Password must contain at least one lowercase letter (a-z).'
    if not any(c.isdigit() for c in password):
        return False, 'Password must contain at least one number (0-9).'
    if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?/~`' for c in password):
        return False, 'Password must contain at least one special character (!@#$%^&* etc).'
    return True, 'Strong password!'

# ====================== ROUTES ======================
@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Please fill in all fields!', 'error')
            return render_template('register.html')

        is_strong, strength_msg = check_password_strength(password)
        if not is_strong:
            flash(strength_msg, 'error')
            return render_template('register.html')

        if get_user(email):
            flash('Email is already registered! Please log in.', 'error')
            return redirect(url_for('login'))

        save_user(email, password)
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Please enter email and password!', 'error')
            return render_template('login.html')

        user = get_user(email)
        if not user:
            flash('Invalid email or password! Please check your credentials.', 'error')
            return render_template('login.html')

        if verify_user_password(email, password):
            session['user'] = email
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password! Please check your credentials.', 'error')
            return render_template('login.html')

    return render_template('login.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        if not email:
            flash('Please enter your email address!', 'error')
            return render_template('forgot_password.html')

        user = get_user(email)
        if user:
            session['reset_email'] = email
            flash('Email verified! Please enter your new password.', 'success')
            return redirect(url_for('reset_password'))
        else:
            flash('No account found with that email address!', 'error')
            return render_template('forgot_password.html')

    return render_template('forgot_password.html')

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if 'reset_email' not in session:
        flash('Please verify your email first!', 'error')
        return redirect(url_for('forgot_password'))

    email = session['reset_email']

    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not password or not confirm_password:
            flash('Please fill in all password fields!', 'error')
            return render_template('reset_password.html', email=email)

        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return render_template('reset_password.html', email=email)

        is_strong, strength_msg = check_password_strength(password)
        if not is_strong:
            flash(strength_msg, 'error')
            return render_template('reset_password.html', email=email)

        update_user_password(email, password)
        session.pop('reset_email', None)
        flash('Password updated successfully! Please log in with your new password.', 'success')
        return redirect(url_for('login'))

    return render_template('reset_password.html', email=email)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    user = sanitize_key(session['user'])

    # Upload File
    if request.method == 'POST':
        if 'file' not in request.files or not request.files['file'].filename:
            flash('No file selected! Please choose a file to upload.', 'error')
            return redirect(url_for('dashboard'))

        file = request.files['file']
        try:
            # Check file size safely
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)

            if file_size == 0:
                flash('Selected file is empty!', 'error')
                return redirect(url_for('dashboard'))

            if file_size > MAX_FILE_SIZE:
                flash('File too large! Maximum 10MB allowed.', 'error')
                return redirect(url_for('dashboard'))

            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)

            key = generate_key()
            with open(filepath, 'rb') as f:
                data = f.read()
            encrypted = xor_encrypt_decrypt(data, key)

            encoded_enc = base64.b64encode(encrypted).decode('utf-8')
            encoded_key = base64.b64encode(key).decode('utf-8')

            file_node_id = sanitize_key(file.filename)
            record = {
                'original_name': file.filename,
                'encrypted': encoded_enc,
                'key': encoded_key
            }

            storage_mode = save_file_record(user, file_node_id, record)

            if os.path.exists(filepath):
                os.remove(filepath)

            flash(f'File uploaded and encrypted successfully! ({storage_mode})', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            if 'filepath' in locals() and os.path.exists(filepath):
                os.remove(filepath)
            err_str = str(e)
            if 'NameResolutionError' in err_str or 'HTTPSConnectionPool' in err_str or 'Temporary failure' in err_str:
                flash('Network Offline: Firebase unreachable. Please check internet connection or retry!', 'error')
            else:
                flash(f'Upload failed: {err_str}', 'error')
            return redirect(url_for('dashboard'))

    # Load Files
    files = []
    try:
        user_records = get_user_file_records(user)
        for fname, info in user_records.items():
            if isinstance(info, dict):
                files.append({
                    'id': fname,
                    'name': info.get('original_name', fname),
                    'key': info.get('key', '')
                })
    except Exception as e:
        print(f"Error loading files: {e}")

    return render_template('dashboard.html', files=files)

@app.route('/delete/<filename>')
def delete_file(filename):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = sanitize_key(session['user'])
    delete_file_record(user, filename)
    flash('File deleted successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/download/<filename>', methods=['GET', 'POST'])
def download(filename):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = sanitize_key(session['user'])
    data = get_single_file_record(user, filename)
    
    if not data:
        flash('File not found!', 'error')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        try:
            user_key = request.form['key']
            provided_key = base64.b64decode(user_key)
            encrypted = base64.b64decode(data['encrypted'])
            decrypted = xor_encrypt_decrypt(encrypted, provided_key)
            
            dec_path = os.path.join(UPLOAD_FOLDER, data['original_name'])
            with open(dec_path, 'wb') as f:
                f.write(decrypted)

            @after_this_request
            def remove_file(response):
                try: os.remove(dec_path)
                except: pass
                return response

            return send_file(dec_path, as_attachment=True, download_name=data['original_name'])
        except Exception as e:
            flash('Invalid key or decryption error! Please try again.', 'error')
            return render_template('enter_key.html', filename=filename)
    
    return render_template('enter_key.html', filename=filename)
@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('welcome'))

if __name__ == '__main__':
    app.run(debug=True)
