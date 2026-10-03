import unittest
import socket
socket.setdefaulttimeout(2.0)

from app import app, save_user, get_user, verify_user_password, update_user_password, delete_user

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-auth'
        self.client = app.test_client()
        self.test_email = 'auth_user_test@example.com'
        self.correct_password = 'MySecureP@ssword123'
        self.wrong_password = 'WrongP@ssword456'
        self.new_password = 'NewP@ssword789!'
        delete_user(self.test_email)

    def tearDown(self):
        delete_user(self.test_email)

    def test_registration_and_password_verification(self):
        # 1. Register User
        res = self.client.post('/register', data={
            'email': self.test_email,
            'password': self.correct_password
        }, follow_redirects=True)
        self.assertIn(b'Account created successfully!', res.data)

        # 2. Verify User stored and hashed
        user = get_user(self.test_email)
        self.assertIsNotNone(user)
        self.assertNotEqual(user['password_hash'], self.correct_password)
        self.assertTrue(verify_user_password(self.test_email, self.correct_password))
        self.assertFalse(verify_user_password(self.test_email, self.wrong_password))

        # 3. Test Login with Wrong Password
        res_fail = self.client.post('/login', data={
            'email': self.test_email,
            'password': self.wrong_password
        }, follow_redirects=True)
        self.assertIn(b'Invalid email or password!', res_fail.data)

        # 4. Test Login with Correct Password
        res_success = self.client.post('/login', data={
            'email': self.test_email,
            'password': self.correct_password
        }, follow_redirects=True)
        self.assertIn(b'Login successful!', res_success.data)

    def test_forgot_and_reset_password_workflow(self):
        # Register user first
        save_user(self.test_email, self.correct_password)

        # 1. Forgot password with invalid email
        res_invalid = self.client.post('/forgot-password', data={'email': 'unregistered_unknown@example.com'}, follow_redirects=True)
        self.assertIn(b'No account found with that email address!', res_invalid.data)

        # 2. Forgot password with valid registered email
        res_valid = self.client.post('/forgot-password', data={'email': self.test_email}, follow_redirects=True)
        self.assertIn(b'Email verified! Please enter your new password.', res_valid.data)
        self.assertIn(b'Create New Password', res_valid.data)

        # 3. Reset password submit
        res_reset = self.client.post('/reset-password', data={
            'password': self.new_password,
            'confirm_password': self.new_password
        }, follow_redirects=True)
        self.assertIn(b'Password updated successfully!', res_reset.data)

        # 4. Login with old password (should fail)
        res_old_pass = self.client.post('/login', data={
            'email': self.test_email,
            'password': self.correct_password
        }, follow_redirects=True)
        self.assertIn(b'Invalid email or password!', res_old_pass.data)

        # 5. Login with new password (should succeed)
        res_new_pass = self.client.post('/login', data={
            'email': self.test_email,
            'password': self.new_password
        }, follow_redirects=True)
        self.assertIn(b'Login successful!', res_new_pass.data)

if __name__ == '__main__':
    unittest.main()
