"""Behaviour tests for the login module (SYNTHETIC FIXTURE)."""

import unittest

from login_service.auth import authenticate, make_user


class LoginBehaviourTest(unittest.TestCase):
    def setUp(self):
        self.users = {"demo.user": make_user("Correct-Horse-1")}

    def test_wrong_password_same_length_is_rejected(self):
        wrong = "Wrong-Battery-9"
        self.assertEqual(len(wrong), len("Correct-Horse-1"))
        self.assertFalse(authenticate("demo.user", wrong, self.users))

    def test_unknown_user_is_rejected(self):
        self.assertFalse(authenticate("nobody", "Correct-Horse-1", self.users))


if __name__ == "__main__":
    unittest.main()
