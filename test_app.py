import unittest
from flask import Flask
from app import app, outcome_matrix_df

class TestMicroservice(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def tearDown(self):
        pass

    def test_home(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Welcome to the Rock-Paper-Scissors-Batman-Ozzy-Lizard-Spock Game!", response.data)

    def test_play_against_computer(self):
        for action in outcome_matrix_df.columns:
            response = self.app.post('/play', json={"user_action": action})
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertIn("user_action", data)
            self.assertIn("computer_action", data)
            self.assertIn("result", data)
            self.assertEqual(data["user_action"], action)

    def test_play_against_user(self):
        for user_action in outcome_matrix_df.columns:
            for opponent_action in outcome_matrix_df.columns:
                response = self.app.post('/play', json={"user_action": user_action, "opponent_action": opponent_action})
                self.assertEqual(response.status_code, 200)
                data = response.get_json()
                self.assertIn("user_action", data)
                self.assertIn("opponent_action", data)
                self.assertIn("result", data)
                self.assertEqual(data["user_action"], user_action)
                self.assertEqual(data["opponent_action"], opponent_action)

if __name__ == '__main__':
    unittest.main()