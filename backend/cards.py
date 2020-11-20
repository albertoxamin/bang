from typing import List, Set, Dict, Tuple, Optional
from abc import ABC, abstractmethod
from enum import IntEnum

class Suit(IntEnum):
    DIAMONDS = 0 # ♦ 
    CLUBS = 1 # ♣
    HEARTS = 2 # ♥
    SPADES = 3  # ♠

class Card(ABC):
    sym = {
        'A': 1,
        'J': 11,
        'Q': 12,
        'K': 13
    }
    def __init__(self, suit: Suit, name: str, number, is_equipment:bool=False, is_weapon:bool=False, vis_mod:int=0, sight_mod:int=0, range:int=99):
        super().__init__()
        self.name = name
        self.suit = suit
        
        if type(number) == int:
            self.number = number
        else:
            self.number = self.sym[number]
        self.is_equipment = is_equipment
        self.is_weapon = is_weapon
        self.vis_mod = vis_mod
        self.sight_mod = sight_mod
        self.range = range

    def __str__(self):
        char = ['♦️','♣️','♥️','♠️'][int(self.suit)]
        return f'{self.name} {char}{self.number}'
        return super().__str__()

class Barile(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Barile', number, is_equipment=True)

class Dinamite(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Dinamite', number, is_equipment=True)

class Mirino(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Mirino', number, is_equipment=True, sight_mod=1)

class Mustang(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Mustang', number, is_equipment=True, is_weapon=True, vis_mod=1)

class Prigione(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Prigione', number, is_equipment=False)

class Remington(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Remington', number, is_equipment=True, is_weapon=True, range=3)

class RevCarabine(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Rev. Carabine', number, is_equipment=True, is_weapon=True, range=4)

class Schofield(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Schofield', number, is_equipment=True, is_weapon=True, range=2)

class Volcanic(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Volcanic', number, is_equipment=True, is_weapon=True, range=1)

class Winchester(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Winchester', number, is_equipment=True, is_weapon=True, range=5)

class Bang(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Bang!', number)

class Birra(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Birra', number)

class CatBalou(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Cat Balou', number)

class Diligenza(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Diligenza', number)

class Duello(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Duello', number)

class Emporio(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Emporio', number)

class Gatling(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Gatling', number)

class Indiani(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Indiani!', number)

class Mancato(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Mancato!', number)

class Panico(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Panico!', number, range=1)

class Saloon(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Saloon', number)

class WellsFargo(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'WellsFargo', number)

def get_starting_deck() -> List[Card]:
    return [
        Barile(Suit.SPADES, 'Q'),
        Barile(Suit.SPADES, 'K'),
        Dinamite(Suit.HEARTS, 2),
        Mirino(Suit.SPADES, 'A'),
        Mustang(Suit.HEARTS, 8),
        Mustang(Suit.HEARTS, 9),
        Prigione(Suit.SPADES, 'J'),
        Prigione(Suit.HEARTS, 4),
        Prigione(Suit.SPADES, 10),
        Remington(Suit.CLUBS, 'K'),
        RevCarabine(Suit.CLUBS, 'A'),
        Schofield(Suit.CLUBS, 'J'),
        Schofield(Suit.CLUBS, 'Q'),
        Schofield(Suit.SPADES, 'K'),
        Volcanic(Suit.SPADES, 10),
        Volcanic(Suit.CLUBS, 10),
        Winchester(Suit.SPADES, 8),
        Bang(Suit.SPADES, 'A'),
        Bang(Suit.DIAMONDS, 2),
        Bang(Suit.DIAMONDS, 3),
        Bang(Suit.DIAMONDS, 4),
        Bang(Suit.DIAMONDS, 5),
        Bang(Suit.DIAMONDS, 6),
        Bang(Suit.DIAMONDS, 7),
        Bang(Suit.DIAMONDS, 8),
        Bang(Suit.DIAMONDS, 9),
        Bang(Suit.DIAMONDS, 10),
        Bang(Suit.DIAMONDS, 'J'),
        Bang(Suit.DIAMONDS, 'Q'),
        Bang(Suit.DIAMONDS, 'K'),
        Bang(Suit.DIAMONDS, 'A'),
        Bang(Suit.CLUBS, 2),
        Bang(Suit.CLUBS, 3),
        Bang(Suit.CLUBS, 4),
        Bang(Suit.CLUBS, 5),
        Bang(Suit.CLUBS, 6),
        Bang(Suit.CLUBS, 7),
        Bang(Suit.CLUBS, 8),
        Bang(Suit.CLUBS, 9),
        Bang(Suit.HEARTS, 'Q'),
        Bang(Suit.HEARTS, 'K'),
        Bang(Suit.HEARTS, 'A'),
        Birra(Suit.HEARTS, 6),
        Birra(Suit.HEARTS, 7),
        Birra(Suit.HEARTS, 8),
        Birra(Suit.HEARTS, 9),
        Birra(Suit.HEARTS, 10),
        Birra(Suit.HEARTS, 'J'),
        CatBalou(Suit.HEARTS, 'K'),
        CatBalou(Suit.DIAMONDS, 9),
        CatBalou(Suit.DIAMONDS, 10),
        CatBalou(Suit.DIAMONDS, 'J'),
        Diligenza(Suit.SPADES, 9),
        Diligenza(Suit.SPADES, 9),
        Duello(Suit.DIAMONDS, 'Q'),
        Duello(Suit.SPADES, 'J'),
        Duello(Suit.CLUBS, 8),
        Emporio(Suit.CLUBS, 9),
        Emporio(Suit.SPADES, 'Q'),
        Gatling(Suit.HEARTS, 10),
        Indiani(Suit.DIAMONDS, 'K'),
        Indiani(Suit.DIAMONDS, 'A'),
        Mancato(Suit.CLUBS, 10),
        Mancato(Suit.CLUBS, 'J'),
        Mancato(Suit.CLUBS, 'Q'),
        Mancato(Suit.CLUBS, 'K'),
        Mancato(Suit.CLUBS, 'A'),
        Mancato(Suit.SPADES, 2),
        Mancato(Suit.SPADES, 3),
        Mancato(Suit.SPADES, 4),
        Mancato(Suit.SPADES, 5),
        Mancato(Suit.SPADES, 6),
        Mancato(Suit.SPADES, 7),
        Mancato(Suit.SPADES, 8),
        Panico(Suit.HEARTS, 'J'),
        Panico(Suit.HEARTS, 'Q'),
        Panico(Suit.HEARTS, 'A'),
        Panico(Suit.DIAMONDS, 8),
        Saloon(Suit.HEARTS, 5),
        WellsFargo(Suit.HEARTS, 3),
    ]
