"""
Unit tests for security, cryptographic hashing, and authentication workflows.
"""

import unittest
from src.core.exceptions import ValidationError, AuthenticationError, UserAlreadyExistsError
from src.storage.database import DatabaseManager
from src.storage.repository import UserRepository
from src.security.auth import SecurityService, AuthService


class TestSecurityAndAuth(unittest.TestCase):

    def setUp(self):
        # In-memory database for fast, isolated test execution
        self.db = DatabaseManager(":memory:")
        self.user_repo = UserRepository(self.db)
        self.auth = AuthService(self.user_repo)

    def test_password_hashing_and_verification(self):
        password = "SecurePassword#2026"
        pw_hash, salt = SecurityService.hash_password(password)
        
        self.assertIsNotNone(pw_hash)
        self.assertIsNotNone(salt)
        self.assertEqual(len(salt), 32)  # 16 bytes hex

        # Positive verification
        self.assertTrue(SecurityService.verify_password(password, pw_hash, salt))
        # Negative verification (wrong password)
        self.assertFalse(SecurityService.verify_password("WrongPassword!", pw_hash, salt))

    def test_username_validation(self):
        # Valid username
        self.auth.validate_username("valid_user99")

        # Too short
        with self.assertRaises(ValidationError):
            self.auth.validate_username("ab")

        # Illegal symbols
        with self.assertRaises(ValidationError):
            self.auth.validate_username("user@vit.ac.in")

    def test_password_validation(self):
        # Valid password
        self.auth.validate_password("pass123")

        # Too short
        with self.assertRaises(ValidationError):
            self.auth.validate_password("12345")

    def test_registration_and_login_lifecycle(self):
        # Register user
        user = self.auth.register("test_student", "mySecret123")
        self.assertIsNotNone(user.user_id)
        self.assertEqual(user.username, "test_student")

        # Duplicate registration should raise error
        with self.assertRaises(UserAlreadyExistsError):
            self.auth.register("test_student", "anotherPass")

        # Login with correct password
        logged_user = self.auth.login("test_student", "mySecret123")
        self.assertEqual(logged_user.user_id, user.user_id)
        self.assertEqual(self.auth.get_current_user().username, "test_student")

        # Login with bad password
        with self.assertRaises(AuthenticationError):
            self.auth.login("test_student", "badPassword")

        # Logout
        self.auth.logout()
        self.assertIsNone(self.auth.get_current_user())


if __name__ == "__main__":
    unittest.main()
