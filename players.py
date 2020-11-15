import roles
import characters

class Player:
    def __init__(self, id):
        super().__init__()
        self.id = id
        self.hand = []
        self.role: roles.Role = None
        self.character: characters.Character = None
        self.lives = 0
        self.max_lives = 0

    def set_role(self, role: roles.Role):
        self.role = role

    def set_character(self, character: characters.Character):
        self.character = character

    def prepare(self):
        self.max_lives = self.character.max_lives + self.role.health_mod
        self.lives = self.max_lives
    
    