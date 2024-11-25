'''
Main.py

Description:
    Main entry point for the Mafia game. This program initializes the game, sets up player roles, 
    and controls the main game loop. It alternates between day and night phases until a win 
    condition is met.
Programmers: Ethan Doughty, Jack Piggot, Aiden Murphy, Daniel Bobadilla, Vy Luu
Date Created: 10/27/24

Revisions:
    - 10/25/2024: Jack - Created the three main files and implemented the basic game logic
    - 10/27/2024: Ethan - Created the day_phase and win_condion methods in gameClass
                        - Created this header
    - 10/27/2024: Vy - Added a dedicated assignRoles, update_role_count and start_game methods to GameClass 
                     - Added a game-over screen with restart and exit options in main
    - [Date]: [Name] - Blah Blah Blah
    - [Date]: [Name] - Blah Blah Blah
    - [Date]: [Name] - Blah Blah Blah

Preconditions:
    - A valid integer input for the number of players.
    - Each player must have a unique name and a valid role (e.g., ethan, mafia).

Acceptable Inputs:
    - number_of_players: Integer, representing the number of players participating in the game.

Unacceptable Inputs:
    - Non-integer inputs for player count will raise a ValueError.
    - Empty or invalid strings when entering player names and roles will lead to incorrect initialization.

Postconditions:
    - The game will initialize with the specified number of players, each with a unique name and role.
    - The game will end once a win condition (either mafia or village) is met.

Return Values:
    - None; this file does not return any values as it runs the game loop directly.

Exceptions:
    - ValueError if input for number of players is non-integer.
    - Custom error handling is required for input validation on player names and roles.

Side Effects:
    - Outputs messages to the console.
    - Changes the game state using `GameClass` methods.

Invariants:
    - `gameCompleted` remains `False` until a win condition is met.
    - Each player is assigned a role upon creation.

Known Faults:
    - Input validation is minimal; role validation is not enforced strictly.  
'''

from player import Player
from gameClass import GameClass
import os
import sys

def main_menu():
    power_flag = True
    print("-----Welcome to Mafia-----\n")
    while power_flag:
        # Prompt the user to choose between single or multiplayer
        print("Singleplayer or Multiplayer?")
        print("1) Singleplayer")
        print("2) Multiplayer")
        print("3) Exit")
        gamemode = input("Enter a choice: ")

        if gamemode in {'1', '2', '3'}:
            return gamemode
        else:
            print('Invalid Input. Please enter 1, 2, or 3.')

def main():
    os.system('cls' if os.name == 'nt' else 'clear') # Clear the terminal

    mode = main_menu()

    if mode == '3':
        print("Exiting Program...")
        sys.exit("Exit Complete.")

    if mode == '1':
        print(f"Player Mode: Single Player")
        game = GameClass(10, int(mode))
        name = input("Enter player name: ").lower
        game.add_player(name)

        # Choose an AI Mode
        game.ai_mode()
        
        name_list = ["John", "Bob", "Robin", "Elizabeth", "Alice", "Danny", "Alphonso", "Sedrick", "Darius"]
        for player in name_list:
            game.add_player(player)

        game.assignRoles()
        game.start_game()

    if mode == '2':
        print(f"Player Mode: Multiplayer\n")
    
        # Prompt for the number of players and create a GameClass instance
        number_of_players = int(input("Enter number of players: "))
        game = GameClass(number_of_players, int(mode))

        # Loop to add players by prompting for each player's name
        for _ in range(number_of_players):
            name = input("Enter player name: ").lower()
            game.add_player(name)  # Add each player to the game
    
        # Assign roles to each player in the game
        game.assignRoles()

        # Start the game loop which alternates between day and night phases
        game.start_game()

    # Display the game-over options once a win condition is met
    while True:
        # Offer options to restart or exit
        choice = input("Game over! Would you like to (R)estart or (E)xit? ").lower()
        if choice == 'r':
            # Restart the game
            main()
        elif choice == 'e':
            # Exit the game
            print("Thank you for playing Mafia!")
            break
        else:
            # Prompt for valid input if an invalid choice is entered
            print("Invalid choice, please select R or E.")

# Run the main function to start the game initially
main()
