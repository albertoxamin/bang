from abc import ABC, abstractmethod
from enum import Enum

class Suit(Enum):
    DIAMONDS = 1 # ♦
    CLUBS = 2 # ♣
    HEARTS = 3 # ♥
    SPADES = 4 # ♠

class Card(ABC):
    def __init__(self):
        super().__init__()