import unittest
import base64
import os
import secrets
from app import xor_encrypt_decrypt, generate_key

class DecryptionTest(unittest.TestCase):
    def test_xor_encryption_decryption_text(self):
        print("\n--- 1. Testing Text Encryption & Decryption ---")
        original_text = b"CONFIDENTIAL_DATA_XOR_2026: The Federal Polytechnic Damaturu - Final Year Project"
        key = generate_key()
        
        # 1. Encrypt
        encrypted = xor_encrypt_decrypt(original_text, key)
        self.assertNotEqual(encrypted, original_text)
        
        # 2. Base64 Encode & Decode (Simulate DB Storage)
        b64_encrypted = base64.b64encode(encrypted).decode('utf-8')
        b64_key = base64.b64encode(key).decode('utf-8')
        
        raw_encrypted = base64.b64decode(b64_encrypted)
        raw_key = base64.b64decode(b64_key)
        
        # 3. Decrypt
        decrypted = xor_encrypt_decrypt(raw_encrypted, raw_key)
        self.assertEqual(decrypted, original_text)
        print(f"✓ Original Text: {original_text.decode('utf-8')}")
        print(f"✓ Encrypted (Base64): {b64_encrypted[:40]}...")
        print(f"✓ Decrypted Output Matches Original Exactly!")

    def test_xor_encryption_decryption_binary_image(self):
        print("\n--- 2. Testing Binary Image File Encryption & Decryption ---")
        # Load supervisor image if exists
        img_path = 'static/images/supervisor.png'
        if os.path.exists(img_path):
            with open(img_path, 'rb') as f:
                original_bytes = f.read()
        else:
            original_bytes = os.urandom(1024 * 50)  # 50KB random binary bytes
            
        key = generate_key()
        
        # Encrypt
        encrypted = xor_encrypt_decrypt(original_bytes, key)
        self.assertNotEqual(encrypted, original_bytes)
        
        # Decrypt
        decrypted = xor_encrypt_decrypt(encrypted, key)
        self.assertEqual(decrypted, original_bytes)
        print(f"✓ Original Binary Size: {len(original_bytes)} bytes")
        print(f"✓ Encrypted Binary Size: {len(encrypted)} bytes")
        print(f"✓ Binary Integrity Verified: Decrypted binary matches original byte-for-byte!")

    def test_wrong_key_decryption_failure(self):
        print("\n--- 3. Testing Wrong Key Decryption Security ---")
        original_text = b"SECRET_CLOUD_DOCUMENT_PAYLOAD"
        correct_key = generate_key()
        wrong_key = generate_key()
        
        encrypted = xor_encrypt_decrypt(original_text, correct_key)
        decrypted_wrong = xor_encrypt_decrypt(encrypted, wrong_key)
        
        # Decrypted with wrong key MUST NOT match original
        self.assertNotEqual(decrypted_wrong, original_text)
        print(f"✓ Wrong key produced scrambled noise output: {decrypted_wrong[:20]}")
        print(f"✓ Security Check Passed: Access denied with incorrect key!")

if __name__ == '__main__':
    unittest.main()
