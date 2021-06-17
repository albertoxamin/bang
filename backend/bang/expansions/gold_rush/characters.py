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
        #TODO

class JoshMcCloud(Character):
    def __init__(self):
        super().__init__("Josh McCloud", max_lives=4)
        # puo pagare 2 pepite per pescare il primo equipaggiamento dalla pila gold rush
        self.icon = '⛅️'
        #TODO

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
        super().__init__("Pretty Luzena", max_lives=4)
        # può scartare 1 pepita per pescare 1 carta (2 volte per turno)
        self.icon = '🐍️'

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
    return cards
