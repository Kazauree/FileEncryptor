# 📖 FileEncryptor Detailed User & Developer Guide

Welcome to the **FileEncryptor** User & Developer Guide. This document provides step-by-step instructions for using all application features, alongside an explanation of the underlying system architecture, encryption mechanisms, cross-platform deployment (Windows, Linux, macOS), and troubleshooting procedures.

---

## 🎯 Table of Contents
1. [Windows OS Setup Guide](#-windows-os-setup-guide)
2. [User Guide](#-user-guide)
   - [1. Creating an Account](#1-creating-an-account)
   - [2. Logging In](#2-logging-in)
   - [3. Uploading & Encrypting Files](#3-uploading--encrypting-files)
   - [4. Dashboard & Managing Files](#4-dashboard--managing-files)
   - [5. Decrypting & Downloading Files](#5-decrypting--downloading-files)
   - [6. Account Password Recovery](#6-account-password-recovery)
3. [System Architecture & Features](#-system-architecture--features)
   - [Encryption Mechanism](#encryption-mechanism)
   - [Hybrid Storage & Offline Resiliency](#hybrid-storage--offline-resiliency)
   - [Fast Network Probing](#fast-network-probing)
4. [Troubleshooting & FAQs](#-troubleshooting--faqs)

---

## 🪟 Windows OS Setup Guide

### 1. Install Python on Windows
1. Download Python 3.8 or newer from [python.org](https://www.python.org/downloads/).
2. Run the installer and **MUST check "Add Python to PATH"** on the first screen.

### 2. Running on Windows via Command Prompt (CMD)
```cmd
cd path\to\file-encryptor-flask
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### 3. Running on Windows via PowerShell
```powershell
cd path\to\file-encryptor-flask
python -m venv venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

### 4. Running on Windows via Git Bash
```bash
cd /c/path/to/file-encryptor-flask
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
python app.py
```

Once started, open your web browser (Chrome, Edge, Firefox) and go to:
**`http://127.0.0.1:5000`**

---

## 👤 User Guide

### 1. Creating an Account
1. Navigate to the landing page and click **Get Started** or go directly to `/register`.
2. Enter your email address.
3. Enter a password. The system enforces strong password security:
   - Must be at least **8 characters long**
   - Must contain an **uppercase letter (A-Z)**
   - Must contain a **lowercase letter (a-z)**
   - Must contain a **number (0-9)**
   - Must contain a **special character (`!@#$%^&*`)**
4. Observe the real-time strength meter bar and checklist. The **Register** button will unlock once all 5 requirements are met.
5. Click **Register** to complete account creation.

### 2. Logging In
1. Go to `/login`.
2. Enter your registered email address and password.
3. Click **Log In**. Upon successful verification, you will be redirected to your personal **Dashboard**.

### 3. Uploading & Encrypting Files
1. On the **Dashboard**, click **Choose File** (or drag & drop a file up to 10 MB).
2. The selected file name will display next to the button.
3. Click **Encrypt & Upload File**.
4. The system generates a unique **32-byte (256-bit) encryption key**, encrypts your file using XOR stream ciphering, base64 encodes the payload, and saves the file record.
5. An alert toast will display your **32-byte Decryption Key**.

> ⚠️ **IMPORTANT**: Copy and save your Decryption Key! You will need it to decrypt and download the file later.

### 4. Dashboard & Managing Files
- Your uploaded files are listed in a table showing:
  - **File Name**
  - **Upload Timestamp**
  - **File Size**
  - **Storage Status** (`Cloud & Local` or `Local Offline Storage`)
- To delete a file, click the **Delete** button in the corresponding row.

### 5. Decrypting & Downloading Files
1. In the file table, click **Download & Decrypt**.
2. You will be redirected to the `/enter-key/<file_id>` decryption page.
3. Paste the **32-byte Secret Key** you received during upload into the key field.
4. Click **Decrypt & Download**.
5. If the key is valid, the file will be decrypted on-the-fly and automatically downloaded to your device in its original format.

### 6. Account Password Recovery
If you forget your password:
1. Click **Forgot password?** on the `/login` page.
2. Enter your registered email address and click **Verify Email**.
3. Upon email verification, you will be navigated to the `/reset-password` page.
4. Enter your new password (must satisfy all 5 strength requirements) and confirm it.
5. Click **Update Password** to save the new credentials and log in.

---

## 🏗️ System Architecture & Features

```
[ User Browser ]
       │
       ▼
 [ Flask App (app.py) ]
       │
       ├──► Password Validator (Werkzeug Hashing)
       ├──► XOR Encryption / Decryption Engine (Secrets API)
       │
       ├──► [ Network Probe (is_firebase_available) ]
       │          │ (Fast 2s probe, 30s TTL cache)
       │          ├──► [ ONLINE  ] ──► Firebase Realtime Database
       │          └──► [ OFFLINE ] ──► local_db.json
```

### Encryption Mechanism
- **Key Generation**: 32 cryptographically secure random bytes generated using Python's `secrets` module.
- **Cipher**: Multi-byte repeating-key XOR stream transformation.
- **Serialization**: Base64 encoding applied to raw cipher bytes before storing in database nodes.

### Hybrid Storage & Offline Resiliency
- Dual-database strategy ensuring complete app functionality regardless of internet status.
- Primary storage attempts sync with **Firebase Realtime Database**.
- Automatic fallback writes and reads from **`local_db.json`**.
- Key sanitization converts prohibited characters (`.`, `$`, `#`, `[`, `]`, `/`) to underscores to guarantee valid database paths across Windows and Unix filesystems.

### Fast Network Probing
- Prevents 30–60 second network timeout delays when offline.
- Executes a 2-second socket ping against Firebase host on port 443.
- Caches the online/offline status for 30 seconds to minimize redundant pings.

---

## ❓ Troubleshooting & FAQs

- **Q: How do I fix `python` command not found on Windows?**  
  *A:* Re-run the Python installer and check **"Add Python to PATH"**, or use `py app.py` instead of `python app.py`.

- **Q: How do I fix PowerShell `script execution disabled` error on Windows?**  
  *A:* Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in PowerShell before running `.\venv\Scripts\Activate.ps1`.

- **Q: Why does my file upload fail with a size error?**  
  *A:* The maximum single file size limit is **10 MB**. Compress or split files larger than 10MB before uploading.

- **Q: What happens if my internet connection goes offline while using the app?**  
  *A:* The app seamlessly switches to `Local Offline Storage`. All uploads, logins, and downloads will continue to work normally using local records.

- **Q: I lost my Decryption Key. Can I recover my file?**  
  *A:* Because XOR encryption relies on a random 256-bit key not stored on the server for security reasons, lost keys cannot be recovered. Always back up your encryption keys safely.

- **Q: How do I run the automated test suite on Windows?**  
  *A:* Run `python test_integration.py` in your Command Prompt / PowerShell terminal.
