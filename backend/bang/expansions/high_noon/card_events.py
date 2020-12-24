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
        self.desc = "I personaggi perdono le loro abilità speciali"
        self.desc_eng = ""

class Sete(CardEvent):
    def __init__(self):
        super().__init__("Sete", "🥵")
        self.desc = "I giocatori pescano 1 carta in meno nella loro fase 1"
        self.desc_eng = ""

class IlTreno(CardEvent):
    def __init__(self):
        super().__init__("Il Treno", "🚂")
        self.desc = "I giocatori pescano 1 carta extra nella loro fase 1"
        self.desc_eng = ""

class IlReverendo(CardEvent):
    def __init__(self):
        super().__init__("Il Reverendo", "⛪️")
        self.desc = "Non si possono giocare le carte Birra"
        self.desc_eng = ""

class IlDottore(CardEvent):
    def __init__(self):
        super().__init__("Il Dottore", "👨‍⚕️")
        self.desc = "Il/i giocatore/i con meno vite ne recupera/no una"
        self.desc_eng = ""

class Sermone(CardEvent):
    def __init__(self):
        super().__init__("Sermone", "✝️")
        self.desc = "I giocatori non possono giocare Bang! durante il loro turno"
        self.desc_eng = ""

class Sparatoria(CardEvent):
    def __init__(self):
        super().__init__("Sparatoria", "🔫🔫")
        self.desc = "Il limite di Bang! per turno è 2 invece che 1"
        self.desc_eng = ""

class CorsaAllOro(CardEvent):
    def __init__(self):
        super().__init__("Corsa All'Oro", "🌟")
        self.desc = "Si gioca per un intero giro in senso antiorario, tuttavia gli effetti delle carte rimangono invariati"
        self.desc_eng = ""

class IDalton(CardEvent):
    def __init__(self):
        super().__init__("I Dalton", "🙇‍♂️")
        self.desc = "Chi ha carte blu in gioco ne scarta 1 a sua scelta"
        self.desc_eng = ""

class Manette(CardEvent):
    def __init__(self):
        super().__init__("Manette", "🔗")
        self.desc = "Dopo aver pescato in fase 1, il giocatore di turno dichiara un seme: potrà usare solamente carte di quel seme nel suo turno"
        self.desc_eng = ""

class NuovaIdentita(CardEvent):
    def __init__(self):
        super().__init__("Nuova Identità", "🕶")
        self.desc = "All'inizio del proprio turno, ogni giocatore potrà decidere se sostituire il suo personaggio attuale con quello era stato proposto ad inizio partita, se lo fa riparte con 2 punti vita"
        self.desc_eng = ""

class CittaFantasma(CardEvent):
    def __init__(self):
        super().__init__("Città Fantasma", "👻")
        self.desc = "Tutti i giocatori morti tornano in vita al proprio turno, non possono morire e pescano 3 carte invece che 2. Quando terminano il turno tornano morti."
        self.desc_eng = ""

class MezzogiornoDiFuoco(CardEvent):
    def __init__(self):
        super().__init__("Mezzogiorno di Fuoco", "🔥")
        self.desc = "Ogni giocatore perde 1 punto vita all'inizio del turno"
        self.desc_eng = "Every player loses 1 HP when their turn starts"

def get_endgame_card():
    end_game = MezzogiornoDiFuoco()
    end_game.expansion = 'high-noon'
    return end_game

def get_all_events():
    cards = [
       Benedizione(),
       Maledizione(),
       CittaFantasma(),
       CorsaAllOro(),
       IDalton(),
       IlDottore(),
       IlReverendo(),
       IlTreno(),
       Sbornia(),
       Sermone(),
       Sete(),
       Sparatoria(),
    #    Manette(),
    #    NuovaIdentita(),
    ]
    random.shuffle(cards)
    for c in cards:
        c.expansion = 'high-noon'
    return cards