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
from player import Player
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
        Radiobutton(self.main_frame, text="Singleplayer", variable=self.gamemode, value=1).pack(anchor="w")
        Radiobutton(self.main_frame, text="Multiplayer", variable=self.gamemode, value=2).pack(anchor="w")
        Radiobutton(self.main_frame, text="Exit", variable=self.gamemode, value=3).pack(anchor="w")
        Button(self.main_frame, text="Proceed", command=self.handle_main_menu).pack(pady=10)

    def handle_main_menu(self):
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
        game = GameClass(10, 1)
        game.main_player(name)
        game.add_player(name)
        # Add AI players
        game.ai_mode()
        name_list = ["John", "Bob", "Robin", "Elizabeth", "Alice", "Danny", "Alphonso", "Sedrick", "Darius"]
        for player in name_list:
            game.add_player(player)
        game.assignRoles()
        game.start_game()
        messagebox.showinfo("Game Over", "Game has ended!")
        self.create_main_menu()

    def create_multiplayer_setup(self):
        self.clear_frame()
        Label(self.main_frame, text="Multiplayer Mode", font=("Arial", 14)).pack(pady=10)
        Label(self.main_frame, text="Enter number of players:", font=("Arial", 12)).pack(pady=5)
        self.num_players = StringVar()
        Entry(self.main_frame, textvariable=self.num_players).pack(pady=5)
        Button(self.main_frame, text="Setup Players", command=self.setup_multiplayer).pack(pady=10)

    def setup_multiplayer(self):
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
        Button(self.main_frame, text="Start Game", command=self.start_multiplayer).pack(pady=10)

    def start_multiplayer(self):
        game = GameClass(len(self.multiplayer_names), 2)
        for name_var in self.multiplayer_names:
            name = name_var.get().lower()
            if not name:
                messagebox.showerror("Error", "Player names cannot be empty!")
                return
            game.add_player(name)
        game.assignRoles()
        game.start_game()
        messagebox.showinfo("Game Over", "Game has ended!")
        self.create_main_menu()


#Run the game application
if __name__ == "__main__":
    root = Tk()
    app = MafiaGameApp(root)
    root.mainloop()
