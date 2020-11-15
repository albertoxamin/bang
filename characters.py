from abc import ABC, abstractmethod 

class Character(ABC):
    def __init__(self, name: str, max_lives: int, sight_mod: int = 0, visibility_mod: int = 0):
        super().__init__()
        self.name = name
        self.max_lives = max_lives
        self.sight_mod = 0
        self.visibility_mod = 0

    @abstractmethod
    def on_hurt(self, dmg: int):
        pass

    @abstractmethod
    def on_pick(self, card): # tipo dinamite e prigione
        pass

    @abstractmethod
    def on_empty_hand(self):
        pass

    @abstractmethod
    def on_empty_hand(self):
        pass

class BartCassidy(Character):
    def __init__(self):
        super().__init__("Bart Cassidy", max_lives=4)
    
    def on_hurt(self, dmg):
        pass

class BlackJack(Character):
    def __init__(self):
        super().__init__("Black Jack", max_lives=4)
