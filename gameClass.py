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
import tkinter as tk
from tkinter import messagebox

class GameClass:
    def __init__(self, players, game_mode, frame, app):
        self.frame = frame # Reuse root window to avoid opening new one (passed through parameter)
        self.app = app # Store the reference to MafiaGameApp
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
        self.main_player 

    def clear_frame(self):
        """Clears current frame"""
        for widget in self.frame.winfo_children():
            widget.destroy()

    def singleplayer_clear_frame_ui(self):
        """After Singleplayer game begins maintains relevant info on screen but clears the rest"""
        self.clear_frame()
        player_role_message = f"Your Role: {self.player_list[0].role.capitalize()}"
        self.message_label = tk.Label(self.frame, text=player_role_message)
        self.message_label.pack()
        return


    def easy_ai(self, cur_list):
        """Randomly selects a target from the current list."""
        return random.choice(cur_list)

    
    def normal_ai(self, role, player, cur_list):
        """Makes informed decisions based on available game information."""
        if role == 'mafia':
            # Avoid targeting other Mafia; focus on non-Mafia players
            non_mafia = [p for p in cur_list if p.role != 'mafia' and p.status == 'alive']
            return random.choice(non_mafia)
        elif role == 'doctor':
            # Protect players at higher risk (non-Mafia, especially Detective)
            return max(cur_list, key=lambda x: x.status)  # Dummy logic; refine as needed
        elif role == 'detective':
            # Investigate new, uninvestigated players
            uninvestigated = [p for p in cur_list if p not in player.investigated]
            return random.choice(uninvestigated) if uninvestigated else random.choice(cur_list)
        elif role == 'villager':
            # Vote for suspected Mafia
            suspected_mafia = [p for p in cur_list if self.is_suspected_mafia(p)]
            return random.choice(suspected_mafia) if suspected_mafia else random.choice(cur_list)
        return random.choice(cur_list)  # Fallback for edge cases


    def hard_ai(self, role, player, cur_list):
        """Makes optimal decisions for each role."""
        if role == 'mafia':
            # Prioritize critical roles (Doctor, Detective) over Villagers
            high_value_targets = [p for p in cur_list if p.role in ['doctor', 'detective']]
            return random.choice(high_value_targets) if high_value_targets else random.choice(cur_list)
        elif role == 'doctor':
            # Protect high-value roles (Detective or critical Villager)
            protect_targets = [p for p in cur_list if p.role in ['detective', 'villager'] and p.status == 'alive']
            return max(protect_targets, key=lambda x: x.status)  # Prioritize active players
        elif role == 'detective':
            # Check uninvestigated or suspicious players
            unknown_roles = [p for p in cur_list if p.role is None and p.status == 'alive']
            return random.choice(unknown_roles) if unknown_roles else random.choice(cur_list)
        elif role == 'villager':
            # Vote strategically against known Mafia
            return self.vote_mafia_strategy(cur_list)
        return random.choice(cur_list)



        # Automated day phase voting based on current knowledge
        self.simulate_strategic_voting()
        
    def assign_villager_attribute(self):
        attributes = ["Intuition", "Suspicion Radar"]
        return random.choice(attributes)

    def villager_intuition(self, villager):
        potential_targets = [p for p in self.player_list if p.status == 'alive' and p != villager]
        if potential_targets:
            target = random.choice(potential_targets)
            is_correct_hint = random.random() > 0.5
            hint_role = "Mafia" if is_correct_hint and target.role == 'mafia' else "Not Mafia"
            hint_role_text = f"Hint for {villager.name}: {target.name} might be {hint_role}."
            hint_role_message = tk.Label(self.frame, text=hint_role_text)
            hint_role_message.pack()
            print(f"Hint for {villager.name}: {target.name} might be {hint_role}.")


    def suspicion_radar(self, villager, mafia_votes):
        if villager.name in mafia_votes:
            suspicion_radar_text = f"Suspicion Radar Alert: {villager.name}, the Mafia may have targeted you last night."
            suspicion_radar_message = tk.Label(self.frame, text=suspicion_radar_text)
            suspicion_radar_message.pack()
            print(f"Suspicion Radar Alert: {villager.name}, the Mafia may have targeted you last night.")
        else:
            suspicion_radar_text = f"Suspicion Radar: {villager.name}, no suspicious activity detected."
            suspicion_radar_message = tk.Label(self.frame, text=suspicion_radar_text)
            suspicion_radar_message.pack()
            print(f"Suspicion Radar: {villager.name}, no suspicious activity detected.")


    def activate_villager_attributes(self):
        for player in self.player_list:
            if player.role == "villager" and player.status == "alive":
                if player.attribute == "Intuition":
                    self.villager_intuition(player)
                elif player.attribute == "Suspicion Radar":
                    self.suspicion_radar(player, self.mafia_votes)

    def resolve_mafia_votes(self, mafia_votes):
        if mafia_votes:
            max_votes = max(mafia_votes.values())
            targets = [p for p, count in mafia_votes.items() if count == max_votes]
            target = random.choice(targets)
            target_obj = next((p for p in self.player_list if p.name == target), None)
            if target_obj and not target_obj.protected:
                target_obj.status = "dead"
                print(f"{target_obj.name} was killed during the night.")
            elif target_obj and target_obj.protected:
                print(f"{target_obj.name} was protected by the Doctor and survived.")

    
    def select_priority_target(self, targets):
        # Mafia targets critical roles first, then any non-mafia
        priority_targets = [p for p in targets if p.role in ['detective', 'doctor']]
        return random.choice(priority_targets) if priority_targets else random.choice(targets)

    def select_protective_target(self, targets):
        # Doctor protects based on previous targeting or critical role
        return max(targets, key=lambda x: (self.target_history.get(x.name, 0), x.role in ['detective']))

    def detective_select_target(self, targets):
        # Detective checks a new player each night, prioritizing those with suspicious behavior
        return random.choice(targets)  # Replace with more nuanced logic based on behavior

    def simulate_strategic_voting(self):
        for player in self.player_list:
            if player.status == 'alive':
                player.vote(self.strategic_vote(player))

    def strategic_vote(self, player):
        # Players vote based on detected Mafia or most suspicious behavior
        if player.role == 'villager':
            suspected_mafia = [p for p in self.player_list if self.is_suspected_mafia(p)]
            return random.choice(suspected_mafia) if suspected_mafia else None
        return None

    def is_suspected_mafia(self, player):
        # Example placeholder for suspicion logic
        return player.role == 'mafia' and player.has_been_suspicious
        
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

    def main_player(self, name):
        self.main_player = name
        return self.main_player
    
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
        attributes = ["Intuition", "Suspicion Radar"]  # Villager attributes
        for player in self.player_list:
            role = roles.pop()  # Assign a role from the shuffled list
            player.role = role
            self.update_role_count(role, increment=True)

            if role == "villager":
                if attributes:
                    player.attribute = attributes.pop(0)  # Assign unique attribute
                else:
                    player.attribute = None  # No attribute left to assign

        # Debugging output to check balance
        self.clear_frame()
        role_distribution_message = f"Roles Distribution: Mafia: {num_mafia}, Doctor: {num_doctors}, Detective: {num_detective}, Villagers: {num_villagers}"
        self.message_label = tk.Label(self.frame, text=role_distribution_message)
        self.message_label.pack()
        print(f"Roles distribution: Mafia: {num_mafia}, Doctor: {num_doctors}, Detective: {num_detective}, Villagers: {num_villagers}")

        self.role_call()  # Perform the private role call

    def role_call(self):
        """Trigger the role call through the appropriate method."""
        if hasattr(self.app, "start_role_call"):
            self.app.start_role_call(self)
        elif hasattr(self, "start_role_call"):
            self.start_role_call(self)
        else:
            raise AttributeError("Neither the app nor the current class has a start_role_call method.")

    def update_role_count(self, role, increment=True):
        """Update the count of each role based on the player's assigned role."""
        if role == "mafia":
            # Increment or decrement the mafia count based on the increment flag
            self.num_mafia += 1 if increment else -1
        elif role == "doctor":
            # Increment or decrement the doctor count based on the increment flag
            self.num_doctors += 1 if increment else -1
        elif role == "villager":
            # Increment or decrement the villager count based on the increment flag
            self.num_villagers += 1 if increment else -1

    def singleplayer_voting_phase(self):
        self.singleplayer_clear_frame_ui()
       
        main_player = self.player_list[0]
        alive_players = [p.name for p in self.player_list if p.status == "alive" and p.name != main_player.name]

        if main_player.role == "mafia":
            mafia_allies_text = f"Your mafia allies are: {self.mafia_ally_list(main_player.name)}"
            mafia_allies_message = tk.Label(self.frame, text=mafia_allies_text)
            mafia_allies_message.pack()
        elif main_player.attribute == "Intuition":
            self.villager_intuition(main_player)
        elif main_player.attribute == "Suspicion Radar":
            self.suspicion_radar(main_player, self.mafia_votes)

        alive_players_text = f"Players available to vote for: ", ', '.join(alive_players)
        alive_players_message = tk.Label(self.frame, text=alive_players_text)
        alive_players_message.pack()
        
        vote_entry = tk.Entry(self.frame)
        vote_entry.pack()

        vote_for = vote_entry.get().lower()
        if vote_for not in [p.lower() for p in alive_players]:
            messagebox.showerror(f"Invalid choice. Please select from: {', '.join(alive_players)}")
        else:
            messagebox.showinfo(f"Vote submitted. You voted to eliminate {vote_for.capitalize()}.")

        vote_button = tk.Button(self.frame, text="Vote", command=lambda: self.singleplayer_submit_vote(vote_for))
        vote_button.pack()

    def singleplayer_submit_vote(self, vote_for):
        votes = {}
        votes[vote_for] = votes.get(vote_for, 0) + 1
        votes = self.easyAI_submit_vote(votes)
        if votes:
            max_votes = max(votes.values())
            candidates = [name for name, count in votes.items() if count == max_votes]

            eliminated_player = random.choice(candidates) if len(candidates) > 1 else candidates[0]
            eliminated_player_obj = next((p for p in self.player_list if p.name.lower() == eliminated_player.lower()), None)

            if eliminated_player_obj:
                eliminated_player_obj.status = "dead"
                eliminated_text = f"{eliminated_player_obj.name.capitalize()} has been eliminated."
                eliminated_message = tk.Label(self.frame, text=eliminated_text)
                eliminated_message.pack()
                self.update_role_count(eliminated_player_obj.role, increment=False)
        self.check_win_conditions()
        button = tk.Button(self.frame, text="Night Phase: Everyone, close your eyes.", command=self.night_phase)
        button.pack()

    def easyAI_submit_vote(self, votes):
        self.singleplayer_clear_frame_ui()
        alive_players = [p.name for p in self.player_list if p.status == "alive" and p.name != self.player_list[0].name]
        for p in alive_players:
            vote_for = self.easy_ai(alive_players)
            votes[vote_for] = votes.get(vote_for, 0) + 1
            vote_text = f"{p} (AI) votes for {vote_for.capitalize()}."
            vote_message = tk.Label(self.frame, text=vote_text)
            vote_message.pack()
        return votes



    def day_phase(self):
        """Handles the day phase, allowing players to vote while displaying private role-specific information."""
        day_phase_message = tk.Label(self.frame, text="Day Phase: Time to vote!")
        day_phase_message.pack()
        continue_button = tk.Button(self.frame, text="Enter Day Phase", command=self.singleplayer_voting_phase)
        continue_button.pack()
        print("Day Phase: Time to vote!")
        input("Press Enter to begin the day phase...")
        self.clear_console()

        # Dictionary to store votes
        votes = {}

        # Call each player for their turn
        for player in self.player_list:
            if player.status == "alive":
                if self.game_mode == 2 or (self.game_mode == 1 and player.name == self.player_list[0].name):
                    # Clear the console for privacy
                    self.clear_console()
                    if self.game_mode == 2:
                        print(f"{player.name.capitalize()}, please come to the screen.")
                        input("Press Enter when the player is ready...")

                        # Clear again for the player to view their private information
                        self.clear_console()

                # Display private information based on role or attributes
                if player.role == "mafia":
                    print(f"Your Mafia allies are: {self.mafia_ally_list(player.name)}")
                elif player.attribute == "Intuition":
                    self.villager_intuition(player)
                elif player.attribute == "Suspicion Radar":
                    self.suspicion_radar(player, self.mafia_votes)

                # Show available players to vote for
                alive_players = [p.name for p in self.player_list if p.status == "alive" and p.name != player.name]
                print("Players available to vote for:", ', '.join(alive_players))

                # Voting process
                if self.game_mode == 2 or (self.game_mode == 1 and player.name == self.main_player):
                    vote_entry = tk.Entry(self.frame)
                    vote_entry.pack()

                    vote_for = input(f"{player.name}, who do you vote to eliminate? ").lower()
                    while vote_for not in [p.lower() for p in alive_players]:
                        print(f"Invalid choice. Please select from: {', '.join(alive_players)}")
                        vote_for = input(f"{player.name}, who do you vote to eliminate? ").lower()

                    # Record the vote
                    votes[vote_for] = votes.get(vote_for, 0) + 1
                elif self.game_mode == 1 and player.name != self.main_player:
                    vote_for = self.easy_ai(alive_players)
                    votes[vote_for] = votes.get(vote_for, 0) + 1
                    print(f"{player.name} (AI) votes for {vote_for.capitalize()}.")

                # Clear the console before transitioning to the next player
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
            eliminated_player_obj = next((p for p in self.player_list if p.name.lower() == eliminated_player.lower()), None)

            # Eliminate the chosen player
            if eliminated_player_obj:
                eliminated_player_obj.status = "dead"
                print(f"{eliminated_player_obj.name.capitalize()} has been eliminated.")
                self.update_role_count(eliminated_player_obj.role, increment=False)

        # Check win conditions after the voting phase
        self.check_win_conditions()


    def night_phase(self):
        self.singleplayer_clear_frame_ui()
        alive_players = [p.name for p in self.player_list if p.status == "alive" and p.name != self.player_list[0].name]
        night_phase_message = tk.Label(self.frame, text="Night Phase!")
        night_phase_message.pack()
        print("Night Phase: Everyone, close your eyes.")
        #input("Press any key to continue...")
        self.clear_console()

        # Mafia Voting Phase
        mafia_awake_message = tk.Label(self.frame, text="Mafia, open your eyes.\n Choose a player to eliminate.")
        mafia_awake_message.pack()
        print("Mafia, open your eyes.")
        print("Mafia, choose a player to eliminate.")
        player_list_text = f"Players: {alive_players}"
        player_list_message = tk.Label(self.frame, text=player_list_text)
        player_list_message.pack()
        
        mafia_votes = {}  # Dictionary to store votes for each target
        for player in self.player_list:
            if player.role == "mafia" and player.status == "alive":
                mafia_votes_text = f"Mafia votes: {self.mafia_votes}"
                mafia_votes_message = tk.Label(self.frame, text=mafia_votes_text)
                mafia_votes_message.pack()
                print(f"Mafia votes: {self.mafia_votes}")
                mafia_allies_text = f"Mafia Allies: {self.mafia_ally_list(player.name)}"
                mafia_allies_message = tk.Label(self.frame, text=mafia_allies_text)
                mafia_allies_message.pack()
                print(f"Mafia Allies: {self.mafia_ally_list(player.name)}")
                target_name_entry = tk.Entry(self.frame)
                target_name_entry.pack()
                #target_name = input(f"{player.name.capitalize()} (Mafia), choose your target: ").lower()
                """NEEDS A BUTTON for input"""
                mafia_vote_button = tk.Button(self.frame, text="Vote", command=self.singleplayer_clear_frame_ui)
                mafia_vote_button.pack()

                if target_name_entry:
                    target_player = next((p for p in self.player_list if p.name == target_name_entry and p.status == "alive"), None)
                if target_name:
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
            target_announcement_text = f"Mafia has chosen to target {target.name}."
            target_announcement_message = tk.Label(self.frame, text=target_announcement_text)
            target_announcement_message.pack()
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
        """Checks if a win condition is met."""
        # Check if the village wins (all mafia members are eliminated)
        if self.num_mafia == 0:
            self.gameCompleted = True
            self.show_winning_team_screen("Village")
            return True  # Stop further processing

        # Check if the mafia wins (mafia outnumber or equal the villagers and doctors)
        elif self.num_mafia >= (self.num_villagers + self.num_doctors):
            self.gameCompleted = True
            self.show_winning_team_screen("Mafia")
            return True  # Stop further processing

        return False
    
    def show_winning_team_screen(self, winning_team):
        """Displays the screen announcing the winning team."""
        self.clear_frame()

        # Display the winning team
        tk.Label(
            self.frame,
            text=f"{winning_team} Wins!",
            font=("Arial", 20),
            fg="green" if winning_team == "Village" else "red"
        ).pack(pady=20)

        # Display a message with options
        tk.Label(
            self.frame,
            text="Congratulations to the winning team! Would you like to play again?",
            font=("Arial", 14)
        ).pack(pady=10)

        # Add buttons for replaying or exiting
        tk.Button(
            self.frame,
            text="Play Again",
            command=self.app.create_main_menu  # Navigate back to the main menu
        ).pack(pady=10)

        tk.Button(
            self.frame,
            text="Exit",
            command=lambda: self.app.root.quit()
        ).pack(pady=10)

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
    
    def multiplayer_day_phase(self):
        """Handles the day phase for multiplayer mode, allowing players to vote."""
        self.clear_frame()
        tk.Label(self.frame, text="Day Phase: Time to vote!", font=("Arial", 14)).pack(pady=10)

        # Filter alive players for the voting process
        self.votes = {}
        self.current_voter_index = 0
        self.alive_players = [p for p in self.player_list if p.status == "alive"]  # Only alive players can vote

        if self.alive_players:
            self.multiplayer_next_voter()
        else:
            messagebox.showinfo("Error", "No players alive to vote!")

    def show_multiplayer_voting_screen(self, voter):
        """Show the voting screen for the current player in multiplayer."""
        self.clear_frame()

        # Display the voter's name and instruction
        tk.Label(self.frame, text=f"{voter.name.capitalize()}, it's your turn to vote!", font=("Arial", 14)).pack(pady=10)

        # List of alive players to vote for
        self.vote_target = tk.StringVar()
        alive_targets = [p for p in self.alive_players if p.name != voter.name]  # Only allow votes for other alive players

        if not alive_targets:
            tk.Label(self.frame, text="No valid targets to vote for!", font=("Arial", 12)).pack(pady=10)
            self.current_voter_index += 1
            self.multiplayer_next_voter()  # Move to the next voter
            return

        for player in alive_targets:
            tk.Radiobutton(
                self.frame,
                text=player.name.capitalize(),
                variable=self.vote_target,
                value=player.name
            ).pack(anchor="w")

        # Submit vote button
        tk.Button(
            self.frame,
            text="Submit Vote",
            command=lambda: self.submit_multiplayer_vote(voter)
        ).pack(pady=10)

    def submit_multiplayer_vote(self, voter):
        """Record the current player's vote and move to the next voter."""
        selected_player = self.vote_target.get()

        if not selected_player:
            messagebox.showerror("Error", "You must select a player to vote!")
            return

        # Record the vote
        self.votes[selected_player] = self.votes.get(selected_player, 0) + 1

        # Move to the next voter
        self.current_voter_index += 1

        if self.current_voter_index < len(self.player_list):
            # Show the voting screen for the next voter
            next_voter = self.player_list[self.current_voter_index]
            self.show_multiplayer_voting_screen(next_voter)
        else:
            # All votes are in, tally the votes
            self.tally_multiplayer_votes()

    def multiplayer_next_voter(self):
        """Handles transitioning to the next voter in the multiplayer day phase."""
        # Check if there are more voters in the queue
        if self.current_voter_index < len(self.alive_players):
            current_voter = self.alive_players[self.current_voter_index]
            self.show_multiplayer_voting_screen(current_voter)
        else:
            # If all voters have voted, tally the votes
            self.tally_multiplayer_votes()

    def tally_multiplayer_votes(self):
        """Tally votes and eliminate the player with the most votes."""
        self.clear_frame()

        if self.votes:
            # Find the player(s) with the most votes
            max_votes = max(self.votes.values())
            candidates = [name for name, count in self.votes.items() if count == max_votes]

            # Handle ties with random selection
            eliminated_player_name = random.choice(candidates) if len(candidates) > 1 else candidates[0]
            eliminated_player = next(p for p in self.player_list if p.name == eliminated_player_name)

            # Eliminate the chosen player
            eliminated_player.status = "dead"
            tk.Label(self.frame, text=f"{eliminated_player.name.capitalize()} has been eliminated!", font=("Arial", 16)).pack(pady=20)

            # Update role counts
            self.update_role_count(eliminated_player.role, increment=False)

            # Check win conditions before proceeding to the next phase
            if self.check_win_conditions():
                return  # If a win condition is met, stop further processing
        
        # Proceed to the next phase
        tk.Button(
            self.frame,
            text="Proceed to Night Phase",
            command=self.multiplayer_night_phase
        ).pack(pady=10)

    def multiplayer_night_phase(self):
        """Handles the Night Phase for multiplayer mode."""
        self.clear_frame()

        # Start with the Mafia's phase
        self.night_phase_message = tk.Label(self.frame, text="Night Phase: Everyone, close your eyes.", font=("Arial", 16))
        self.night_phase_message.pack(pady=10)

        tk.Button(
            self.frame,
            text="Begin Mafia Phase",
            command=self.mafia_phase
        ).pack(pady=10)

    def mafia_phase(self):
        """Handles the Mafia's voting phase."""
        self.clear_frame()
        tk.Label(self.frame, text="Mafia, open your eyes.", font=("Arial", 16)).pack(pady=10)
        tk.Label(self.frame, text="Mafia, choose a player to eliminate.", font=("Arial", 12)).pack(pady=10)

        # Create a dictionary for Mafia votes
        self.mafia_votes = {}
        self.current_mafia_index = 0  # Start with the first Mafia player
        self.show_mafia_voting_screen()
    
    def show_mafia_voting_screen(self):
        """Display the voting screen for the current Mafia player."""
        mafia_player = [
            p for p in self.player_list if p.role == "mafia" and p.status == "alive"
        ][self.current_mafia_index]

        self.clear_frame()
        tk.Label(self.frame, text=f"{mafia_player.name.capitalize()}, it's your turn to vote!", font=("Arial", 14)).pack(pady=10)

        # Voting options for Mafia
        alive_players = [p for p in self.player_list if p.status == "alive" and p.name != mafia_player.name]
        self.vote_target = tk.StringVar()

        for player in alive_players:
            tk.Radiobutton(
                self.frame,
                text=player.name.capitalize(),
                variable=self.vote_target,
                value=player.name
            ).pack(anchor="w")

        tk.Button(
            self.frame,
            text="Submit Vote",
            command=lambda: self.submit_mafia_vote(mafia_player)
        ).pack(pady=10)

    def submit_mafia_vote(self, mafia_player):
        """Record the Mafia player's vote and move to the next Mafia player."""
        selected_player = self.vote_target.get()

        if not selected_player:
            messagebox.showerror("Error", "You must select a player to vote!")
            return

        # Record the vote
        self.mafia_votes[selected_player] = self.mafia_votes.get(selected_player, 0) + 1

        # Move to the next Mafia player
        self.current_mafia_index += 1
        mafia_players = [p for p in self.player_list if p.role == "mafia" and p.status == "alive"]

        if self.current_mafia_index < len(mafia_players):
            self.show_mafia_voting_screen()
        else:
            self.resolve_mafia_votes()

    def resolve_mafia_votes(self):
        """Determine and announce the Mafia's chosen target."""
        self.clear_frame()
        if self.mafia_votes:
            max_votes = max(self.mafia_votes.values())
            targets_with_max_votes = [name for name, count in self.mafia_votes.items() if count == max_votes]
            self.mafia_target = random.choice(targets_with_max_votes)

            tk.Label(
                self.frame,
                text=f"Mafia has chosen to target {self.mafia_target.capitalize()}.",
                font=("Arial", 16)
            ).pack(pady=10)

        tk.Button(
            self.frame,
            text="Proceed to Doctor Phase",
            command=self.doctor_phase
        ).pack(pady=10)

    def doctor_phase(self):
        """Handles the Doctor's protection phase."""
        self.clear_frame()
        tk.Label(self.frame, text="Doctor, open your eyes.", font=("Arial", 16)).pack(pady=10)
        tk.Label(self.frame, text="Doctor, choose a player to protect.", font=("Arial", 12)).pack(pady=10)

        # Display Doctor voting screen
        self.show_doctor_screen()

    def show_doctor_screen(self):
        """Display the screen for the Doctor to choose a player to protect."""
        doctor_player = next((p for p in self.player_list if p.role == "doctor" and p.status == "alive"), None)

        if not doctor_player:
            self.proceed_to_villager_phase()
            return

        self.clear_frame()
        tk.Label(self.frame, text=f"{doctor_player.name.capitalize()}, it's your turn to protect a player!", font=("Arial", 14)).pack(pady=10)

        # List of alive players
        self.protect_target = tk.StringVar()
        alive_players = [p for p in self.player_list if p.status == "alive"]

        for player in alive_players:
            tk.Radiobutton(
                self.frame,
                text=player.name.capitalize(),
                variable=self.protect_target,
                value=player.name
            ).pack(anchor="w")

        tk.Button(
            self.frame,
            text="Submit Protection",
            command=self.submit_doctor_protection
        ).pack(pady=10)

    def submit_doctor_protection(self):
        """Record the Doctor's protection choice."""
        selected_player = self.protect_target.get()

        if not selected_player:
            messagebox.showerror("Error", "You must select a player to protect!")
            return

        # Protect the selected player
        protected_player = next(p for p in self.player_list if p.name == selected_player)
        protected_player.protected = True

        self.proceed_to_villager_phase()

    def proceed_to_villager_phase(self):
        """Proceed to the Villager Suspicion Radar phase."""
        self.clear_frame()
        tk.Label(self.frame, text="Villagers with Suspicion Radar, open your eyes.", font=("Arial", 16)).pack(pady=10)

        for player in self.player_list:
            if player.role == "villager" and player.status == "alive" and player.attribute == "Suspicion Radar":
                if player.name in self.mafia_votes:
                    tk.Label(
                        self.frame,
                        text=f"{player.name.capitalize()}, your Suspicion Radar detects that someone targeted you last night.",
                        font=("Arial", 12)
                    ).pack(pady=5)
                else:
                    tk.Label(
                        self.frame,
                        text=f"{player.name.capitalize()}, your Suspicion Radar is calm tonight.",
                        font=("Arial", 12)
                    ).pack(pady=5)

        tk.Button(
            self.frame,
            text="Proceed to Day Phase",
            command=self.resolve_night_phase
        ).pack(pady=10)

    def resolve_night_phase(self):
        """Resolve the Night Phase actions and announce the results."""
        self.clear_frame()

        if self.mafia_target:
            target_player = next(p for p in self.player_list if p.name == self.mafia_target)
            if target_player.protected:
                tk.Label(self.frame, text=f"{target_player.name.capitalize()} was protected by the Doctor and survived!", font=("Arial", 14)).pack(pady=10)
            else:
                target_player.status = "dead"
                tk.Label(self.frame, text=f"{target_player.name.capitalize()} was killed during the night!", font=("Arial", 14)).pack(pady=10)

        # Reset night actions
        for player in self.player_list:
            player.reset_night_actions()

        # Check win conditions before transitioning to the next day
        if self.check_win_conditions():
            return  # If a win condition is met, stop further processing
    
        tk.Button(
            self.frame,
            text="Proceed to Day Phase",
            command=self.multiplayer_day_phase
        ).pack(pady=10)