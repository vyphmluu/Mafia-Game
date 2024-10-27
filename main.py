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


print("-----Welcome to Mafia-----")
print("\n")


number_of_players = int(input("Enter number of players:"))
game1 = GameClass(number_of_players)

#add players before starting the game
for player in range(number_of_players):
    game1.add_player()


#not necessary for loop, just for checking players and roles
for player in game1.player_list:
    print("Name: ", player.name, "Role: ", player.role)


#main while loop that runs the full game until its completion
while game1.gameCompleted == False:
    game1.day_phase()


    if game1.gameCompleted == True:
        break

    game1.night_phase()
