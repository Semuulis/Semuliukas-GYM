import unittest
import os
import promo1

class TestFitnessApp(unittest.TestCase):

    def setUp(self):
        self.username = "Yra yra nera bus"
        self.password = "SikSiksik"
        self.hashed_password = promo1.hash_password(self.password)

    def test_hash_password(self):
        self.assertNotEqual(self.password, self.hashed_password)

    def test_verify_password(self):
        self.assertTrue(promo1.verify_password(self.hashed_password, self.password))

    def simulate_user_signup(self):
        promo1.user_information(self.username, self.hashed_password)
        self.assertTrue(os.path.exists(f"{self.username}_task.txt"))

    def test_signup(self):
        self.simulate_user_signup()
        with open(f"{self.username}_task.txt", 'r') as file:
            contents = file.read()
            self.assertIn(self.username, contents)

    def tearDown(self):
        try:
            os.remove(f"{self.username}_task.txt")
        except FileNotFoundError:
            pass

if __name__ == '__main__':
    unittest.main()

