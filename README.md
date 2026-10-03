# 🔐 FileEncryptor Flask

A secure, high-performance web application built with **Flask**, **Firebase Realtime Database**, and **XOR Cipher Encryption** for encrypting, storing, and decrypting files safely.

It features hybrid cloud & local offline storage fallback, fast network connectivity probing, real-time password strength validation, and account recovery workflows. Cross-platform compatible with **Windows**, **Linux**, and **macOS**.

---

## 🌟 Key Features

- 🔑 **End-to-End File Encryption**: Files are encrypted using a 256-bit key XOR cipher stream before storage and base64-encoded for database compatibility.
- ☁️ **Hybrid Cloud & Offline Storage**: Integrates with Firebase Realtime Database when online, and seamlessly falls back to a local JSON database (`local_db.json`) when offline.
- ⚡ **Fast Network Detection**: Built-in 2-second socket probe with 30-second TTL caching prevents long Firebase timeout delays when working offline.
- 🛡️ **Strong Password Enforcement**: Password validator requiring 8+ characters, uppercase, lowercase, numbers, and special characters, with a real-time UI strength meter.
- 🔑 **Account Recovery**: Forgot password flow allowing users to reset passwords securely upon email verification.
- 🎨 **Responsive UI & Offline CSS**: Designed with modern dark theme UI using Tailwind CSS with embedded standalone CSS fallbacks in `static/css/style.css`.
- 🧪 **Comprehensive Test Coverage**: Unit and integrated test suites covering auth, file uploads, password recovery, and Firebase operations.

---

## 🛠️ Tech Stack

- **Backend**: Python 3, Flask 3.0.3, Werkzeug Security
- **Cloud Database**: Firebase Admin SDK 6.5.0 (Firebase Realtime Database)
- **Local Fallback DB**: `local_db.json`
- **Encryption**: Python Secrets (32-byte key generation), XOR stream cipher, Base64 encoding
- **Frontend**: HTML5, Vanilla JavaScript, Tailwind CSS (with local CSS fallback)

---

## 🪟 Windows OS Installation & Quick Start

### Prerequisites
- Install **Python 3.8+** for Windows from [python.org](https://www.python.org/downloads/).
  *(Make sure to check the box **"Add Python to PATH"** during installation)*.

---

### Step 1: Open Terminal / Command Prompt
Open **Command Prompt (`cmd.exe`)** or **PowerShell** in your project folder:
```cmd
cd path\to\file-encryptor-flask
```

### Step 2: Create Virtual Environment
```cmd
python -m venv venv
```

### Step 3: Activate Virtual Environment

- **Command Prompt (`cmd.exe`)**:
  ```cmd
  venv\Scripts\activate
  ```
- **PowerShell**:
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
  *(If PowerShell displays a execution policy error, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first)*

- **Git Bash**:
  ```bash
  source venv/Scripts/activate
  ```

### Step 4: Install Dependencies
```cmd
pip install -r requirements.txt
```

### Step 5: Run the Application
```cmd
python app.py
```

Open your browser and navigate to **`http://127.0.0.1:5000`**.

---

## 🐧 Linux / macOS Quick Start

```bash
# 1. Create virtual environment
python3 -m venv venv

# 2. Activate virtual environment
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run application
python3 app.py
```

---

## 🧪 Running Tests (Windows & Linux)

To run automated test suites:

```cmd
# Test authentication & password reset flow
python test_auth.py

# Test file upload & size restrictions
python test_upload.py

# Test Firebase Realtime Database connection & CRUD operations
python test_firebase.py

# Run complete integrated end-to-end test suite
python test_integration.py
```

---

## 📖 User & Developer Guide

For detailed step-by-step user workflows, architecture explanations, and troubleshooting, refer to [GUIDE.md](file:///home/kazauree/file-encryptor-flask/GUIDE.md).

---

## 📄 License

This project is licensed under the MIT License.
