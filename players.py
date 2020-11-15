import roles
import cards
import characters

class Player:
    def __init__(self, id):
        super().__init__()
        self.id = id
        self.hand: cards.Card = []
        self.equipment: cards.Card = []
        self.role: roles.Role = None
        self.character: characters.Character = None
        self.lives = 0
        self.max_lives = 0
        self.game = None
    
    def join_game(self, game):
        self.game = game

    def set_role(self, role: roles.Role):
        self.role = role

    def set_character(self, character: characters.Character):
        self.character = character

    def prepare(self):
        self.max_lives = self.character.max_lives + self.role.health_mod
        self.lives = self.max_lives
        self.hand = []
        self.equipment = []

    def set_available_character(self, available):
        self.available_characters = available
    
    def play_turn(self):
        print('not implemented')

    def end_turn(self):
        if len(self.hand) > self.max_lives:
            print("discard a card")
        else:
            game.next_turn()

