from flask import Flask, request, jsonify
import pandas as pd
import random

app = Flask(__name__)

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

def get_computer_selection():
    action_name = random.choice(list(outcome_matrix_df.columns))
    print(f"Computer has chosen: {action_name}")
    return action_name


def determine_winner(user_action, computer_action, return_result=False):
    if user_action == computer_action:
        result = "It's a tie!"
    else:
        outcome = outcome_matrix_df.loc[user_action, computer_action]
        if outcome:
            result = f"{user_action} beats {computer_action}! You win!"
        else:
            result = f"{computer_action} beats {user_action}! You lose."
    if return_result:
        return result
    print(result)


@app.route('/')
def home():
    return "Welcome to the Rock-Paper-Scissors-Batman-Ozzy-Lizard-Spock Game! Use /play to start. You can play against another player or the computer."


@app.route('/play', methods=['POST'])
def play_game():
    data = request.json
    user_action = data.get('user_action')
    opponent_action = data.get('opponent_action', None)  # New line to accept opponent's action

    # Validate user action
    if user_action not in outcome_matrix_df.columns:
        return jsonify({"error": "Invalid user action"}), 400

    # User vs. Computer
    if opponent_action is None:
        computer_action = get_computer_selection()
        result = determine_winner(user_action, computer_action, return_result=True)
        return jsonify({"user_action": user_action, "computer_action": computer_action, "result": result})

    # User vs. User
    elif opponent_action in outcome_matrix_df.columns:  # Validate opponent action
        result = determine_winner(user_action, opponent_action, return_result=True)
        return jsonify({"user_action": user_action, "opponent_action": opponent_action, "result": result})
    else:
        return jsonify({"error": "Invalid opponent action"}), 400


if __name__ == '__main__':
    app.run(debug=True)