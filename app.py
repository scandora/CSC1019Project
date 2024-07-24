from flask import Flask, request, jsonify, session
import pandas as pd
import random

class User:
    def __init__(self, username):
        self.username = username
        self.session_token = None
        self.opponent = None
        self.action = None
        self.game_request = None

    def clear_game_request(self):
        self.game_request = None
        self.opponent = None
        self.action = None

app = Flask(__name__)
app.secret_key = 'your_secret_key'

users = {}
game_sessions = {}

# Add the computer user
computer_username = "Computer"
users[computer_username] = User(computer_username)

outcome_matrix_df = pd.DataFrame(
    [
        [None, False, True, False, True, True, False],  # Rock: Wins against Scissors, Batman, Lizard; loses to Paper, Ozzy, Spock
        [True, None, False, True, False, True, False],  # Paper: Wins against Rock, Spock, Batman; loses to Scissors, Lizard, Ozzy
        [False, True, None, False, True, False, True],  # Scissors: Wins against Paper, Lizard, Ozzy; loses to Rock, Batman, Spock
        [True, False, True, None, False, False, True],  # Batman: Wins against Scissors, Lizard, Ozzy; loses to Rock, Paper, Spock
        [False, True, False, True, None, True, False],  # Ozzy: Wins against Rock, Paper, Spock; loses to Scissors, Batman, Lizard
        [False, True, False, True, False, None, True],  # Lizard: Wins against Paper, Spock, Ozzy; loses to Rock, Scissors, Batman
        [True, False, True, False, True, False, None],  # Spock: Wins against Rock, Scissors, Batman; loses to Paper, Ozzy, Lizard
    ],
    columns=["Rock", "Paper", "Scissors", "Batman", "Ozzy", "Lizard", "Spock"],
    index=["Rock", "Paper", "Scissors", "Batman", "Ozzy", "Lizard", "Spock"]
)

def get_computer_action():
    return random.choice(list(outcome_matrix_df.columns))

def determine_winner(user_action, opponent_action):
    if user_action == opponent_action:
        return "It's a tie!"
    elif outcome_matrix_df.at[user_action, opponent_action]:
        return "You win!"
    else:
        return "You lose!"

# Error handling
@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad Request"}), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({"error": "Unauthorized"}), 401

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not Found"}), 404

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({"error": "Internal Server Error"}), 500

@app.route('/')
def home():
    if 'username' in session:
        return jsonify({"message": f"Welcome {session['username']}!"})
    else:
        return jsonify({"message": "Please log in."})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    if username:
        if username not in users:
            users[username] = User(username)
        session['username'] = username
        return jsonify({"message": f"Logged in as {username}"}), 200
    return jsonify({"error": "Username is required"}), 400

@app.route('/logout')
def logout():
    username = session.pop('username', None)
    if username:
        return jsonify({"message": "Logged out"}), 200
    return jsonify({"message": "No active session"}), 200

@app.route('/start_game', methods=['POST'])
def start_game():
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    opponent = data.get('opponent')
    if opponent not in users:
        return jsonify({"error": "Opponent not found"}), 404

    users[opponent].game_request = session['username']
    users[session['username']].opponent = opponent
    users[opponent].opponent = session['username']
    return jsonify({"message": f"Game request sent to {opponent}"}), 200

@app.route('/check_game_requests', methods=['GET'])
def check_game_requests():
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    username = session['username']
    requester = users[username].game_request
    if requester:
        return jsonify({"requester": requester}), 200
    return jsonify({"requester": None}), 200


@app.route('/clear_game_request', methods=['POST'])
def clear_game_request():
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    username = session['username']
    users[username].clear_game_request()
    return jsonify({"message": "Game request cleared"}), 200


@app.route('/play', methods=['POST'])
def play_game():
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    user_action = data.get('user_action')

    if user_action not in outcome_matrix_df.columns:
        return jsonify({"error": "Invalid action"}), 400

    username = session['username']
    opponent = users[username].opponent
    if not opponent:
        return jsonify({"error": "No opponent found"}), 400

    users[username].action = user_action

    if opponent == computer_username:
        opponent_action = get_computer_action()
        result = determine_winner(user_action, opponent_action)
        return jsonify({"user_action": user_action, "opponent_action": opponent_action, "result": result}), 200
    else:
        opponent_action = users[opponent].action
        if opponent_action:
            result = determine_winner(user_action, opponent_action)
            users[username].action = None
            users[opponent].action = None
            return jsonify({"user_action": user_action, "opponent_action": opponent_action, "result": result}), 200
        else:
            return jsonify({"message": "Waiting for opponent"}), 200

@app.route('/check_opponent_action', methods=['GET'])
def check_opponent_action():
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    username = session['username']
    opponent = users[username].opponent
    if not opponent:
        return jsonify({"error": "No opponent found"}), 400

    opponent_action = users[opponent].action
    if opponent_action:
        return jsonify({"opponent_action": opponent_action}), 200
    else:
        return jsonify({"opponent_action": None}), 200

@app.route('/users', methods=['GET'])
def get_logged_in_users():
    return jsonify({"users": list(users.keys())}), 200

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"message": "pong"}), 200

if __name__ == '__main__':
    app.run(debug=True)