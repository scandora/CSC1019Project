from flask import Flask, request, jsonify, session
import pandas as pd
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'

logged_in_users = set()
game_sessions = {}
game_requests = {}

# Add the computer user
computer_username = "Computer"
logged_in_users.add(computer_username)

outcome_matrix_df = pd.DataFrame(
    [
        [None, False, True, False, True, True, False],  # Rock: Wins against Scissors, Batman, Lizard; loses to Paper, Ozzy, Spock
        [True, None, False, True, False, True, False],  # Paper: Wins against Rock, Spock, Batman; loses to Scissors, Lizard, Ozzy
        [False, True, None, False, True, False, True],  # Scissors: Wins against Paper, Lizard, Ozzy; loses to Rock, Batman, Spock
        [True, False, True, None, False, False, True],  # Batman: Wins against Scissors, Lizard, Ozzy; loses to Rock, Paper, Spock
        [False, True, False, True, None, True, False],  # Ozzy: Wins against Rock, Paper, Lizard; loses to Scissors, Batman, Spock
        [False, False, True, True, False, None, True],  # Lizard: Wins against Spock, Paper, Batman; loses to Rock, Scissors, Ozzy
        [True, True, False, False, True, False, None]   # Spock: Wins against Rock, Scissors, Ozzy; loses to Paper, Batman, Lizard
    ],
    columns=["Rock", "Paper", "Scissors", "Batman", "Ozzy", "Lizard", "Spock"],
    index=["Rock", "Paper", "Scissors", "Batman", "Ozzy", "Lizard", "Spock"]
)

def get_computer_action():
    return random.choice(list(outcome_matrix_df.columns))

def determine_winner(user_action, opponent_action, return_result=False):
    if user_action == opponent_action:
        result = "It's a tie!"
    else:
        outcome = outcome_matrix_df.loc[user_action, opponent_action]
        if outcome:
            result = f"{user_action} beats {opponent_action}! You win!"
        else:
            result = f"{opponent_action} beats {user_action}! You lose."
    if return_result:
        return result
    print(result)

@app.route('/')
def home():
    if 'username' in session:
        return f"Welcome {session['username']}! Use /play to start. You can play against another player or the computer."
    else:
        return "Welcome to the Rock-Paper-Scissors-Batman-Ozzy-Lizard-Spock Game! Please log in using /login."

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    if username:
        session['username'] = username
        logged_in_users.add(username)
        return jsonify({"message": f"Logged in as {username}"}), 200
    return jsonify({"error": "Username is required"}), 400

@app.route('/logout')
def logout():
    username = session.pop('username', None)
    if username:
        logged_in_users.discard(username)
    return jsonify({"message": "Logged out"}), 200

@app.route('/start_game', methods=['POST'])
def start_game():
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    opponent = data.get('opponent')
    if opponent not in logged_in_users:
        return jsonify({"error": "Opponent not logged in"}), 400

    game_requests[opponent] = session['username']
    return jsonify({"message": f"Game request sent to {opponent}"}), 200


@app.route('/check_game_requests', methods=['GET'])
def check_game_requests():
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    username = session['username']
    requester = game_requests.get(username)
    if requester:
        return jsonify({"requester": requester}), 200
    else:
        return jsonify({"message": "No game requests"}), 200


@app.route('/play', methods=['POST'])
def play_game():
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    user_action = data.get('user_action')

    if user_action not in outcome_matrix_df.columns:
        return jsonify({"error": "Invalid user action"}), 400

    opponent = game_sessions.get(session['username'])
    if not opponent:
        return jsonify({"error": "No game session found"}), 400

    # Store the user's action
    session['user_action'] = user_action

    # Check if the opponent has made their choice
    if opponent == computer_username:
        opponent_action = get_computer_action()
    else:
        opponent_action = session.get('opponent_action')

    if opponent_action:
        result = determine_winner(user_action, opponent_action, return_result=True)
        return jsonify({"user_action": user_action, "opponent_action": opponent_action, "result": result})
    else:
        return jsonify({"message": "Waiting for opponent"}), 200


@app.route('/check_opponent_action', methods=['GET'])
def check_opponent_action():
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    opponent = game_sessions.get(session['username'])
    if not opponent:
        return jsonify({"error": "No game session found"}), 400

    if opponent == computer_username:
        return jsonify({"opponent_action": get_computer_action()}), 200

    opponent_action = session.get('opponent_action')
    if opponent_action:
        return jsonify({"opponent_action": opponent_action}), 200
    else:
        return jsonify({"message": "Opponent has not made a choice yet"}), 200

@app.route('/users', methods=['GET'])
def get_logged_in_users():
    return jsonify({"users": list(logged_in_users)}), 200

if __name__ == '__main__':
    app.run(debug=True)