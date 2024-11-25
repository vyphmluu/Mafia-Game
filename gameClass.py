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
    def __init__(self, players, game_mode):
        self.num_players = players # Total number of players in the game
        self.num_mafia = 0 # Counter for mafia players
        self.num_doctors = 0 # Counter for doctor players
        self.num_villagers = 0 # Counter for villager players
        self.gameCompleted = False # Boolean value to indicate if the game has ended
        self.player_list = [] # List to store player objects
        self.round_cycle = 0 # Tracks if the game has gone through a full day/night cycle (for target history mafia method)
        self.mafia_votes = {}
        self.game_mode = game_mode
        self.game_difficulty = 0

    def easy_ai(self):
        random_vote = random.choice(player_list)
        return random_vote

    def ai_mode(self):
        input_flag = True
        while input_flag:
            print(f"Please Choose A Difficulty Setting:")
            print(f"1) Easy Mode")
            print(f"2) Normal Mode")
            print(f"3) Hard Mode")
            choice = input("Enter a choice: ")
            if choice in {'1', '2', '3'}:
                self.game_difficulty == int(choice)
                return self.game_difficulty
            else:
                print(f"Invalid input. Enter 1, 2, or 3.")

    # Method to add a new player to the game
    def add_player(self, name):
        """Add a new player to the game with a placeholder role."""
        # Create a new Player instance with a name and no role assigned yet
        player = Player(role=None, name=name)
        # Add the player to the player list
        self.player_list.append(player)

    def assign_villager_attribute(self):
        """Assigns a random passive attribute to a villager."""
        attributes = ["Intuition", "Suspicion Radar"]
        return random.choice(attributes)

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

            if role == "villager":
                player.attribute = self.assign_villager_attribute()
        
        # Debugging output to check balance
        print(f"Roles distribution: Mafia: {num_mafia}, Doctor: {num_doctors}, Detective: {num_detective}, Villagers: {num_villagers}")

        self.role_call()  # Perform the private role call

    def role_call(self):
        """Privately informs each player of their assigned role with double prompts for GM and player."""
        singleplayer = self.player_list[0].role.capitalize()
        if self.game_mode == 1:
            print(f"\nPlayer, your role is: {singleplayer}")
            return

        print("\nRole Call: Each player will learn their role privately.")
        input("Press Enter to begin the role call...")

        for player in self.player_list:
            if player.status == "alive":
                # Clear the console for Game Master to call the player
                self.clear_console()
                print(f"{player.name.capitalize()}, please look at the screen.")
                input("Press Enter when you are ready...")  # confirmation to call the player

                # Clear the console for the player to see their role
                self.clear_console()
                print(f"{player.name.capitalize()}, it's your turn to check your role.")
                print(f"Your role is: {player.role.capitalize()}")

                # Additional information for villagers
                if player.attribute:
                    print(f"Your special ability is: {player.attribute.capitalize()}")

                input("Press Enter when you have seen your role.")  # Player confirms they've seen the role

            else:
                print(f"{player.name.capitalize()} is not in the game.")  # Handle inactive players

        # Final screen clear after all players
        self.clear_console()
        print("Role Call is complete. All players now know their roles.")
        input("Press Enter to begin the game.")

    def update_role_count(self, role, increment=True):
        """Update the count of each role based on the player's assigned role."""
        if role == "mafia":
            # Increment or decrement the mafia count based on the `increment` flag
            self.num_mafia += 1 if increment else -1
        elif role == "doctor":
            # Increment or decrement the doctor count based on the `increment` flag
            self.num_doctors += 1 if increment else -1
        elif role == "villager":
            # Increment or decrement the villager count based on the `increment` flag
            self.num_villagers += 1 if increment else -1

    def day_phase(self):
        """Handles the day phase, allowing players to vote while displaying private role-specific information."""
        print("Day Phase: Time to vote!")
        input("Press Enter to begin the day phase...")
        self.clear_console()

        # Initialize a dictionary to store vote counts
        votes = {}

        # Call each player individually
        for player in self.player_list:
            if player.status == "alive":
                # Clear the console for privacy
                self.clear_console()
                print(f"{player.name.capitalize()}, please come to the screen.")
                input("Press Enter when the player is ready...")

                # Clear again for the player to view their private information
                self.clear_console()

                # Display private information for Mafia or special abilities
                if player.role == "mafia":
                    print(f"Your Mafia allies are: {self.mafia_ally_list(player.name)}")
                if player.attribute == "Intuition":
                    # Provide subtle hints (e.g., role probabilities for one random player)
                    hint_player = random.choice([p for p in self.player_list if p != player and p.status == "alive"])
                    hint = f"Your intuition suggests that {hint_player.name} might {'' if random.random() > 0.2 else 'NOT'} be Mafia."
                    print(f"Hint for {player.name}: {hint}")
                    input("Press Enter to continue...")

                # Display players available to vote for
                alive_players = [p.name for p in self.player_list if p.status == "alive" and p.name != player.name]
                print("Players available to vote for:", ', '.join(alive_players))

                # Prompt the player to cast their vote
                vote_for = input(f"{player.name}, who do you vote to eliminate? ").lower()
                while vote_for not in alive_players:
                    print(f"Invalid choice. Please select from: {', '.join(alive_players)}")
                    vote_for = input(f"{player.name}, who do you vote to eliminate? ").lower()

                # Record the vote
                votes[vote_for] = votes.get(vote_for, 0) + 1

                # Clear the console before transitioning back to GM
                self.clear_console()
                input("Press Enter to proceed to the next player.")
            else:
                print(f"{player.name.capitalize()} is not in the game.")

        # Determine the player with the most votes
        if votes:
            max_votes = max(votes.values())
            candidates = [name for name, count in votes.items() if count == max_votes]

            # Handle ties with random selection
            eliminated_player = random.choice(candidates) if len(candidates) > 1 else candidates[0]
            eliminated_player_obj = next((p for p in self.player_list if p.name == eliminated_player), None)

            # Eliminate the chosen player
            if eliminated_player_obj:
                eliminated_player_obj.status = "dead"
                print(f"{eliminated_player_obj.name.capitalize()} has been eliminated.")
                self.update_role_count(eliminated_player_obj.role, increment=False)

        # Check win conditions after the voting phase
        self.check_win_conditions()

    def night_phase(self):
        print("Night Phase: Everyone, close your eyes.")
        input("Press any key to continue...")
        self.clear_console()

        # Mafia Voting Phase
        print("Mafia, open your eyes.")
        print("Mafia, choose a player to eliminate.")
        
        mafia_votes = {}  # Dictionary to store votes for each target
        for player in self.player_list:
            if player.role == "mafia" and player.status == "alive":
                print(f"Mafia votes: {self.mafia_votes}")
                print(f"Mafia Allies: {self.mafia_ally_list(player.name)}")
                target_name = input(f"{player.name.capitalize()} (Mafia), choose your target: ").lower()
                target_player = next((p for p in self.player_list if p.name == target_name and p.status == "alive"), None)
                if target_player:
                    player.mafia_action(target_player)  # Mafia player uses mafia_action method
                    mafia_votes[target_player] = mafia_votes.get(target_player, 0) + 1
                self.clear_console()

        # Determine final target with most votes
        target = None
        if mafia_votes:
            max_votes = max(mafia_votes.values())
            targets_with_max_votes = [p for p, votes in mafia_votes.items() if votes == max_votes]
            target = random.choice(targets_with_max_votes) if len(targets_with_max_votes) > 1 else targets_with_max_votes[0]
            print(f"Mafia has chosen to target {target.name}.")  # Announce chosen target

        # Close Mafia phase
        print("Mafia, close your eyes.")
        input("Press any key to continue...")
        self.clear_console()

        # Doctor Voting Phase
        print("Doctor, open your eyes.")
        print("Doctor, choose a player to protect.")

        for player in self.player_list:
            if player.role == "doctor" and player.status == "alive":
                target_name = input(f"{player.name} (Doctor), choose a player to protect: ").lower()
                target_player = next((p for p in self.player_list if p.name == target_name and p.status == "alive"), None)
                if target_player:
                    player.doctor_action(target_player)  # Doctor uses doctor_action method
                self.clear_console()

        # Close Doctor phase
        print("Doctor, close your eyes.")
        input("Press any key to continue...")
        self.clear_console()

        # Villager Suspicion Radar Phase
        print("Villagers with Suspicion Radar, open your eyes.")
        for player in self.player_list:
            if player.role == "villager" and player.status == "alive" and player.attribute == "Suspicion Radar":
                if player.name in mafia_votes:
                    print(f"{player.name}, your Suspicion Radar detects that someone voted for you last night.")
                else:
                    print(f"{player.name}, your Suspicion Radar is calm tonight.")
                input("Press Enter to continue...")
                self.clear_console()

        print("Villagers, close your eyes.")
        input("Press any key to continue...")
        self.clear_console()

        # Announce day and resolve night actions
        print("Everyone, open your eyes.")
        print("The day begins...")

        # Resolve night actions based on Mafia target and Doctor protection
        if target and not target.protected:
            target.status = "dead"  # Mark as dead if unprotected
            print(f"{target.name} was killed during the night.")
        elif target and target.protected:
            print(f"{target.name} was protected by the Doctor and survived the night.")

        # Reset night actions for all players
        for player in self.player_list:
            player.reset_night_actions()

        # Check win conditions
        self.check_win_conditions()

    def check_win_conditions(self):
        # Check if the village wins (all mafia members are eliminated)
        if self.num_mafia == 0:
            # Set the game completion flag to true, ending the game loop
            self.gameCompleted = True
            # Display the victory message for the village
            print("Village Wins!")

        # Check if the mafia wins (mafia outnumber or equal the villagers and doctors)
        elif self.num_mafia >= (self.num_villagers + self.num_doctors):
            # Set the game completion flag to true, ending the game loop
            self.gameCompleted = True
            # Display the victory message for the mafia
            print("Mafia wins!")

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

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

    def clear_console(self):
        """Utility function to clear the console."""
        # Clear console for Windows
        if os.name == 'nt':
            os.system('cls')
        # Clear console for MacOS and Linux
        else:
            os.system('clear')

    def fullRound(self):
        self.night_phase()
        if not self.game_over:
            self.day_phase()

    # Returns the list of mafia allies
    def mafia_ally_list(self, cur_player):
        ally_list = []
        for player in self.player_list:
            if player.role == "mafia" and player.status == "alive" and player.name != cur_player:
                ally_list.append(player.name)
        return ", ".join(ally_list)

    def targetHistory(self, cur_player, day_vote):
        history = {} # store mafia member's day cycle votes
        for player in self.player_list:
            if player.role == "mafia" and player.status == "alive" and player.name != cur_player:
                history[cur_player] = day_vote
        self.mafia_votes = history
        return self.mafia_votes
