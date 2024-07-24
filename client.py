import requests
import os
import signal
import sys
import atexit
import traceback
import time

BASE_URL = "http://127.0.0.1:5000"
PID = str(os.getpid())
SESSION_COOKIE = f"session_{PID}"
USERNAME_COOKIE = f"username_{PID}"

def remove_cookies():
    if os.path.exists(SESSION_COOKIE):
        os.remove(SESSION_COOKIE)
    if os.path.exists(USERNAME_COOKIE):
        os.remove(USERNAME_COOKIE)

def save_session_token(token, username):
    with open(SESSION_COOKIE, "w") as file:
        file.write(token)
    with open(USERNAME_COOKIE, "w") as file:
        file.write(username)

def load_session_token():
    if os.path.exists(SESSION_COOKIE):
        with open(SESSION_COOKIE, "r") as file:
            token = file.read().strip()
    else:
        token = None

    if os.path.exists(USERNAME_COOKIE):
        with open(USERNAME_COOKIE, "r") as file:
            username = file.read().strip()
    else:
        username = None

    return token, username

def ping_server():
    try:
        response = requests.get(f"{BASE_URL}/ping")
        if response.status_code == 200 and response.json().get("message") == "pong":
            return True
    except requests.RequestException as e:
        print(f"Error pinging server: {e}")
    return False

def login():
    if not ping_server():
        print("Server is not reachable. Please try again later.")
        sys.exit(1)

    while True:
        username = input("Enter your username: ")
        if username:
            response = requests.post(f"{BASE_URL}/login", json={"username": username})
            if response.status_code == 200:
                print(f'\n*** {response.json()["message"]}')
                save_session_token(response.cookies.get("session"), username)
                break
            else:
                print("Error:", response.json().get("error"))
        else:
            print("Error: Username is required")

def get_user_action(username):
    actions = ["Rock", "Paper", "Scissors", "Batman", "Ozzy", "Lizard", "Spock"]
    while True:
        for i, action in enumerate(actions, 1):
            print(f"{i}. {action}")
        try:
            choice = int(input(f"{username}, enter the number of your choice: "))
            if 1 <= choice <= len(actions):
                return actions[choice - 1]
            else:
                print("Invalid choice. Please enter a number between 1 and", len(actions))
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def poll_for_opponent_action(session_token):
    if not ping_server():
        print("Server is not reachable. Please try again later.")
        sys.exit(1)

    while True:
        response = requests.get(f"{BASE_URL}/check_opponent_action", cookies={"session": session_token})
        if response.status_code == 200:
            data = response.json()
            if data.get("opponent_action"):
                return data["opponent_action"]
        time.sleep(1)  # Poll every second

def check_game_requests(session_token):
    if not ping_server():
        print("Server is not reachable. Please try again later.")
        sys.exit(1)

    response = requests.get(f"{BASE_URL}/check_game_requests", cookies={"session": session_token})
    if response.status_code == 200:
        data = response.json()
        requester = data.get("requester")
        if requester:
            print(f"\n*** {requester} has requested to play a game with you.")
            choice = input("Do you want to accept the game request? (yes/no): ").strip().lower()
            if choice == 'yes':
                return requester
    return None

def clear_game_request(session_token):
    response = requests.post(f"{BASE_URL}/clear_game_request", cookies={"session": session_token})
    if response.status_code == 200:
        print(response.json()["message"])
    else:
        print("Error clearing game request:", response.json().get("error"))

