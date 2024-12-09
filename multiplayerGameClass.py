from gameClass import GameClass
import tkinter as tk
import random
from tkinter import Label, Button, Entry, StringVar, messagebox, Radiobutton

class MultiplayerGameClass(GameClass):
    def __init__(self, num_players, main_frame, app):
        super().__init__(num_players, 2, main_frame, app)
        self.main_frame = main_frame  # Store the main_frame for UI updates

    def multiplayer_day_phase(self):
        """Handles the day phase for multiplayer mode, allowing players to vote."""
        self.clear_frame()
        tk.Label(self.frame, text="Day Phase: Time to vote!", font=("Arial", 14)).pack(pady=10)

        self.votes = {}
        self.current_voter_index = 0
        self.alive_players = [p for p in self.player_list if p.status == "alive"]

        if self.alive_players:
            self.multiplayer_next_voter()
        else:
            messagebox.showinfo("Error", "No players alive to vote!")

    def multiplayer_next_voter(self):
        """Handles transitioning to the next voter in the multiplayer day phase."""
        if self.current_voter_index < len(self.alive_players):
            current_voter = self.alive_players[self.current_voter_index]
            self.show_multiplayer_voting_screen(current_voter)
        else:
            self.tally_multiplayer_votes()

    def show_multiplayer_voting_screen(self, voter):
        """Show the voting screen for the current player in multiplayer."""
        self.clear_frame()

        # Display the voter's name and instruction
        tk.Label(self.frame, text=f"{voter.name.capitalize()}, it's your turn to vote!", font=("Arial", 14)).pack(pady=10)

        # Initialize the StringVar for vote_target with an empty value
        self.vote_target = tk.StringVar(value="")

        # List of alive players to vote for (exclude the voter themselves)
        alive_targets = [p for p in self.player_list if p.status == "alive" and p.name != voter.name]

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

        self.votes[selected_player] = self.votes.get(selected_player, 0) + 1
        self.current_voter_index += 1

        if self.current_voter_index < len(self.alive_players):
            self.show_multiplayer_voting_screen(self.alive_players[self.current_voter_index])
        else:
            self.tally_multiplayer_votes()

    def tally_multiplayer_votes(self):
        """Tally votes and eliminate the player with the most votes."""
        self.clear_frame()

        if self.votes:
            max_votes = max(self.votes.values())
            candidates = [name for name, count in self.votes.items() if count == max_votes]
            eliminated_player_name = random.choice(candidates) if len(candidates) > 1 else candidates[0]
            eliminated_player = next(p for p in self.player_list if p.name == eliminated_player_name)

            eliminated_player.status = "dead"
            tk.Label(self.frame, text=f"{eliminated_player.name.capitalize()} has been eliminated!", font=("Arial", 16)).pack(pady=20)
            self.update_role_count(eliminated_player.role, increment=False)

            if self.check_win_conditions():
                return

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
        mafia_players = [p for p in self.player_list if p.role == "mafia" and p.status == "alive"]
        
        # Check if there are Mafia players left to act
        if not mafia_players:
            messagebox.showinfo("Game Info", "No Mafia members are alive to act.")
            self.resolve_mafia_votes()  # Optionally resolve Mafia votes or move to the next phase
            return
        
        # Ensure current_mafia_index is within bounds
        if self.current_mafia_index >= len(mafia_players):
            messagebox.showinfo("Game Info", "No more Mafia members left to vote.")
            self.resolve_mafia_votes()  # Resolve votes or adjust game flow as needed
            return

        mafia_player = mafia_players[self.current_mafia_index]
        self.clear_frame()

        # Display the current mafia player's name and instruction
        tk.Label(self.frame, text=f"{mafia_player.name.capitalize()}, it's your turn to vote!", font=("Arial", 14)).pack(pady=10)
        tk.Label(self.frame, text="Mafia allies:", font=("Arial", 12, "bold")).pack(pady=5)

        # Display the list of mafia allies
        mafia_allies = [p.name.capitalize() for p in mafia_players if p != mafia_player]
        if mafia_allies:
            tk.Label(self.frame, text=", ".join(mafia_allies), font=("Arial", 12)).pack(pady=5)
        else:
            tk.Label(self.frame, text="No other mafia allies alive.", font=("Arial", 12)).pack(pady=5)

        # Voting options for the mafia player
        alive_targets = [p for p in self.player_list if p.status == "alive" and p.name != mafia_player.name]
        self.vote_target = tk.StringVar(value="")

        tk.Label(self.frame, text="Choose a player to eliminate:", font=("Arial", 12)).pack(pady=10)

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
            text="Proceed to Detective Phase",
            command=self.detective_phase  # Transition to the Detective Phase
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
            text="Proceed to Random Event",
            command=self.random_event_generator
        ).pack(pady=10)

    def start_role_call(self, game):
        """Begin the role call sequence with a transition screen for the first player."""
        self.current_role_index = 0  # Start with the first player
        self.transition_screen()

    def show_player_role(self, player):
        """Display the current player's role."""
        self.clear_frame()

        tk.Label(self.frame, text=f"{player.name.capitalize()}, it's your turn!", font=("Arial", 14)).pack(pady=10)
        tk.Label(self.frame, text=f"Your role: {player.role.capitalize()}", font=("Arial", 12)).pack(pady=10)

        # Display special abilities for villagers
        if player.role == "villager" and player.attribute:
            tk.Label(self.frame, text=f"Special ability: {player.attribute.capitalize()}", font=("Arial", 12)).pack(pady=5)

        # Add a button for the next step
        if self.current_role_index < len(self.player_list) - 1:
            tk.Button(self.frame, text="Next", command=self.next_player_role).pack(pady=10)
        else:
            tk.Button(self.frame, text="Proceed to Day Phase", command=self.multiplayer_day_phase).pack(pady=10)

    def transition_screen(self):
        """Show a transition screen between players' role displays."""
        self.clear_frame()

        # Display a message for the next player
        tk.Label(
            self.frame,
            text=f"Next Player: {self.player_list[self.current_role_index].name.capitalize()}",
            font=("Arial", 14),
        ).pack(pady=20)
        tk.Label(
            self.frame,
            text="Please come to the screen. Press 'Continue' when ready.",
            font=("Arial", 12),
        ).pack(pady=10)

        # Add a button to proceed
        tk.Button(
            self.frame,
            text="Continue",
            command=lambda: self.show_player_role(self.player_list[self.current_role_index]),
        ).pack(pady=10)
            
    def next_player_role(self):
        self.current_role_index += 1
        self.transition_screen()

    def detective_phase(self):
        """Handles the Detective's investigation phase."""
        self.clear_frame()

        # Identify the detective
        detective = next((p for p in self.player_list if p.role == "detective" and p.status == "alive"), None)

        if not detective:
            # No active detective, proceed to the Doctor Phase
            self.proceed_to_doctor_phase()
            return

        # UI for the detective's turn
        tk.Label(self.frame, text=f"{detective.name.capitalize()}, it's your turn to investigate!", font=("Arial", 14)).pack(pady=10)
        tk.Label(self.frame, text="Select a player to investigate:", font=("Arial", 12)).pack(pady=10)

        # List of alive players to investigate
        self.investigation_target = tk.StringVar()
        alive_players = [p for p in self.player_list if p.status == "alive" and p.name != detective.name]

        for player in alive_players:
            tk.Radiobutton(
                self.frame,
                text=player.name.capitalize(),
                variable=self.investigation_target,
                value=player.name
            ).pack(anchor="w")

        # Button to submit investigation
        tk.Button(
            self.frame,
            text="Investigate",
            command=lambda: self.show_investigation_result(detective)
        ).pack(pady=10)

    def show_detective_screen(self):
        """Display the screen for the Detective to choose a player to investigate."""
        detective_player = next((p for p in self.player_list if p.role == "detective" and p.status == "alive"), None)

        if not detective_player:
            self.proceed_to_doctor_phase()  # Skip this phase if no detective is alive
            return

        self.clear_frame()
        tk.Label(self.frame, text=f"{detective_player.name.capitalize()}, it's your turn to investigate a player!", font=("Arial", 14)).pack(pady=10)

        # List of alive players to investigate
        self.investigate_target = tk.StringVar(value="")  # No default selection
        alive_players = [p for p in self.player_list if p.status == "alive" and p.name != detective_player.name]

        for player in alive_players:
            tk.Radiobutton(
                self.frame,
                text=player.name.capitalize(),
                variable=self.investigate_target,
                value=player.name
            ).pack(anchor="w")

        # Submit investigation button
        tk.Button(
            self.frame,
            text="Submit Investigation",
            command=self.submit_detective_investigation
        ).pack(pady=10)

    def submit_detective_investigation(self):
        """Record the Detective's investigation and reveal the result."""
        selected_player_name = self.investigate_target.get()

        if not selected_player_name:
            messagebox.showerror("Error", "You must select a player to investigate!")
            return

        # Reveal the investigated player's role
        investigated_player = next((p for p in self.player_list if p.name == selected_player_name), None)

        if investigated_player:
            role_message = f"{investigated_player.name.capitalize()} is a {investigated_player.role.capitalize()}."
            messagebox.showinfo("Investigation Result", role_message)

        # Proceed to the next phase (e.g., Doctor Phase)
        self.proceed_to_doctor_phase()

    def show_investigation_result(self, detective):
        """Show the result of the detective's investigation on the main app screen."""
        target_name = self.investigation_target.get()

        if not target_name:
            messagebox.showerror("Error", "You must select a player to investigate!")
            return

        # Find the target player
        target_player = next(p for p in self.player_list if p.name == target_name)

        # Clear the current screen
        self.clear_frame()

        # Display the investigation result
        tk.Label(
            self.frame,
            text=f"Investigation Result",
            font=("Arial", 16)
        ).pack(pady=10)

        tk.Label(
            self.frame,
            text=f"{target_player.name.capitalize()} is a {target_player.role.capitalize()}!",
            font=("Arial", 14)
        ).pack(pady=20)

        # Add a continue button to proceed to the next phase
        tk.Button(
            self.frame,
            text="Continue",
            command=self.check_for_doctor_phase
        ).pack(pady=10)

    def check_for_doctor_phase(self):
        """Check if a doctor is alive before proceeding to the Doctor Phase."""
        if not any(player.role == "doctor" and player.status == "alive" for player in self.player_list):
            # Skip to Villager Phase if no doctors are alive
            self.proceed_to_villager_phase()
        else:
            # Proceed with the Doctor Phase
            self.doctor_phase()

    def proceed_to_doctor_phase(self):
        """Proceeds to the Doctor's phase after the Detective's actions."""
        self.clear_frame()
        tk.Label(self.frame, text="Proceeding to the Doctor Phase.", font=("Arial", 14)).pack(pady=10)

        tk.Button(
            self.frame,
            text="Continue",
            command=self.doctor_phase
        ).pack(pady=10)

    def random_event_generator(self):
        self.clear_frame()

        choice = random.randint(0,5)
        if choice == 0:
            self.hurricane()
        elif choice == 1:
            self.tornado()
        elif choice == 2:
            self.village_fire()
        elif choice == 3:
            self.suspicious_action()
        else:
            tk.Label(
                self.frame,
                text="No Random Event Occurs Today.",
                font=("Arial", 12),
            ).pack(pady=10)

        if self.check_win_conditions():
            return

        tk.Button(
            self.frame,
            text="Proceed to Day Phase",
            command=self.multiplayer_day_phase
        ).pack(pady=10)
   
    def hurricane(self):
        tk.Label(
            self.frame,
            text="A massive hurricane hits the village!",
            font=("Arial", 12),
        ).pack(pady=10)
        self.alive_players = [p for p in self.player_list if p.status == "alive"]
        target_player = self.alive_players[1]
        target_player.status = "dead"
        tk.Label(self.frame, text=f"{target_player.name.capitalize()} was killed in the hurricane!", font=("Arial", 14)).pack(pady=10)

    def tornado(self):
        tk.Label(
            self.frame,
            text="Look! A tornado is heading towards the village!",
            font=("Arial", 12),
        ).pack(pady=10)
        self.alive_players = [p for p in self.player_list if p.status == "alive"]
        target_player = self.alive_players[1]
        target_player.status = "dead"
        tk.Label(self.frame, text=f"{target_player.name.capitalize()} was killed in the tornado!", font=("Arial", 14)).pack(pady=10)

    def village_fire(self):
        tk.Label(
            self.frame,
            text="Oh no! A villager's house is on fire!",
            font=("Arial", 12),
        ).pack(pady=10)
        
        # Refresh the list of alive players to ensure it's up to date
        self.alive_players = [p for p in self.player_list if p.status == "alive"]
        
        # Ensure there are at least two alive players before accessing the second one
        if len(self.alive_players) > 1:
            target_player = self.alive_players[1]  # Assuming we want to affect the second player in the list
            target_player.status = "dead"
            tk.Label(self.frame, text=f"{target_player.name.capitalize()} was killed in the fire!", font=("Arial", 14)).pack(pady=10)
        else:
            # Handle the scenario where fewer than two players are alive
            tk.Label(self.frame, text="Not enough players alive to spread the fire.", font=("Arial", 14)).pack(pady=10)

    def suspicious_action(self):
        tk.Label(
            self.frame,
            text="The word around the town is that someone has been doing some suspicious things.",
            font=("Arial", 12),
        ).pack(pady=10)
        
        # Ensure there are at least two alive players before accessing them
        if len(self.alive_players) > 1:
            target_player = self.alive_players[1]  # Target the second alive player in the list
            tk.Label(self.frame, text=f"{target_player.name.capitalize()} has been hiding guns and knives in his house! Do with that info as you please.", font=("Arial", 14)).pack(pady=10)
        else:
            tk.Label(self.frame, text="Not enough players alive for any suspicious action to be noteworthy.", font=("Arial", 14)).pack(pady=10)
