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
        self.is_my_turn = False
        self.is_waiting_for_action = True
        self.has_played_bang = False

    def join_game(self, game):
        self.game = game
        print(f'I {self.id} joined {game}')

    def set_role(self, role: roles.Role):
        self.role = role
        print(f'I {self.id} am a {role.name}')

    def set_character(self, character: characters.Character):
        self.available_characters = []
        self.character = character
        print(f'I {self.id} chose character {character.name}')

    def prepare(self):
        self.max_lives = self.character.max_lives + self.role.health_mod
        self.lives = self.max_lives
        self.hand = []
        self.equipment = []

    def set_available_character(self, available):
        self.available_characters = available
        print(f'I {self.id} have to choose between {available}')
    
    def play_turn(self):
        self.is_my_turn = True
        self.is_waiting_for_action = True
        self.has_played_bang = False
        print(f'I {self.id} was notified that it is my turn')
        print(f'lives: {self.lives}/{self.max_lives} hand: {[str(c) for c in self.hand]}')

    def get_playable_cards(self):
        playable_cards = []
        for i in range(len(self.hand)):
            card = self.hand[i]
            if type(card) == cards.Bang and self.has_played_bang and not any([type(c) == cards.Volcanic for c in self.equipment]):
                continue
            elif type(card) == cards.Birra and self.lives >= self.max_lives:
                continue
            else:
                playable_cards.append(i)
        return playable_cards

    def play_card(self, hand_index: int, againts=None):
        if not (0 <= hand_index < len(self.hand)):
            print('illegal')
            return
        card: cards.Card = self.hand.pop(hand_index)
        print(self.id, 'is playing ', card, ' against:', againts)
        if card.is_equipment and card.name not in [c.name for c in self.equipment]:
            if card.is_weapon:
                for i in range(len(self.equipment)):
                    if self.equipment[i].is_weapon:
                        game.deck.scrap(self.equipment[i])
                        self.equipment[i] = card
                        break
            else:
                self.equipment.append(card)
        else:
            if type(card) == cards.Bang and self.has_played_bang and not any([type(c) == cards.Volcanic for c in self.equipment]):
                print('you retard')
            game.deck.scrap(card)
            pass

    def get_sight(self):
        aim = 0
        for card in self.equipment:
            aim += card.sight_mod
            if card.is_weapon:
                aim += card.range
        return 1 + self.character.sight_mod + aim

    def get_visibility(self):
        covers = 0
        for card in self.equipment:
            covers += card.vis_mod
        return self.character.visibility_mod + covers

    def end_turn(self):
        if len(self.hand) > self.max_lives:
            print(f"I {self.id} have to many cards in my hand and I can't end the turn")
        else:
            game.next_turn()