def play_game():
    session_token, username = load_session_token()
    if not session_token:
        print("\n*** You need to log in first.")
        return

    # Check for pending game requests
    requester = check_game_requests(session_token)
    if requester:
        opponent = requester
    else:
        users = show_logged_in_users()
        if not users:
            return

        opponent = input("Enter the username of your choice: ").strip()
        if opponent not in users:
            print("Invalid choice. Please try again.")
            return play_game()

        if not ping_server():
            print("Server is not reachable. Please try again later.")
            sys.exit(1)

        response = requests.post(f"{BASE_URL}/start_game", json={"opponent": opponent}, cookies={"session": session_token})
        try:
            response_data = response.json()
        except requests.exceptions.JSONDecodeError:
            print("Error starting game session: Invalid JSON response")
            print("Response content:", response.content)
            return

        if response.status_code != 200:
            print("Error starting game session:", response_data.get("error"))
            return

    print(f"Game session started with {opponent}.")
    while True:
        user_action = get_user_action(username)
        if not ping_server():
            print("Server is not reachable. Please try again later.")
            sys.exit(1)

        response = requests.post(f"{BASE_URL}/play", json={"user_action": user_action}, cookies={"session": session_token})
        if response.status_code == 200:
            try:
                result = response.json()
                if result.get("message") == "Waiting for opponent":
                    print("Waiting for opponent to make a choice...")
                    opponent_action = poll_for_opponent_action(session_token)
                    if not ping_server():
                        print("Server is not reachable. Please try again later.")
                        sys.exit(1)

                    response = requests.post(f"{BASE_URL}/play", json={"user_action": user_action}, cookies={"session": session_token})
                    result = response.json()
                print(f"\n{username} action: {result['user_action']}")
                print(f"{opponent} action: {result['opponent_action']}")
                print(f"Result: {result['result']}")
                if result['result'] != "It's a tie!":
                    clear_game_request(session_token)
                    break
            except requests.exceptions.JSONDecodeError:
                print("Error: Received non-JSON response from server")
        else:
            try:
                error_message = response.json().get("error")
            except requests.exceptions.JSONDecodeError:
                error_message = "Unknown error"
            print("Error:", error_message)
            break


def show_logged_in_users():
    if not ping_server():
        print("Server is not reachable. Please try again later.")
        sys.exit(1)

    session_token, username = load_session_token()
    response = requests.get(f"{BASE_URL}/users")
    if response.status_code == 200:
        users = response.json().get("users", [])
        if users:
            users = [user for user in users if user != username]
            if users:
                print("\n*** Logged-in users:")
                for user in users:
                    print(user)
                return users
            else:
                print("\n*** No other users are currently logged in.")
        else:
            print("\n*** No users are currently logged in.")
    else:
        print("Error fetching users:", response.json().get("error"))
    return []

def logout():
    if not ping_server():
        print("Server is not reachable.  Forcing logout and cleanup.")

    session_token, username = load_session_token()
    if session_token:
        response = requests.get(f"{BASE_URL}/logout", cookies={"session": session_token})
        if response.status_code == 200:
            print(response.json()["message"])
        else:
            print("Error:", response.json().get("error"))
    else:
        print("No active session found")

    remove_cookies()

# function to say goodbye and logout, nice goodbye with no error.
def say_goodbye():
    print("\nGoodbye!")
    logout()

# cleanup function to handle signals and exit, only called on exceptions.
def cleanup(signum=None, frame=None):
    print("Cleaning up")
    if signum is not None:
        print(f"Received signal: {signum}")
    if frame is not None:
        print(f"Signal received in file: {frame.f_code.co_filename}, line: {frame.f_lineno}, in function: {frame.f_code.co_name}")
    logout()

def print_instructions():
    instructions = """
    Welcome to Rock, Paper, Scissors, Batman, Ozzy, Lizard, Spock!

    The rules are as follows:
    - Rock: Wins against Scissors, Batman, Lizard; loses to Paper, Ozzy, Spock
    - Paper: Wins against Rock, Spock, Batman; loses to Scissors, Lizard, Ozzy
    - Scissors: Wins against Paper, Lizard, Ozzy; loses to Rock, Batman, Spock
    - Batman: Wins against Scissors, Lizard, Ozzy; loses to Rock, Paper, Spock
    - Ozzy: Wins against Rock, Paper, Spock; loses to Scissors, Batman, Lizard
    - Lizard: Wins against Paper, Spock, Ozzy; loses to Rock, Scissors, Batman
    - Spock: Wins against Rock, Scissors, Batman; loses to Paper, Ozzy, Lizard

    Have fun!
    """
    print(instructions)

def main():
    atexit.register(cleanup)
    signal.signal(signal.SIGINT, cleanup)
    login()
    try:
        while True:
            session_token, username = load_session_token()
            if username:
                print(f"\nWelcome back, {username}!")
            print("\n1. Print instructions")
            print("2. Show logged-in users")
            print("3. Play game")
            print("0. Quit")
            try:
                choice = int(input(f"\nEnter your choice: "))
            except ValueError:
                print("Invalid input. Please enter a number.")
                continue

            if choice == 1:
                print_instructions()
            elif choice == 2:
                show_logged_in_users()
            elif choice == 3:
                play_game()
            elif choice == 0:
                say_goodbye()
                sys.exit(0)
            else:
                print("Invalid choice. Please try again.")
    except KeyboardInterrupt:
        cleanup()


if __name__ == "__main__":
    main()