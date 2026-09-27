"""
MindPulse: Security and Authentication Engine
Implements secure password hashing with PBKDF2-HMAC-SHA256 and constant-time comparison.
"""

import hashlib
import os
import hmac
import re
from typing import Optional
from src.core.models import User
from src.core.exceptions import AuthenticationError, UserAlreadyExistsError, ValidationError
from src.storage.repository import UserRepository


class SecurityService:
    """Provides cryptographic operations for password hashing and authentication."""

    ITERATIONS = 100_000
    ALGORITHM = "sha256"

    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
        """
        Hashes a plain-text password using PBKDF2-HMAC-SHA256.
        Returns (hex_hash, hex_salt).
        """
        if salt is None:
            salt_bytes = os.urandom(16)
            salt = salt_bytes.hex()
        else:
            salt_bytes = bytes.fromhex(salt)

        key = hashlib.pbkdf2_hmac(
            SecurityService.ALGORITHM,
            password.encode("utf-8"),
            salt_bytes,
            SecurityService.ITERATIONS
        )
        return key.hex(), salt

    @staticmethod
    def verify_password(password: str, stored_hash: str, salt: str) -> bool:
        """Verifies password using constant-time comparison to avoid timing attacks."""
        computed_hash, _ = SecurityService.hash_password(password, salt)
        return hmac.compare_digest(computed_hash, stored_hash)


class AuthService:
    """Manages user registration, credential validation, and active session context."""

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
        self.current_user: Optional[User] = None

    def validate_username(self, username: str) -> None:
        """Validates username format and constraints."""
        username = username.strip()
        if len(username) < 3 or len(username) > 20:
            raise ValidationError("Username must be between 3 and 20 characters.")
        if not re.match(r"^[a-zA-Z0-9_]+$", username):
            raise ValidationError("Username may only contain letters, numbers, and underscores.")

    def validate_password(self, password: str) -> None:
        """Validates password strength criteria."""
        if len(password) < 6:
            raise ValidationError("Password must be at least 6 characters in length.")

    def register(self, username: str, password: str) -> User:
        """Registers a new user account with hashed credentials."""
        self.validate_username(username)
        self.validate_password(password)

        existing = self.user_repo.get_by_username(username)
        if existing:
            raise UserAlreadyExistsError(f"Username '{username}' is already registered.")

        pw_hash, salt = SecurityService.hash_password(password)
        user = self.user_repo.create_user(username, pw_hash, salt)
        return user

    def login(self, username: str, password: str) -> User:
        """Authenticates user credentials and establishes active session context."""
        user = self.user_repo.get_by_username(username)
        if not user:
            raise AuthenticationError("Invalid username or password.")

        if not SecurityService.verify_password(password, user.password_hash, user.salt):
            raise AuthenticationError("Invalid username or password.")

        self.user_repo.update_last_login(user.user_id)
        self.current_user = user
        return user

    def logout(self) -> None:
        """Clears the active session context."""
        self.current_user = None

    def get_current_user(self) -> Optional[User]:
        return self.current_user
