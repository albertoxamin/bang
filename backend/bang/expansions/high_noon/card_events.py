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

class IlDottore(CardEvent):
    def __init__(self):
        super().__init__("Il Dottore", "👨‍⚕️")
        self.desc = "Il giocatore con meno vite recupera 1 vita"
        self.desc_eng = ""


class Sermone(CardEvent):
    def __init__(self):
        super().__init__("Sermone", "✝️")
        self.desc = "I giocatori non possono giocare Bang!"
        self.desc_eng = ""

class Sparatoria(CardEvent):
    def __init__(self):
        super().__init__("Sparatoria", "‼️")
        self.desc = "Il limite di bang è 2 invece che 1!"
        self.desc_eng = ""

class CorsaAllOro(CardEvent):
    def __init__(self):
        super().__init__("Corsa All'Oro", "‼️")
        self.desc = "Si gioca in senso antiorario!"
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
       CorsaAllOro(),
    #    IDalton(),
       IlDottore(),
       IlReverendo(),
       IlTreno(),
       Sbornia(),
       Sermone(),
       Sete(),
       Sparatoria(),
    ]
    random.shuffle(cards)
    cards.append(MezzogiornoDiFuoco())
    for c in cards:
        c.expansion = 'high-noon'
    return cards