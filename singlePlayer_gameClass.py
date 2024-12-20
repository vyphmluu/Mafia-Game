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
import sys
import random
import tkinter as tk

class SinglePlayerMode:
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

    #def detective_select_target(self, targets):
        # Detective checks a new player each night, prioritizing those with suspicious behavior
        #return random.choice(targets)  # Replace with more nuanced logic based on behavior

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
        num_detective = 0 if self.num_players >= 5 else 0  # 1 detective for 5+ players
        num_doctors = 1 if self.num_players >= 4 else 0  # 1 doctor for 4+ players
        num_villagers = self.num_players - (num_mafia + num_detective + num_doctors)  # Remaining players are villagers

        # Create a role list based on calculated numbers
        roles = (
            ['mafia'] * num_mafia +
            #['detective'] * num_detective +
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

    # UI Transition In Progress
    def role_call(self):
        """Trigger the UI-based role call in MafiaGameApp."""
        if self.game_mode == 2:  # Multiplayer mode
            # Notify the app to start the role call UI
            self.app.start_role_call(self)

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
        #if vote_for not in [p.lower() for p in alive_players]:
            #messagebox.showerror(f"Invalid choice. Please select from: {', '.join(alive_players)}")
        #else:
            #messagebox.showinfo(f"Vote submitted. You voted to eliminate {vote_for.capitalize()}.")

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
        self.check_win_conditions("day")
        #button = tk.Button(self.frame, text="Night Phase: Everyone, close your eyes.", command=self.check_win_conditions("day"))
        #button.pack()

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

    """ =============================================================== NIGHT PHASE CODE ======================================================================= """

    def night_phase(self):
        self.singleplayer_clear_frame_ui()
        alive_players = [p.name for p in self.player_list if p.status == "alive" and p.name != self.player_list[0].name]
        night_phase_message = tk.Label(self.frame, text="Night Phase!")
        night_phase_message.pack()
        mafia_votes = {}

        # AI voting first
        for player in self.player_list:
            if player.role == "mafia" and player.status == "alive":
                target_name = self.easy_ai(alive_players)
                target_player = next((p for p in self.player_list if p.name == target_name and p.status == "alive"), None)
                player.mafia_action(target_player)
                mafia_votes[target_name] = mafia_votes.get(target_player, 0) + 1
                target = target_player
            elif player.role == "doctor":
                target_name = self.easy_ai(alive_players)
                target_player = next((p for p in self.player_list if p.name == target_name and p.status == "alive"), None)
                player.doctor_action(target_player)
                target = target_player
            else:
                pass



        if self.player_list[0].role == "mafia":
            button = tk.Button(self.frame, text="Close your eyes...", command=lambda: self.night_phase_mafia(alive_players, target))
            button.pack()
        elif self.player_list[0].role == "doctor":
            button = tk.Button(self.frame, text="Close your eyes...", command=lambda: self.night_phase_doctor(alive_players, target))
            button.pack()
        elif self.player_list[0].role == "villager":
            button = tk.Button(self.frame, text="Close your eyes...", command=lambda: self.night_phase_villager(alive_players, mafia_votes, target))
            button.pack()
        #else:
            #button = tk.Button(self.frame, text="Close your eyes...", command=lambda: self.night_phase_detective(alive_players, target))
            #button.pack()

    def night_phase_mafia(self, alive_players, target):
        # Mafia Voting Phase
        self.singleplayer_clear_frame_ui()
        mafia_awake_message = tk.Label(self.frame, text="Mafia, open your eyes.\n Choose a player to eliminate.")
        mafia_awake_message.pack()
        print("Mafia, open your eyes.")
        print("Mafia, choose a player to eliminate.")
        player_list_text = f"Players: {alive_players}"
        player_list_message = tk.Label(self.frame, text=player_list_text)
        player_list_message.pack()
        
        mafia_votes = {}  # Dictionary to store votes for each target
        for player in self.player_list:
            if (player.role == "mafia" and player.status == "alive" and self.game_mode == 2) or (player.name == self.player_list[0].name):
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

                if target_name_entry:
                    target_player = next((p for p in self.player_list if p.name == target_name_entry and p.status == "alive"), None)
                #if target_name:
                    #target_player = next((p for p in self.player_list if p.name == target_name and p.status == "alive"), None)
                
                if target_player:
                    player.mafia_action(target_player)  # Mafia player uses mafia_action method
                    mafia_votes[target_player] = mafia_votes.get(target_player, 0) + 1
                mafia_vote_button = tk.Button(self.frame, text="Vote", command=lambda: self.final_mafia_vote(alive_players, mafia_votes, target))
                mafia_vote_button.pack()

    def final_mafia_vote(self, alive_players, mafia_votes, target):
        # Determine final target with most votes
        self.singleplayer_clear_frame_ui()
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
        button = tk.Button(self.frame, text="Mafia, close your eyes...", command=lambda: self.conclude_night_phase(target))
        button.pack()
        #input("Press any key to continue...")

    def night_phase_doctor(self, alive_players, target):
        self.singleplayer_clear_frame_ui()
        # Doctor Voting Phase
        print("Doctor, open your eyes.")
        print("Doctor, choose a player to protect.")
        doctor_vote_message = tk.Label(self.frame, text="Doctor, open your eyes.\nDoctor, choose a player to protect.")
        doctor_vote_message.pack()
        doctors_list = [p for p in alive_players]
        doctor_list_text = f"Players Alive: {doctors_list}"
        doctor_list_message = tk.Label(self.frame, text=doctor_list_text)
        doctor_list_message.pack()


        for player in self.player_list:
            if player.role == "doctor" and player.status == "alive":
                #target_name = input(f"{player.name} (Doctor), choose a player to protect: ").lower()
                target_name_entry = tk.Entry(self.frame)
                target_name_entry.pack()
                target_player = next((p for p in self.player_list if p.name == target_name_entry and p.status == "alive"), None)

                if target_player:
                    player.doctor_action(target_player)  # Doctor uses doctor_action method
                button = tk.Button(self.frame, text="Vote", command=lambda: self.final_doctor_vote(target))
                button.pack()

    def final_doctor_vote(self, target):
        # Close Doctor phase
        self.singleplayer_clear_frame_ui()
        print("Doctor, close your eyes.")
        button = tk.Button(self.frame, text="Doctor, close your eyes...", command=lambda: self.conclude_night_phase(target))
        button.pack()

    def night_phase_villager(self, alive_players, mafia_votes, target):
        #input("Press any key to continue...")
        self.singleplayer_clear_frame_ui()

        # Villager Suspicion Radar Phase
        print("Villagers with Suspicion Radar, open your eyes.")
        message = tk.Label(self.frame, text="Villager with Suspicion Radar, open your eyes...")
        message.pack()

        for player in self.player_list:
            print(player.name, self.player_list[0].name)
            if player.role == "villager" and player.status == "alive" and player.attribute == "Suspicion Radar" and player.name == self.player_list[0].name:
                if player.name in mafia_votes:
                    print(f"{self.main_player.name}, your Suspicion Radar detects that someone voted for you last night.")
                    detect_text = f"{self.main_player.name}, your Suspicion Radar detects that someone voted for you last night."
                    detect_message = tk.Label(self.frame, text=detect_text)
                    detect_message.pack()
                else:
                    print(f"{self.main_player.name}, your Suspicion Radar is calm tonight.")
                    detect_text = f"{self.main_player.name}, your Suspicion Radar is calm tonight."
                    detect_message = tk.Label(self.frame, text=detect_text)
                    detect_message.pack()
        button = tk.Button(self.frame, text="Villager, close your eyes...", command=lambda: self.conclude_night_phase(target))
        button.pack()

        print("Villagers, close your eyes.")

    #def night_phase_detective(self, alive_players, target):
        #self.singleplayer_clear_frame_ui()
        #button = tk.Button(self.frame, text="Sleep through the night...", command=lambda: self.conclude_night_phase(target))
        #button.pack()

    def conclude_night_phase(self, target):
        self.singleplayer_clear_frame_ui()
        # Announce day and resolve night actions
        message = tk.Label(self.frame, text="Everyone, open your eyes.\nThe day begins...")
        message.pack()
        print("Everyone, open your eyes.")
        print("The day begins...")

        # Resolve night actions based on Mafia target and Doctor protection
        print(f"Target passed to conclude_night_phase: {target}")
        if target and not target.protected:
            target.status = "dead"  # Mark as dead if unprotected
            rip_text = f"{target.name} was killed during the night."
            rip_message = tk.Label(self.frame, text=rip_text)
            rip_message.pack()
            print(f"{target.name} was killed during the night.")
        elif target and target.protected:
            survived_text = f"{target.name} was protected by the Doctor and survived the night."
            survived_message = tk.Label(self.frame, text=survived_text)
            survived_message.pack()
            print(f"{target.name} was protected by the Doctor and survived the night.")

        # Reset night actions for all players
        for player in self.player_list:
            player.reset_night_actions()

        self.check_win_conditions("night")

    """ =================================================================================================================================== """

    def check_win_conditions(self, signal):
        self.singleplayer_clear_frame_ui()
        # Check if the village wins (all mafia members are eliminated)
        if self.num_mafia == 0:
            # Set the game completion flag to true, ending the game loop
            self.gameCompleted = True
            # Display the victory message for the village
            village_win_message = tk.Label(self.frame, text="Village Wins!")
            village_win_message.pack()
            print("Village Wins!")
            signal = "gameover"

        # Check if the mafia wins (mafia outnumber or equal the villagers and doctors)
        elif self.num_mafia >= (self.num_villagers + self.num_doctors):
            # Set the game completion flag to true, ending the game loop
            self.gameCompleted = True
            # Display the victory message for the mafia
            mafia_win_message = tk.Label(self.frame, text="Mafia wins!")
            mafia_win_message.pack()
            print("Mafia wins!")
            signal = "gameover"

        if signal == "day":
            #button = tk.Button(self.frame, text="Continue", command=self.night_phase)
            #button.pack()
            self.show_image(r"C:/Users/Murph/OneDrive/Desktop/Code/EECS581/Mafia/night_phase.png", self.night_phase)
        elif signal == "night":
            #button = tk.Button(self.frame, text="Continue", command=self.day_phase)
            #button.pack()
            self.show_image(r"C:/Users/Murph/OneDrive/Desktop/Code/EECS581/Mafia/day_phase.png", self.day_phase)
        else:
            button = tk.Button(self.frame, text="Continue", command=self.end_game)
            button.pack()

    def end_game(self):
        sys.exit()

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
    
    def show_image(self, image_path, next_phase_callback):
        """Displays a PNG image and proceeds to the next phase when clicked."""
        self.clear_frame()
        try:
            # Load the image
            image = tk.PhotoImage(file=image_path)
            
            # Resize the image (set width and height, preserving aspect ratio)
            max_width, max_height = 300, 300  # Desired dimensions
            original_width = image.width()
            original_height = image.height()

            # Scale factors
            scale_width = max_width / original_width
            scale_height = max_height / original_height
            scale = min(scale_width, scale_height)

            # Apply scaling
            new_width = int(original_width * scale)
            new_height = int(original_height * scale)
            resized_image = image.subsample(int(original_width / new_width), int(original_height / new_height))

            # Display the resized image
            label = tk.Label(self.frame, image=resized_image)
            label.image = resized_image  # Keep a reference to avoid garbage collection
            label.pack(pady=10)

            # Add a button to proceed
            proceed_button = tk.Button(
                self.frame,
                text="Proceed",
                font=("Arial", 12),
                command=next_phase_callback
            )
            proceed_button.pack(pady=10)

        except Exception as e:
            # Display an error message if the image fails to load
            tk.Label(self.frame, text=f"Error loading image: {e}", font=("Arial", 12)).pack(pady=10)
            tk.Button(
                self.frame,
                text="Continue",
                font=("Arial", 12),
                command=next_phase_callback
            ).pack(pady=10)
