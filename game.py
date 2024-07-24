# import pandas as pd
# import random
#
#
# outcome_matrix_df = pd.DataFrame(
#     [
#         [None, False, True, False, True, True, False],  # Rock: Wins against Scissors, Batman, Lizard; loses to Paper, Ozzy, Spock
#         [True, None, False, True, False, True, False],  # Paper: Wins against Rock, Spock, Batman; loses to Scissors, Lizard, Ozzy
#         [False, True, None, False, True, False, True],  # Scissors: Wins against Paper, Lizard, Ozzy; loses to Rock, Batman, Spock
#         [True, False, True, None, False, False, True],  # Batman: Wins against Scissors, Lizard, Ozzy; loses to Rock, Paper, Spock
#         [False, True, False, True, None, True, False],  # Ozzy: Wins against Rock, Paper, Lizard; loses to Scissors, Batman, Spock
#         [False, False, True, True, False, None, True],  # Lizard: Wins against Spock, Paper, Batman; loses to Rock, Scissors, Ozzy
#         [True, True, False, False, True, False, None]   # Spock: Wins against Rock, Scissors, Ozzy; loses to Paper, Batman, Lizard
#     ],
#     columns=["Rock", "Paper", "Scissors", "Batman", "Ozzy", "Lizard", "Spock"],
#     index=["Rock", "Paper", "Scissors", "Batman", "Ozzy", "Lizard", "Spock"]
# )
#
#
# def get_user_selection():
#     choices = list(outcome_matrix_df.columns)
#     choices_str = ", ".join([f"{name}[{i}]" for i, name in enumerate(choices, 1)])
#     print(f"Enter a choice ({choices_str}), or 0 to Quit:")
#     selection = int(input())
#     if selection == 0:
#         return None
#     action_name = choices[selection - 1]
#     print(f"User has chosen: {action_name}")
#     return action_name
#
# def get_computer_selection():
#     action_name = random.choice(list(outcome_matrix_df.columns))
#     print(f"Computer has chosen: {action_name}")
#     return action_name
#
# def determine_winner(user_action, computer_action):
#     if user_action is None:
#         return
#     result = outcome_matrix_df.loc[user_action, computer_action]
#     if result is None:
#         print(f"Both players selected {user_action}. It's a tie!")
#     elif result:
#         print(f"{user_action} beats {computer_action}! You win!")
#     else:
#         print(f"{computer_action} beats {user_action}! You lose.")
#
# while True:
#     try:
#         user_action = get_user_selection()
#         if user_action is None:  # User chose to quit
#             print("Game over. Thanks for playing!")
#             break
#     except ValueError as e:
#         print(f"Invalid selection. Please try again.")
#         continue
#
#     computer_action = get_computer_selection()
#     determine_winner(user_action, computer_action)