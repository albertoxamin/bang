from abc import ABC, abstractmethod 

class Character(ABC):
    def __init__(self, name: str, max_lives: int, sight_mod: int = 0, visibility_mod: int = 0, pick_mod: int = 0, desc: str = ''):
        super().__init__()
        self.name = name
        self.max_lives = max_lives
        self.sight_mod = 0
        self.visibility_mod = 0
        self.pick_mod = 0
        self.desc = desc

    # @abstractmethod
    # def on_hurt(self, dmg: int):
    #     pass

    # @abstractmethod
    # def on_pick(self, card): # tipo dinamite e prigione
    #     pass

    # @abstractmethod
    # def on_empty_hand(self):
    #     pass

    # @abstractmethod
    # def on_empty_hand(self):
    #     pass

class BartCassidy(Character):
    def __init__(self):
        super().__init__("Bart Cassidy", max_lives=4, desc='Ogni volta che viene ferito, pesca una carta.')
    
    def on_hurt(self, dmg):
        pass

class BlackJack(Character):
    def __init__(self):
        super().__init__("Black Jack", max_lives=4)

class CalamityJanet(Character):
    def __init__(self):
        super().__init__("Calamity Janet", max_lives=4)

class ElGringo(Character):
    def __init__(self):
        super().__init__("El Gringo", max_lives=3)

class JesseJones(Character):
    def __init__(self):
        super().__init__("Jesse Jones", max_lives=4)

class Jourdonnais(Character):
    def __init__(self):
        super().__init__("Jourdonnais", max_lives=4)

class KitCarlson(Character):
    def __init__(self):
        super().__init__("Kit Carlson", max_lives=4)

class LuckyDuke(Character):
    def __init__(self):
        super().__init__("Lucky Duke", max_lives=4, pick_mod=1)

class PaulRegret(Character):
    def __init__(self):
        super().__init__("Paul Regret", max_lives=3)

class PedroRamirez(Character):
    def __init__(self):
        super().__init__("Pedro Ramirez", max_lives=4)

class RoseDoolan(Character):
    def __init__(self):
        super().__init__("Rose Doolan", max_lives=4)

class SidKetchum(Character):
    def __init__(self):
        super().__init__("Sid Ketchum", max_lives=4)

class SlabTheKiller(Character):
    def __init__(self):
        super().__init__("Slab The Killer", max_lives=4)

class SuzyLafayette(Character):
    def __init__(self):
        super().__init__("Suzy Lafayette", max_lives=4)

class VultureSam(Character):
    def __init__(self):
        super().__init__("Vulture Sam", max_lives=4)

class WillyTheKid(Character):
    def __init__(self):
        super().__init__("Willy The Kid", max_lives=4)

def all_characters():
    return [
        BartCassidy(),
        BlackJack(),
        CalamityJanet(),
        ElGringo(),
        JesseJones(),
        Jourdonnais(),
        KitCarlson(),
        LuckyDuke(),
        PaulRegret(),
        PedroRamirez(),
        RoseDoolan(),
        SidKetchum(),
        SlabTheKiller(),
        SuzyLafayette(),
        VultureSam(),
        WillyTheKid(),
    ]