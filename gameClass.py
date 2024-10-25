'''
gameClass.py
Runs the game through the day phase/voting phase and the night phase using methods from the player class
'''

from player import Player

class GameClass:
    def __init__(self, players):
        self.num_players = players
        self.num_mafia = 0
        self.num_doctors = 0
        self.num_villagers = 0
        self.gameCompleted = False
        self.player_list = []

    def add_player(self):

        player_name = input("Enter player name:")   #assign player name
        player_name = player_name.lower()
        print("\n")

        player_role = input("Enter role(mafia, villager, doctor):")   #assign role through user input, will randomized later
        player_role = player_role.lower()
        print("\n")


        self.player_list.append(Player(player_role, player_name))   #adds player to list of players

        if player_role == "mafia":
            self.num_mafia += 1
        elif player_role == "doctor":
            self.num_doctors += 1
        else:
            self.num_villagers += 1

    def day_phase(self):
        
        #each player either votes to kill a player or votes to pass

        #dead players do not interact



        #game completion conditions check
        if (self.num_mafia == 0):
            self.gameCompleted = True
            print("Village Wins!")
        elif (self.num_mafia >= (self.num_villagers + self.num_doctors)):
            self.gameCompleted = True
            print("Mafia wins!")

    def night_phase(self):

        #mafia choose someone to kill (maybe more than 1 for more players/mafia)

        #doctors choose someone to protect

        #villagers do nothing

        #dead players do not interact


        #game completion conditions check
        if (self.num_mafia == 0):
            self.gameCompleted = True
            print("Village Wins!")
        elif (self.num_mafia >= (self.num_villagers + self.num_doctors)):
            self.gameCompleted = True
            print("Mafia wins!")










