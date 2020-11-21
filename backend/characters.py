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
        self.icon = '🤷‍♂️'
        self.number = ''.join(['❤️']*self.max_lives)

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
        super().__init__("Bart Cassidy", max_lives=4)
        self.desc = "Ogni volta che viene ferito, pesca una carta"
    
    def on_hurt(self, dmg):
        pass

class BlackJack(Character):
    def __init__(self):
        super().__init__("Black Jack", max_lives=4)
        self.desc = "All'inizio del suo turno, quando deve pescare, mostra a tutti la seconda carta, se è Cuori o Quadri pesca una terza carta senza farla vedere"

class CalamityJanet(Character):
    def __init__(self):
        super().__init__("Calamity Janet", max_lives=4)
        self.icon = '🤷‍♀️'
        self.desc = "Può usare i Mancato! come Bang! e viceversa"
        #TODO:  gestire bene la scelta multipla in ogni iterazione con la carta bang e mancato
        #       vale anche per le carte indiani e duello
        #       se usa un mancato come bang ovviamente non ne può usare altri lo stesso turno se non ha una volcanic

class ElGringo(Character):
    def __init__(self):
        super().__init__("El Gringo", max_lives=3)
        self.desc = "Ogni volta che perde un punto vita pesca una carta dalla mano del personaggio che gli ha sparato (solo se ha carte in mano; una carta per ogni punto vita)"
        # ovviamente la dinamite non è considerata danno inferto da un giocatore

class JesseJones(Character):
    def __init__(self):
        super().__init__("Jesse Jones", max_lives=4)
        self.desc = "All'inizio del suo turno, quando deve pescare, può prendere la prima carta a caso dalla mano di un giocatore e la seconda dal mazzo"

class Jourdonnais(Character):
    def __init__(self):
        super().__init__("Jourdonnais", max_lives=4)
        self.desc = "Gioca come se avesse un Barile sempre attivo, nel caso in cui metta in gioco un Barile 'Reale' può estrarre due volte"

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
        self.icon = '🤷‍♀️'

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