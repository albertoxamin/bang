from typing import List
from bang.characters import Character

class BlackFlower(Character):
    def __init__(self):
        super().__init__("Black Flower", max_lives=4)
        # Una volta nel tuo turno, puoi usare una carta di fiori per sparare un BANG! extra.
        self.icon = '🥀'

class ColoradoBill(Character):
    def __init__(self):
        super().__init__("Colorado Bill", max_lives=4)
        # Ogni volta che giochi una carta BANG!, "estrai!": se è Picche, il colpo non può essere evitato.
        self.icon = '♠️'

class DerSpotBurstRinger(Character):
    def __init__(self):
        super().__init__("Der Spot Burst Ringer", max_lives=4)
        # Una volta nel tuo turno, puoi usare una carta BANG! come Gatling.
        self.icon = '🫧'

class EvelynShebang(Character):
    def __init__(self):
        super().__init__("Evelyn Shebang", max_lives=4)
        # Puoi rinunciare a pescare carte nella tua fase di pesca. Per ogni carta non pescata, spari un BANG! a distanza raggiungibile, a un diverso bersaglio.
        self.icon = '📵'

class HenryBlock(Character):
    def __init__(self):
        super().__init__("Henry Block", max_lives=4)
        # Chiunque peschi o scarti una tua cartain gioco o in mano) è bersaglio di un BANG!.
        self.icon = '🚯'

class LemonadeJim(Character):
    def __init__(self):
        super().__init__("Lemonade Jim", max_lives=4)
        # Ogni volta che un altro giocatore gioca una Birra, puoi scartare una carta dalla mano per riguadagnare anche tu 1 punto vita.
        self.icon = '🍋'

class MickDefender(Character):
    def __init__(self):
        super().__init__("Mick Defender", max_lives=4)
        # Se sei bersaglio di una carta marrone (non BANG!), puoi usare una carta Mancato! evitarne 1 gli effetti. 
        self.icon = '⛔'

class TucoFranziskaner(Character):
    def __init__(self):
        super().__init__("Tuco Franziskaner", max_lives=4)
        # Durante la tua fase di pesca, se non hai carte blu in gioco, pesca 2 carte extra.
        self.icon = '🥬'

def all_characters() -> List[Character]:
    cards = [
        # BlackFlower(),
        # ColoradoBill(),
        # DerSpotBurstRinger(),
        # EvelynShebang(),
        # HenryBlock(),
        # LemonadeJim(),
        # MickDefender(),
        TucoFranziskaner(),
    ]
    for c in cards:
        c.expansion_icon = '👻️'
    return cards
