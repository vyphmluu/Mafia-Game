'''
player.py
Player class for defining attributed for each player role and methods for day phase and night phase
'''

class Player:
    def __init__(self, role, name):
        self.status = "alive"
        self.role = role  # Role of the player (e.g., mafia, doctor, detective, villager)
        self.name = name  # Name of the player
        self.protected = False  # Indicates if the player is protected for the night
        self.night_target = None  # Target chosen by the player during the night phase (if applicable)
        self.investigated = None  # Target investigated by the detective (if applicable)
        self.attribute = None

    def mafia_action(self, target):
        """ Sets the target for the Mafia to kill. """
        if self.role == "mafia" and self.status == "alive":
            self.night_target = target
            print(f"Mafia {self.name} has chosen {target.name} as their target.")

    def doctor_action(self, target):
        """ Sets the target for the Doctor to protect. """
        if self.role == "doctor" and self.status == "alive":
            target.protected = True
            print(f"Doctor {self.name} has chosen to protect {target.name}.")

    def detective_action(self, target):
        """ Sets the target for the Detective to investigate. """
        if self.role == "detective" and self.status == "alive":
            self.investigated = target  # Set the target for investigation
            print(f"Detective {self.name} is investigating {target.name}.")
            if target.role == "mafia":
                print(f"Detective {self.name} discovers that {target.name} is a Mafia member.")
            else:
                print(f"Detective {self.name} discovers that {target.name} is not a Mafia member.")

    def reset_night_actions(self):
        """ Resets temporary night attributes, preparing the player for the next day. """
        self.protected = False
        self.night_target = None
        self.investigated = None
