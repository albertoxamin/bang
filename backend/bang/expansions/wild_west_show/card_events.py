import random

from bang.expansions.fistful_of_cards.card_events import CardEvent


class Bavaglio(CardEvent):
    def __init__(self):
        super().__init__("Bavaglio", "🤐")
        # I giocatori non possono parlare (ma possono gesticolare, mugugnare...). Chi parla perde 1 punto vita.
        # NOT IMPLEMENTED

class Camposanto(CardEvent):
    def __init__(self):
        super().__init__("Camposanto", "⚰")
        # All'inizio del proprio turno, ogni giocatore eliminato torna in gioco con 1 punto vita. Pesca il ruolo a caso fra quelli dei giocatori eliminati.

class DarlingValentine(CardEvent):
    def __init__(self):
        super().__init__("Darling Valentine", "💋")
        # All'inizio del proprio turno, ogni giocatore scarta le carte in mano e ne pesca dal mazzo altrettante.

class DorothyRage(CardEvent):
    def __init__(self):
        super().__init__("Dorothy Rage", "👩‍⚖️")
        # Nel proprio turno, ogni giocatore può obbligarne un altro a giocare una carta.

class HelenaZontero(CardEvent):
    def __init__(self):
        super().__init__("Helena Zontero", "💞")
        # Quando Helena entra in gioco, "estrai!": se esce Cuori o Quadri, rimescola i ruoli attivi tranne lo Sceriffo, e ridistribuiscili a caso.

class LadyRosaDelTexas(CardEvent):
    def __init__(self):
        super().__init__("Lady Rosa del Texas", "🩰")
        # Nel proprio turno, ogni giocatore può scambiarsi di posto con quello alla sua destra, il quale salta il prossimo turno.

class MissSusanna(CardEvent):
    def __init__(self):
        super().__init__("Miss Susanna", "👩‍🎤")
        # Nel proprio turno ogni giocatore deve giocare almeno 3 carte. Se non lo fa, perde 1 punto vita.

class RegolamentoDiConti(CardEvent):
    def __init__(self):
        super().__init__("Regolamento di conti", "🤠")
        # Tutte le carte possono essere giocate come se fossero BANG!. Le carte BANG! come se fossero Mancato!

class Sacagaway(CardEvent):
    def __init__(self):
        super().__init__("Sacagaway", "🏇")
        # Tutti i giocatori giocano a carte scoperte (tranne il ruolo!).

class WildWestShow(CardEvent):
    def __init__(self):
        super().__init__("Wild West Show", "🎪")
        # L'obiettivo di ogni giocatore diventa: "Rimani l'ultimo in gioco!"

def get_endgame_card():
    end_game = WildWestShow()
    end_game.expansion = 'wild-west-show'
    return end_game

def get_all_events(rng=random):
    cards = [
        Bavaglio(),
        Camposanto(),
        DarlingValentine(),
        DorothyRage(),
        HelenaZontero(),
        LadyRosaDelTexas(),
        MissSusanna(),
        RegolamentoDiConti(),
        Sacagaway(),
    ]
    rng.shuffle(cards)
    for c in cards:
        c.expansion = 'wild-west-show'
    return cards