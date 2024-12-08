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

from tkinter import Tk, Label, Button, Entry, StringVar, messagebox, Frame, Radiobutton, IntVar
from gameClass import GameClass
import sys


class MafiaGameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mafia Game")
        self.main_frame = Frame(root)
        self.main_frame.pack(pady=20, padx=20)

        self.gamemode = IntVar()
        self.create_main_menu()

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def create_main_menu(self):
        self.clear_frame()
        Label(self.main_frame, text="-----Welcome to Mafia-----", font=("Arial", 16)).pack(pady=10)
        Label(self.main_frame, text="Choose a Mode:", font=("Arial", 12)).pack(pady=5)
        Radiobutton(self.main_frame, text="Single player", variable=self.gamemode, value=1).pack(anchor="w")
        Radiobutton(self.main_frame, text="Multi player", variable=self.gamemode, value=2).pack(anchor="w")
        Radiobutton(self.main_frame, text="Exit", variable=self.gamemode, value=3).pack(anchor="w")
        Button(self.main_frame, text="Proceed", command=self.handle_main_menu).pack(pady=10)

    def handle_main_menu(self):
        """Handle the user's choice from the main menu."""
        mode = self.gamemode.get()
        if mode == 3:
            sys.exit("Exit Complete.")
        elif mode == 1:
            self.create_singleplayer_setup()
        elif mode == 2:
            self.create_multiplayer_setup()
        else:
            messagebox.showerror("Invalid Input", "Please select a mode!")

    def create_singleplayer_setup(self):
        self.clear_frame()
        Label(self.main_frame, text="Single Player Mode", font=("Arial", 14)).pack(pady=10)
        Label(self.main_frame, text="Enter your name:", font=("Arial", 12)).pack(pady=5)
        self.player_name = StringVar()
        Entry(self.main_frame, textvariable=self.player_name).pack(pady=5)
        Button(self.main_frame, text="Start Game", command=self.start_singleplayer).pack(pady=10)

    def start_singleplayer(self):
        name = self.player_name.get().lower()
        if not name:
            messagebox.showerror("Error", "Player name cannot be empty!")
            return
        self.clear_frame()
        Label(self.main_frame, text="Choose AI Difficulty", font=("Arial", 14)).pack(pady=10)
        Button(self.main_frame, text="Easy Mode", command=lambda: self.start_game(name, 1)).pack(pady=5)
        Button(self.main_frame, text="Normal Mode", command=lambda: self.start_game(name, 2)).pack(pady=5)
        Button(self.main_frame, text="Hard Mode", command=lambda: self.start_game(name, 3)).pack(pady=5)

    def start_game(self, name, difficulty):
        """Initialize the game and start the first phase."""
        self.game = GameClass(10, 1, self.main_frame, self)  # Pass `self` as the `app` parameter
        self.game.main_player(name)
        self.game.add_player(name)

        # Add other players
        name_list = ["John", "Bob", "Robin", "Elizabeth", "Alice", "Danny", "Alphonso", "Sedrick", "Darius"]
        for player in name_list:
            self.game.add_player(player)

        # Assign roles and set difficulty
        self.game.assignRoles()
        self.game.game_difficulty = difficulty

        # Transition to the Day Phase
        self.game.day_phase()

    def create_multiplayer_setup(self):
        self.clear_frame()
        Label(self.main_frame, text="Multiplayer Mode", font=("Arial", 14)).pack(pady=10)
        Label(self.main_frame, text="Enter number of players:", font=("Arial", 12)).pack(pady=5)
        self.num_players = StringVar()
        Entry(self.main_frame, textvariable=self.num_players).pack(pady=5)
        Button(self.main_frame, text="Setup Players", command=self.setup_multiplayer).pack(pady=10)

    def setup_multiplayer(self):
        """Collect player names for multiplayer mode and start the game."""
        try:
            number_of_players = int(self.num_players.get())
            if number_of_players <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of players!")
            return

        self.multiplayer_names = []
        self.clear_frame()
        Label(self.main_frame, text=f"Enter names for {number_of_players} players:", font=("Arial", 14)).pack(pady=10)
        for i in range(number_of_players):
            Label(self.main_frame, text=f"Player {i + 1} Name:").pack(anchor="w")
            name_var = StringVar()
            Entry(self.main_frame, textvariable=name_var).pack(pady=5)
            self.multiplayer_names.append(name_var)

        Button(self.main_frame, text="Start Game", command=self.start_multiplayer_game).pack(pady=10)

    def start_multiplayer(self):
        self.game = GameClass(len(self.multiplayer_names), 2, self.main_frame, self)  # Pass self
        for name_var in self.multiplayer_names:
            name = name_var.get().lower()
            if not name:
                messagebox.showerror("Error", "Player names cannot be empty!")
                return
            self.game.add_player(name)

        self.game.assignRoles()

        # Start the role call UI
        self.start_role_call(self.game)
    
    def start_multiplayer_game(self):
        """Initialize the game for multiplayer and start the first phase."""
        # Set up the GameClass instance for multiplayer
        self.game = GameClass(len(self.multiplayer_names), 2, self.main_frame, self)

        # Add players from the collected names
        for name_var in self.multiplayer_names:
            name = name_var.get().lower()
            if not name:
                messagebox.showerror("Error", "Player names cannot be empty!")
                return
            self.game.add_player(name)

        # Assign roles and start role call
        self.game.assignRoles()
        self.start_role_call(self.game)
    
    def start_role_call(self, game):
        """Begin the role call sequence with a transition screen for the first player."""
        self.game = game
        self.current_role_index = 0  # Start with the first player

        # Show the transition screen for the first player
        self.transition_screen()

    def show_player_role(self, player):
        """Display the current player's role."""
        self.clear_frame()

        Label(self.main_frame, text=f"{player.name.capitalize()}, it's your turn!", font=("Arial", 14)).pack(pady=10)
        Label(self.main_frame, text=f"Your role: {player.role.capitalize()}", font=("Arial", 12)).pack(pady=10)

        # Display special abilities for villagers
        if player.role == "villager" and player.attribute:
            Label(self.main_frame, text=f"Special ability: {player.attribute.capitalize()}", font=("Arial", 12)).pack(pady=5)

        # Add a button for the next step
        if self.current_role_index < len(self.game.player_list) - 1:
            Button(self.main_frame, text="Next", command=self.next_player_role).pack(pady=10)
        else:
            Button(self.main_frame, text="Proceed to Day Phase", command=self.game.day_phase).pack(pady=10)

    def transition_screen(self):
        """Show a transition screen between players' role displays."""
        self.clear_frame()

        # Display a message for the next player
        Label(
            self.main_frame,
            text=f"Next Player: {self.game.player_list[self.current_role_index].name.capitalize()}",
            font=("Arial", 14),
        ).pack(pady=20)
        Label(
            self.main_frame,
            text="Please come to the screen. Press 'Continue' when ready.",
            font=("Arial", 12),
        ).pack(pady=10)

        # Add a button to proceed
        Button(
            self.main_frame,
            text="Continue",
            command=lambda: self.show_player_role(self.game.player_list[self.current_role_index]),
        ).pack(pady=10)
        
    def next_player_role(self):
        self.current_role_index += 1
        self.transition_screen()


if __name__ == "__main__":
    root = Tk()
    app = MafiaGameApp(root)
    root.mainloop()
