'''
player.py
Player class for defining attributed for each player role and methods for day phase and night phase
'''

class Player:
    def __init__(self, role, name):
        self.status = "alive"
        self.role = role # Role of the player. (mafia, doctor, villager)
        self.name = name # Name of the player
        self.protected = False  # Indicates if the player is protected for the night
        self.night_target = None  # Target chosen by the player during the night phase (if applicable)

    def mafia_action(self, target):
        """
        Sets the target for the Mafia to kill.
        
        :param target: Player object that the Mafia intends to eliminate
        """
        if self.role == "mafia" and self.status == "alive":
            self.night_target = target  # Set the target for the night
            print(f"Mafia {self.name} has chosen {target.name} as their target.")

    def doctor_action(self, target):
        """
        Sets the target for the Doctor to protect.
        
        :param target: Player object that the Doctor intends to protect
        """
        if self.role == "doctor" and self.status == "alive":
            target.protected = True  # Mark the target as protected for the night
            print(f"Doctor {self.name} has chosen to protect {target.name}.")

    def reset_night_actions(self):
        """
        Resets the temporary night attributes, preparing the player for the next day.
        """
        self.protected = False  # Reset protection status
        self.night_target = None  # Reset any targets chosen for the night