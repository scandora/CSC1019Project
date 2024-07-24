import unittest
from unittest.mock import patch, MagicMock
import client

class TestClient(unittest.TestCase):

    @patch('builtins.input', side_effect=['1'])
    def test_get_user_action(self, mock_input):
        action = client.get_user_action()
        self.assertEqual(action, 'Rock')

    @patch('client.get_user_action', return_value='Rock')
    @patch('requests.post')
    def test_play_against_computer(self, mock_post, mock_get_user_action):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'user_action': 'Rock',
            'computer_action': 'Scissors',
            'result': 'Rock beats Scissors! You win!'
        }
        mock_post.return_value = mock_response

        with patch('builtins.print') as mock_print:
            client.play_against_computer()
            mock_print.assert_any_call('User action: Rock')
            mock_print.assert_any_call('Computer action: Scissors')
            mock_print.assert_any_call('Result: Rock beats Scissors! You win!')

    @patch('client.get_user_action', side_effect=['Rock', 'Paper'])
    @patch('requests.post')
    def test_play_against_user(self, mock_post, mock_get_user_action):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'user_action': 'Rock',
            'opponent_action': 'Paper',
            'result': 'Paper beats Rock! You lose.'
        }
        mock_post.return_value = mock_response

        with patch('builtins.print') as mock_print:
            client.play_against_user()
            mock_print.assert_any_call('User action: Rock')
            mock_print.assert_any_call('Opponent action: Paper')
            mock_print.assert_any_call('Result: Paper beats Rock! You lose.')

    @patch('builtins.input', side_effect=['1', '0'])
    @patch('client.play_against_computer')
    def test_main(self, mock_play_against_computer, mock_input):
        with patch('builtins.print') as mock_print:
            client.main()
            mock_print.assert_any_call('Goodbye!')
            mock_play_against_computer.assert_called_once()

if __name__ == '__main__':
    unittest.main()