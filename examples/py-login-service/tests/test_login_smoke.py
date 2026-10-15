"""Smoke tests for the login module (SYNTHETIC FIXTURE)."""

import unittest

from login_service.auth import authenticate, make_user


class LoginSmokeTest(unittest.TestCase):
    def setUp(self):
        self.users = {"demo.user": make_user("Correct-Horse-1")}

    def test_authenticate_returns_bool(self):
        self.assertIsInstance(authenticate("demo.user", "anything", self.users), bool)

    def test_known_user_with_correct_password(self):
        self.assertTrue(authenticate("demo.user", "Correct-Horse-1", self.users))


if __name__ == "__main__":
    unittest.main()
