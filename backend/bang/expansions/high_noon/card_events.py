import random
from bang.expansions.fistful_of_cards.card_events import CardEvent

class Benedizione(CardEvent):
    def __init__(self):
        super().__init__("Benedizione", "🙏")
        self.desc = "Tutte le carte sono considerate di cuori ♥️"
        self.desc_eng = ""

class Maledizione(CardEvent):
    def __init__(self):
        super().__init__("Maledizione", "🤬")
        self.desc = "Tutte le carte sono considerate di picche ♠"
        self.desc_eng = ""

class Sbornia(CardEvent):
    def __init__(self):
        super().__init__("Sbornia", "🥴")
        self.desc = "I personaggi perdono la loro abilità speciale"
        self.desc_eng = ""

class Sete(CardEvent):
    def __init__(self):
        super().__init__("Sete", "🥵")
        self.desc = "I giocatori pescano solo 1 carta"
        self.desc_eng = ""

class IlTreno(CardEvent):
    def __init__(self):
        super().__init__("Il Treno", "🚂")
        self.desc = "I giocatori pescano 1 carta extra"
        self.desc_eng = ""

class IlReverendo(CardEvent):
    def __init__(self):
        super().__init__("Il Reverendo", "⛪️")
        self.desc = "Non si possono giocare birre"
        self.desc_eng = ""

class MezzogiornoDiFuoco(CardEvent):
    def __init__(self):
        super().__init__("Mezzogiorno di Fuoco", "🔥")
        self.desc = "Ogni giocatore perde 1 punto vita all'inizio del turno"
        self.desc_eng = "Every player loses 1 HP when their turn starts"

def get_all_events():
    cards = [
       Benedizione(),
       Maledizione(),
    #    CittaFantasma(),
    #    CorsaAllOro(),
    #    IDalton(),
    #    IlDottore(),
       IlReverendo(),
       IlTreno(),
       Sbornia(),
    #    Seromone(),
       Sete(),
    #    Sparatoria(),
    ]
    random.shuffle(cards)
    # cards.append(MezzogiornoDiFuoco())
    for c in cards:
        c.expansion = 'high-noon'
    return cards