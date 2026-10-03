import firebase_admin
from firebase_admin import credentials, db
import sys

def test_firebase_connection():
    print("1. Initializing Firebase Admin SDK...")
    try:
        cred = credentials.Certificate('firebase-key.json')
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://fileencryption-69539-default-rtdb.firebaseio.com/'
        })
        print("✓ Firebase initialized successfully.")
    except Exception as e:
        print(f"✗ Failed to initialize Firebase: {e}")
        sys.exit(1)

    print("\n2. Testing Write Operation to Firebase RTDB...")
    try:
        ref = db.reference('test_node')
        test_data = {
            'status': 'connected',
            'message': 'Firebase RTDB test successful!',
            'timestamp': '2026-08-11'
        }
        ref.set(test_data)
        print("✓ Write successful: Set test node in database.")
    except Exception as e:
        print(f"✗ Failed to write to Firebase: {e}")
        sys.exit(1)

    print("\n3. Testing Read Operation from Firebase RTDB...")
    try:
        data = ref.get()
        print(f"✓ Read successful! Fetched data: {data}")
        assert data.get('status') == 'connected'
    except Exception as e:
        print(f"✗ Failed to read from Firebase: {e}")
        sys.exit(1)

    print("\n4. Testing Delete Operation on Firebase RTDB...")
    try:
        ref.delete()
        print("✓ Cleanup/Delete successful! Test node removed.")
    except Exception as e:
        print(f"✗ Failed to delete test node: {e}")
        sys.exit(1)

    print("\n🎉 ALL FIREBASE TESTS PASSED SUCCESSFULLY!")

if __name__ == '__main__':
    test_firebase_connection()
