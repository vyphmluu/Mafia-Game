'''
Main.py
Runs the main while loop for the game cycle and uses the others classes and methods to run the game
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
