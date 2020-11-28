from abc import ABC, abstractmethod
from typing import List

class Character(ABC):
    def __init__(self, name: str, max_lives: int, sight_mod: int = 0, visibility_mod: int = 0, pick_mod: int = 0, desc: str = ''):
        super().__init__()
        self.name = name
        self.max_lives = max_lives
        self.sight_mod = sight_mod
        self.visibility_mod = visibility_mod
        self.pick_mod = pick_mod
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
        self.icon = '💔'
    
    def on_hurt(self, dmg):
        pass

class BlackJack(Character):
    def __init__(self):
        super().__init__("Black Jack", max_lives=4)
        self.desc = "All'inizio del suo turno, quando deve pescare, mostra a tutti la seconda carta, se è Cuori o Quadri pesca una terza carta senza farla vedere"
        self.icon = '🎰'

class CalamityJanet(Character):
    def __init__(self):
        super().__init__("Calamity Janet", max_lives=4)
        self.icon = '🔀'
        self.desc = "Può usare i Mancato! come Bang! e viceversa"
        #TODO:  gestire bene la scelta multipla in ogni iterazione con la carta bang e mancato
        #       vale anche per le carte indiani e duello
        #       se usa un mancato come bang ovviamente non ne può usare altri lo stesso turno se non ha una volcanic

class ElGringo(Character):
    def __init__(self):
        super().__init__("El Gringo", max_lives=3)
        self.desc = "Ogni volta che perde un punto vita pesca una carta dalla mano del giocatore responsabile ma solo se il giocatore in questione ha carte in mano (una carta per ogni punto vita)"
        self.icon = '🤕'
        # ovviamente la dinamite non è considerata danno inferto da un giocatore

class JesseJones(Character):
    def __init__(self):
        super().__init__("Jesse Jones", max_lives=4)
        self.desc = "All'inizio del suo turno, quando deve pescare, può prendere la prima carta a caso dalla mano di un giocatore e la seconda dal mazzo"
        self.icon = '😜'

class Jourdonnais(Character):
    def __init__(self):
        super().__init__("Jourdonnais", max_lives=4)
        self.desc = "Gioca come se avesse un Barile sempre attivo, nel caso in cui metta in gioco un Barile 'Reale' può estrarre due volte"
        self.icon = '🛢'

class KitCarlson(Character):
    def __init__(self):
        super().__init__("Kit Carlson", max_lives=4)
        self.desc = "All'inizio del suo turno, quando deve pescare, pesca tre carte, ne sceglie due da tenere in mano e la rimanente la rimette in cima la mazzo"
        self.icon = '🤔'

class LuckyDuke(Character):
    def __init__(self):
        super().__init__("Lucky Duke", max_lives=4, pick_mod=1)
        self.desc = "Ogni volta che deve estrarre, prende due carte dal mazzo, sceglie una delle due carte per l'estrazione, infine le scarta entrambe"
        self.icon = '🍀'

class PaulRegret(Character):
    def __init__(self):
        super().__init__("Paul Regret", max_lives=3, visibility_mod=1)
        self.desc = "Gioca come se avesse una Mustang sempre attiva, nel caso in cui metta in gioco una Mustang 'Reale' l'effetto si somma tranquillamente"
        self.icon = '🏇'

class PedroRamirez(Character):
    def __init__(self):
        super().__init__("Pedro Ramirez", max_lives=4)
        self.desc = "All'inizio del suo turno, quando deve pescare, può prendere la prima carta dalla cima degli scarti e la seconda dal mazzo"
        self.icon = '🚮'

class RoseDoolan(Character):
    def __init__(self):
        super().__init__("Rose Doolan", max_lives=4, sight_mod=1)
        self.icon = '🕵️‍♀️'
        self.desc = "Gioca come se avesse un Mirino sempre attivo, nel caso in cui metta in gioco una Mirino 'Reale' l'effetto si somma tranquillamente"

class SidKetchum(Character):
    def __init__(self):
        super().__init__("Sid Ketchum", max_lives=4)
        self.desc = "Può scartare due carte per recuperare un punto vita anche più volte di seguito a patto di avere carte da scartare, può farlo anche nel turno dell'avversario se starebbe per morire"
        self.icon = '🤤'

class SlabTheKiller(Character):
    def __init__(self):
        super().__init__("Slab The Killer", max_lives=4)
        self.desc = "Per evitare i suoi Bang servono due Mancato, un eventuale barile vale solo come un Mancato"
        self.icon = '🔪'
        #vale per tutte le carte bang non solo per la carta che si chiama Bang!

class SuzyLafayette(Character):
    def __init__(self):
        super().__init__("Suzy Lafayette", max_lives=4)
        self.desc = "Appena rimane senza carte in mano pesca immediatamente una carta dal mazzo"
        self.icon = '🔂'

class VultureSam(Character):
    def __init__(self):
        super().__init__("Vulture Sam", max_lives=4)
        self.desc = "Quando un personaggio viene eliminato prendi tutte le carte di quel giocatore e aggiungile alla tua mano, sia le carte in mano che quelle in gioco"
        self.icon = '💰'

class WillyTheKid(Character):
    def __init__(self):
        super().__init__("Willy The Kid", max_lives=4)
        self.desc = "Questo personaggio può giocare quanti bang vuole nel suo turno"
        self.icon = '🎉'

def all_characters(expansions: List[str]):
    from bang.expansions import DodgeCity
    base_chars = [
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
    if 'dodge_city' in expansions:
        base_chars.extend(DodgeCity.get_characters())
    return base_chars