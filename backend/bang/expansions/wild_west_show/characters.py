from typing import List
from bang.characters import Character

class BigSpencer(Character):
    def __init__(self):
        super().__init__("Big Spencer", max_lives=9)
        # Inizia con 5 carte. Non può giocare Mancato!
        self.icon = '🫘'

class FlintWestwood(Character):
    def __init__(self):
        super().__init__("Flint Westwood", max_lives=4)
        # Nel suo turno può scambiare una carta dalla mano con 2 carte a caso dalla mano di un altro giocatore.
        self.icon = '🔫'

class GaryLooter(Character):
    def __init__(self):
        super().__init__("Gary Looter", max_lives=5)
        # Pesca tutte le carte in eccesso scartate dagli altri giocatori a fine turno.
        self.icon = '🥲'

class GreygoryDeckard(Character):
    def __init__(self):
        super().__init__("Greygory Deckard", max_lives=4)
        # All'inizio del suo turno può pescare 2 personaggi a caso. Ha tutte le abilità dei personaggi pescati.
        self.icon = '👨‍🦳'    

class JohnPain(Character):
    def __init__(self):
        super().__init__("John Pain", max_lives=4)
        # Se ha meno di 6 carte in mano, quando un giocatore "estrae!" John aggiunge alla mano la carta appena estratta.
        self.icon = '🤕'

class LeeVanKliff(Character):
    def __init__(self):
        super().__init__("Lee Van Kliff", max_lives=4)
        # Nel suo turno, può scartare un BANG! per ripetere l'effetto di una carta a bordo marrone che ha appena giocato.
        self.icon = '👨‍🦲'

class TerenKill(Character):
    def __init__(self):
        super().__init__("Teren Kill", max_lives=3)
        # Ogni volta che sarebbe eliminato "estrai!": se non è Picche, Teren resta a 1 punto vita e pesca 1 carta.
        self.icon = '👨‍🦰'

class YoulGrinner(Character):
    def __init__(self):
        super().__init__("Youl Grinner", max_lives=4)
        # Prima di pescare, i giocatori con più carte in mano di lui devono dargli una carta a scelta.
        self.icon = '🤡'

def all_characters() -> List[Character]:
    cards = [
        BigSpencer(),
        FlintWestwood(),
        GaryLooter(),
        GreygoryDeckard(),
        JohnPain(),
        LeeVanKliff(),
        TerenKill(),
        YoulGrinner(),
    ]
    for c in cards:
        c.expansion_icon = '🎪'
        c.expansion = 'wild_west_show'
    return cards
