import unittest
import io
import os
import json
import base64
import socket

# Fast 2-second network timeout for offline fallback tests
socket.setdefaulttimeout(2.0)

from app import app, LOCAL_DB_FILE, xor_encrypt_decrypt, sanitize_key, delete_user

class IntegratedAppTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-key-2026'
        self.client = app.test_client()
        self.test_email = 'integration_test_user@example.com'
        self.test_file_name = 'test_sample_document.txt'
        self.test_content = b'This is a secret confidential string for XOR encryption end-to-end integration test.'
        delete_user(self.test_email)

    def tearDown(self):
        delete_user(self.test_email)

    def test_full_user_workflow_integration(self):
        print("\n--- 1. Testing Welcome & Register Page ---")
        welcome_res = self.client.get('/')
        self.assertEqual(welcome_res.status_code, 200)
        self.assertIn(b'FileEncryptor', welcome_res.data)

        reg_res = self.client.post('/register', data={'email': self.test_email, 'password': 'StrongP@ss123!'}, follow_redirects=True)
        self.assertEqual(reg_res.status_code, 200)
        self.assertIn(b'Account created successfully!', reg_res.data)

        print("--- 2. Testing User Login ---")
        login_res = self.client.post('/login', data={'email': self.test_email, 'password': 'StrongP@ss123!'}, follow_redirects=True)
        self.assertEqual(login_res.status_code, 200)
        self.assertIn(b'Dashboard', login_res.data)
        self.assertIn(b'Your Files', login_res.data)

        print("--- 3. Testing File Upload & XOR Encryption ---")
        upload_data = {
            'file': (io.BytesIO(self.test_content), self.test_file_name)
        }
        upload_res = self.client.post('/dashboard', data=upload_data, follow_redirects=True)
        self.assertEqual(upload_res.status_code, 200)
        self.assertIn(b'File uploaded and encrypted successfully!', upload_res.data)
        self.assertIn(self.test_file_name.encode('utf-8'), upload_res.data)

        print("--- 4. Testing Key Retrieval & Decryption Workflow ---")
        sanitized_filename = sanitize_key(self.test_file_name)
        download_page_res = self.client.get(f'/download/{sanitized_filename}')
        self.assertEqual(download_page_res.status_code, 200)
        self.assertIn(b'Decrypt File', download_page_res.data)

        # Retrieve encryption key from local session/record
        clean_user = sanitize_key(self.test_email)
        with open(LOCAL_DB_FILE, 'r') as f:
            db_data = json.load(f)
        
        user_records = db_data.get(clean_user, {})
        self.assertIn(sanitized_filename, user_records)
        key_b64 = user_records[sanitized_filename]['key']

        print(f"Extracted Base64 Key: {key_b64}")

        print("--- 5. Testing File Decryption & Download Payload ---")
        decrypt_res = self.client.post(f'/download/{sanitized_filename}', data={'key': key_b64})
        self.assertEqual(decrypt_res.status_code, 200)
        self.assertEqual(decrypt_res.data, self.test_content)

        print("--- 6. Testing File Deletion ---")
        delete_res = self.client.get(f'/delete/{sanitized_filename}', follow_redirects=True)
        self.assertEqual(delete_res.status_code, 200)
        self.assertIn(b'File deleted successfully!', delete_res.data)

        print("\n🎉 INTEGRATED END-TO-END WORKFLOW TEST COMPLETED SUCCESSFULLY!")

if __name__ == '__main__':
    unittest.main()
