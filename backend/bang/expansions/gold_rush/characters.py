from typing import List
from bang.characters import Character

class DonBell(Character):
    def __init__(self):
        super().__init__("Don Bell", max_lives=4)
        # A fine turno estrae, ❤️ o ♦️ gioca di nuovo
        self.icon = '🔔️'

class DutchWill(Character):
    def __init__(self):
        super().__init__("Dutch Will", max_lives=4)
        # Pesca 2 ne scarta 1 e prende 1 pepita
        self.icon = '🧐️'

class JackyMurieta(Character):
    def __init__(self):
        super().__init__("Jacky Murieta", max_lives=4)
        # puo pagare 2 pepite per sparare 1 bang extra
        self.icon = '💆‍♂️️'

    def special(self, player, data):
        if super().special(player, data):
            if player.gold_nuggets >= 2 and player.is_my_turn:
                player.gold_nuggets -= 2
                player.has_played_bang = False
                player.bang_used -= 1
                player.notify_self()
                return True
        return False

class JoshMcCloud(Character):
    def __init__(self):
        super().__init__("Josh McCloud", max_lives=4)
        # puo pagare 2 pepite per pescare il primo equipaggiamento dalla pila gold rush
        self.icon = '⛅️'

    def special(self, player, data):
        if super().special(player, data):
            if player.gold_nuggets >= 2 and player.is_my_turn:
                player.gold_nuggets -= 2
                card = player.game.deck.shop_deck.pop(0)
                print(f'{player.name} ha comprato usando la abilità speciale {card.name}')
                if card.play_card(player):
                    player.game.deck.shop_deck.append(card)
                player.notify_self()
                return True
        return False

class MadamYto(Character):
    def __init__(self):
        super().__init__("Madam Yto", max_lives=4)
        # quando viene giocata 1 birra pesca 1 carta
        self.icon = '💃️'

class PrettyLuzena(Character):
    def __init__(self):
        super().__init__("Pretty Luzena", max_lives=4)
        # una volta per turno ha 1 sconto di 1 pepita sugli equipaggiamenti
        self.icon = '👛️'

class RaddieSnake(Character):
    def __init__(self):
        super().__init__("Raddie Snake", max_lives=4)
        # può scartare 1 pepita per pescare 1 carta (2 volte per turno)
        self.icon = '🐍️'

    def special(self, player, data):
        if super().special(player, data):
            if player.gold_nuggets >= 1 and player.is_my_turn and player.special_use_count < 2:
                player.gold_nuggets -= 1
                player.special_use_count += 1
                player.hand.append(player.game.deck.draw(True))
                player.notify_self()
                return True
        return False

class SimeonPicos(Character):
    def __init__(self):
        super().__init__("Simeon Picos", max_lives=4)
        # ottiene 1 pepita ogni volta che perde 1 punto vita
        self.icon = '🏇️'


def all_characters() -> List[Character]:
    cards = [
        DonBell(),
        DutchWill(),
        JackyMurieta(),
        JoshMcCloud(),
        MadamYto(),
        PrettyLuzena(),
        RaddieSnake(),
        SimeonPicos(),
    ]
    for c in cards:
        c.expansion_icon = '🤑️'
        c.expansion = 'gold_rush'
    return cards
