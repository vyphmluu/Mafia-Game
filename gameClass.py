'''
gameClass.py
Description:
    This file contains the GameClass, which manages the primary gameplay mechanics for Mafia. 
    The GameClass includes methods for the day phase (voting phase), where players vote to 
    eliminate others, and the night phase, where actions specific to player roles occur. 
    It interacts with the Player class to handle individual player attributes and behaviors.
'''

from player import Player
import os
import random

class GameClass:
    def __init__(self, players):
        self.num_players = players  # Total number of players in the game
        self.num_mafia = 0  # Counter for mafia players
        self.num_doctors = 0  # Counter for doctor players
        self.num_villagers = 0  # Counter for villager players
        self.gameCompleted = False  # Boolean to indicate if the game has ended
        self.player_list = []  # List to store player objects
        self.roles = ['mafia', 'doctor', 'villager'] * (self.num_players // 3 + 1)

    def add_player(self, name):
        """ Adds a new player to the game with a placeholder role. """
        player = Player(role=None, name=name)
        self.player_list.append(player)

    def assignRoles(self):
        """ Dynamically assigns roles to players based on the number of players. """
        # Calculate number of roles based on player count
        num_mafia = max(1, self.num_players // 3)  # At least 1 mafia, ~1/3 of players
        num_detective = 1 if self.num_players >= 5 else 0  # 1 detective for 5+ players
        num_doctors = 1 if self.num_players >= 4 else 0  # 1 doctor for 4+ players
        num_villagers = self.num_players - (num_mafia + num_detective + num_doctors)  # Remaining players are villagers

        # Create a role list based on calculated numbers
        roles = (
            ['mafia'] * num_mafia +
            ['detective'] * num_detective +
            ['doctor'] * num_doctors +
            ['villager'] * num_villagers
        )
        
        # Shuffle roles to ensure randomness
        random.shuffle(roles)

        # Assign roles to players and update role counts
        for player in self.player_list:
            role = roles.pop()  # Assign a role from the shuffled list
            player.role = role
            self.update_role_count(role, increment=True)
            print(f"{player.name} has been assigned the role of {role}.")
        
        # Debugging output to check balance
        print(f"Roles distribution: Mafia: {num_mafia}, Doctor: {num_doctors}, Detective: {num_detective}, Villagers: {num_villagers}")

    def update_role_count(self, role, increment):
        """ Updates the count of each role based on the player's assigned role. """
        if role == "mafia":
            self.num_mafia += 1 if increment else -1
        elif role == "doctor":
            self.num_doctors += 1 if increment else -1
        elif role == "villager":
            self.num_villagers += 1 if increment else -1

    def day_phase(self):
        """ Manages the day phase of the game where players can vote to eliminate others. """
        votes = {}
        print("Day Phase: Time to vote!")
        input("Press any key to continue...")
        for player in self.player_list:
            if player.status == "alive":
                print(f"\n{player.name} is voting...")
                alive_players = [p.name for p in self.player_list if p.status == "alive" and p.name != player.name]
                if player.role == "mafia":
                    print(f"\nMafia Allies: {self.mafia_ally_list(player.name)}")
                print("Players available to vote for:", ', '.join(alive_players))
                vote_for = input(f"{player.name}, who do you vote to eliminate? ").lower()
                if player.role == "mafia":
                    self.targetHistory(player, vote_for)
                if vote_for == player.name:
                    print("You cannot vote for yourself. Skipping vote.")
                    continue
                voted_player = next((p for p in self.player_list if p.name == vote_for and p.status == "alive"), None)
                if voted_player:
                    votes[vote_for] = votes.get(vote_for, 0) + 1
                else:
                    print(f"{vote_for} is either not found or not alive. Vote is skipped.")
            self.clear_console()
        if votes:
            max_votes_player = max(votes, key=votes.get)
            eliminated_player = next((p for p in self.player_list if p.name == max_votes_player), None)
            if eliminated_player:
                eliminated_player.status = "dead"
                print(f"{eliminated_player.name} has been eliminated.")
                self.update_role_count(eliminated_player.role, increment=False)
        self.check_win_conditions()

    def night_phase(self):
        """ Manages the night phase where players perform their special actions. """
        print("Night Phase: Everyone, close your eyes.")
        input("Press any key to continue...")
        self.clear_console()
        # Mafia action phase
        self.mafia_action_phase()
        # Doctor protection phase
        self.doctor_action_phase()
        # Detective investigation phase
        self.detective_action_phase()
        # Announce day and resolve night actions
        print("Everyone, open your eyes.")
        print("The day begins...")
        self.resolve_night_actions()
        # Reset night actions for all players
        for player in self.player_list:
            player.reset_night_actions()
        # Check win conditions
        self.check_win_conditions()

    def mafia_action_phase(self):
        print("Mafia, open your eyes.")
        print("Mafia, choose a player to eliminate.")
        mafia_votes = {}
        for player in self.player_list:
            if player.role == "mafia" and player.status == "alive":
                print(f"Mafia Allies: {self.mafia_ally_list(player.name)}")
                target_name = input(f"{player.name} (Mafia), choose your target: ").lower()
                target_player = next((p for p in self.player_list if p.name == target_name and p.status == "alive"), None)
                if target_player:
                    player.mafia_action(target_player)
                    mafia_votes[target_player] = mafia_votes.get(target_player, 0) + 1
                self.clear_console()
        print("Mafia, close your eyes.")
        input("Press any key to continue...")
        self.clear_console()

    def doctor_action_phase(self):
        print("Doctor, open your eyes.")
        print("Doctor, choose a player to protect.")
        for player in self.player_list:
            if player.role == "doctor" and player.status == "alive":
                target_name = input(f"{player.name} (Doctor), choose a player to protect: ").lower()
                target_player = next((p for p in self.player_list if p.name == target_name and p.status == "alive"), None)
                if target_player:
                    player.doctor_action(target_player)
                self.clear_console()
        print("Doctor, close your eyes.")
        input("Press any key to continue...")
        self.clear_console()

    def detective_action_phase(self):
        print("Detective, open your eyes.")
        print("Detective, choose a player to investigate.")
        for player in self.player_list:
            if player.role == "detective" and player.status == "alive":
                target_name = input(f"{player.name} (Detective), who do you want to investigate? ").lower()
                target_player = next((p for p in self.player_list if p.name == target_name and p.status == "alive"), None)
                if target_player:
                    player.detective_action(target_player)
                else:
                    print(f"No active player found with the name {target_name}.")
                input("Press any key to continue after reviewing the investigation results...")  # Adds a pause for visibility
                self.clear_console()
        print("Detective, close your eyes.")
        input("Press any key to continue...")
        self.clear_console()


    def resolve_night_actions(self):
        for player in self.player_list:
            if player.night_target and player.night_target.status == "alive":
                if not player.night_target.protected:
                    print(f"{player.night_target.name} was killed during the night.")
                    player.night_target.status = "dead"
                    self.update_role_count(player.night_target.role, increment=False)
                else:
                    print(f"{player.night_target.name} was protected and survived.")
                player.night_target = None  # Reset target for the next night

    def check_win_conditions(self):
        alive_mafia = sum(1 for player in self.player_list if player.role == "mafia" and player.status == "alive")
        alive_non_mafia = sum(1 for player in self.player_list if player.role != "mafia" and player.status == "alive")
        if alive_mafia == 0:
            self.gameCompleted = True
            print("Village Wins!")
            return
        if alive_mafia >= alive_non_mafia:
            self.gameCompleted = True
            print("Mafia wins!")

    def handle_game_over(self):
        """ Handles the game over process, offering restart or exit options. """
        while True:
            choice = input("Game over! Would you like to (R)estart or (E)xit? ").lower()
            if choice == 'r':
                print("Restarting the game...\n")
                self.__init__(self.num_players)  # Re-initialize the game
                self.start_game()  # Start a new game
                break
            elif choice == 'e':
                print("Thank you for playing Mafia!")
                break
            else:
                print("Invalid choice, please select 'R' or 'E'.")

    def clear_console(self):
        """ Utility function to clear the console. """
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')

    def start_game(self):
        """Main game loop that alternates between day and night phases."""
        while not self.gameCompleted:
            # Run the day phase
            self.day_phase()
            if self.gameCompleted:
                # Break if a win condition has been met
                break
            # Run the night phase
            self.night_phase()

    def mafia_ally_list(self, cur_player):
        """ Returns the list of mafia allies for the given player. """
        ally_list = []
        for player in self.player_list:
            if player.role == "mafia" and player.status == "alive" and player.name != cur_player:
                ally_list.append(player.name)
        return ", ".join(ally_list)

    def targetHistory(self, cur_player, day_vote):
        """ Stores target history for mafia members' day cycle votes. """
        history = {}
        for player in self.player_list:
            if player.role == "mafia" and player.status == "alive" and player.name != cur_player:
                history[cur_player] = day_vote
        self.mafia_votes = history
        return self.mafia_votes
