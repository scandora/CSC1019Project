import requests

BASE_URL = "http://127.0.0.1:5000"

def get_user_action():
    actions = ["Rock", "Paper", "Scissors", "Batman", "Ozzy", "Lizard", "Spock"]
    for i, action in enumerate(actions, 1):
        print(f"{i}. {action}")
    choice = int(input("Enter the number of your choice: "))
    if 1 <= choice <= len(actions):
        return actions[choice - 1]
    else:
        print("Invalid choice. Please try again.")
        return get_user_action()

def play_against_computer():
    user_action = get_user_action()
    response = requests.post(f"{BASE_URL}/play", json={"user_action": user_action})
    if response.status_code == 200:
        try:
            result = response.json()
            print(f"User action: {result['user_action']}")
            print(f"Computer action: {result['computer_action']}")
            print(f"Result: {result['result']}")
        except requests.exceptions.JSONDecodeError:
            print("Error: Received non-JSON response from server")
    else:
        try:
            error_message = response.json().get("error")
        except requests.exceptions.JSONDecodeError:
            error_message = "Unknown error"
        print("Error:", error_message)

def play_against_user():
    user_action = get_user_action()
    opponent_action = get_user_action()
    response = requests.post(f"{BASE_URL}/play", json={"user_action": user_action, "opponent_action": opponent_action})
    if response.status_code == 200:
        try:
            result = response.json()
            print(f"User action: {result['user_action']}")
            print(f"Opponent action: {result['opponent_action']}")
            print(f"Result: {result['result']}")
        except requests.exceptions.JSONDecodeError:
            print("Error: Received non-JSON response from server")
    else:
        try:
            error_message = response.json().get("error")
        except requests.exceptions.JSONDecodeError:
            error_message = "Unknown error"
        print("Error:", error_message)

def main():
    while True:
        print("\n1. Play against computer")
        print("2. Play against another user")
        print("0. Quit")
        choice = int(input("Enter your choice: "))
        if choice == 1:
            play_against_computer()
        elif choice == 2:
            play_against_user()
        elif choice == 0:
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()