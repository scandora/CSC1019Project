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

def login():
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
    for i, action in enumerate(actions, 1):
        print(f"{i}. {action}")
    choice = int(input(f"{username}, enter the number of your choice: "))
    if 1 <= choice <= len(actions):
        return actions[choice - 1]
    else:
        print("Invalid choice. Please try again.")
        return get_user_action(username)

def poll_for_opponent_action(session_token):
    while True:
        response = requests.get(f"{BASE_URL}/check_opponent_action", cookies={"session": session_token})
        if response.status_code == 200:
            data = response.json()
            if data.get("opponent_action"):
                return data["opponent_action"]
        time.sleep(1)  # Poll every second

def check_game_requests(session_token):
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

def check_game_requests_and_offer_to_play():
    session_token, username = load_session_token()
    if not session_token:
        print("\n***You need to log in first.")
        return

    requester = check_game_requests(session_token)
    if requester:
        print(f"\n*** {requester} has requested to play a game with you.")
        choice = input("Do you want to accept the game request? (yes/no): ").strip().lower()
        if choice == 'yes':
            play_against_user()
        else:
            print("Game request declined.")
    else:
        print("No game requests found.")


def play_against_user():
    session_token, username = load_session_token()
    if not session_token:
        print("\n***You need to log in first.")
        return

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
            return play_against_user()

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
        response = requests.post(f"{BASE_URL}/play", json={"user_action": user_action}, cookies={"session": session_token})
        if response.status_code == 200:
            try:
                result = response.json()
                if result.get("message") == "Waiting for opponent":
                    print("Waiting for opponent to make a choice...")
                    opponent_action = poll_for_opponent_action(session_token)
                    response = requests.post(f"{BASE_URL}/play", json={"user_action": user_action}, cookies={"session": session_token})
                    result = response.json()
                print(f"\nUser action: {result['user_action']}")
                print(f"Opponent action: {result['opponent_action']}")
                print(f"Result: {result['result']}")
                if result['result'] != "It's a tie!":
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
    session_token, username = load_session_token()
    if session_token:
        response = requests.get(f"{BASE_URL}/logout", cookies={"session": session_token})
        if response.status_code == 200:
            print(response.json()["message"])
            remove_cookies()
        else:
            print("Error:", response.json().get("error"))
    else:
        print("No active session found.")

def say_goodbye():
    print("\nGoodbye!")
    logout()

def cleanup(signum=None, frame=None):
    print("Cleaning up")
    if signum is not None:
        print(f"Received signal: {signum}")
    if frame is not None:
        print(f"Signal received in file: {frame.f_code.co_filename}, line: {frame.f_lineno}, in function: {frame.f_code.co_name}")
    logout()


def refresh_main_menu():
    print("\nRefreshing main menu...")
    main()


def main():
    atexit.register(cleanup)
    signal.signal(signal.SIGINT, cleanup)
    login()
    try:
        while True:
            session_token, username = load_session_token()
            if username:
                print(f"\nWelcome back, {username}!")
            print("\n1. Play against another user")
            print("2. Show logged-in users")
            print("3. Check for game requests and offer to play")
            print("4. Refresh main menu")
            print("0. Quit")
            choice = int(input(f"\nEnter your choice: "))
            if choice == 1:
                play_against_user()
            elif choice == 2:
                show_logged_in_users()
            elif choice == 3:
                check_game_requests_and_offer_to_play()
            elif choice == 4:
                refresh_main_menu()
            elif choice == 0:
                say_goodbye()
                sys.exit(0)
            else:
                print("Invalid choice. Please try again.")
    except KeyboardInterrupt:
        say_goodbye()
        sys.exit(0)
    except Exception as e:
        print(f"An error occurred: {e}")
        print(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()