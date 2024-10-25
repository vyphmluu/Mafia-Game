'''
player.py
Player class for defining attributed for each player role and methods for day phase and night phase
'''

class Player:
    def __init__(self, role, name):
        self.status = "alive"
        self.role = role
        self.name = name
    