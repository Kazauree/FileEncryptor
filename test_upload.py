import unittest
import io
from app import app

class UploadTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret'
        self.client = app.test_client()

    def test_upload_without_login(self):
        response = self.client.post('/dashboard', data={}, follow_redirects=True)
        self.assertIn(b'Login', response.data)

    def test_upload_empty_file(self):
        with self.client.session_transaction() as sess:
            sess['user'] = 'testuser@example.com'

        data = {
            'file': (io.BytesIO(b''), '')
        }
        response = self.client.post('/dashboard', data=data, follow_redirects=True)
        self.assertIn(b'No file selected', response.data)

    def test_upload_valid_file(self):
        with self.client.session_transaction() as sess:
            sess['user'] = 'testuser@example.com'

        data = {
            'file': (io.BytesIO(b'Hello World! Secure file upload content.'), 'test_document.txt')
        }
        response = self.client.post('/dashboard', data=data, follow_redirects=True)
        self.assertIn(b'File uploaded and encrypted successfully!', response.data)

if __name__ == '__main__':
    unittest.main()
