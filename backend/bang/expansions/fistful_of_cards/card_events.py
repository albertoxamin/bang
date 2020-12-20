from abc import ABC, abstractmethod

class CardEvent(ABC):
    def __init__(self, name, icon):
        self.name = name
        self.icon = icon

class Agguato(CardEvent):
    def __init__(self):
        super().__init__("Agguato", "🛁")
        self.desc = "La distanza base di tra 2 qualsiasi giocatori è 1"
        self.desc_eng = "The base distance from any 2 players is 1"

class Cecchino(CardEvent):
    def __init__(self): #TODO
        super().__init__("Cecchino", "👁")
        self.desc = "Nel proprio turno i giocatori possono scartare 2 Bang assieme per sparare un bang a cui servono 2 mancato"
        self.desc_eng = "During their turn, players can discard 2 Bang! to shoot a bang that requires 2 missed"

class DeadMan(CardEvent):
    def __init__(self):
        super().__init__("Dead Man", "⚰️")
        self.desc = "Al proprio turno il giocatore che è morto per primo torna in vita con 2 vite e 2 carte"
        self.desc_eng = "The first player that died return back to life with 2 hp and 2 cards"

class FratelliDiSangue(CardEvent):
    def __init__(self):#TODO
        super().__init__("Fratelli Di Sangue", "💉")
        self.desc = "All'inizio del proprio turno i giocatori possono perdere 1 vita per darla a un altro giocatore"
        self.desc_eng = "At the begin of their turn, payers can lose 1 hp to give it to another player"

class IlGiudice(CardEvent):
    def __init__(self):
        super().__init__("Il Giudice", "👨‍⚖️")
        self.desc = "Non si possono equipaggiare carte a se stessi o agli altri"
        self.desc_eng = "You can't equip cards on your or other players"

class Lazo(CardEvent):
    def __init__(self):
        super().__init__("Lazo", "📿")
        self.desc = "Le carte equipaggiate non hanno effetto"
        self.desc_eng = "Cards in the equipment slot do not work"

class LeggeDelWest(CardEvent):
    def __init__(self):
        super().__init__("Legge Del West", "⚖️")
        self.desc = "I giocatori mostrano la seconda carta che pescano e sono obbligati a usarla in quel turno (se possibile)"
        self.desc_eng = "Every player shows the second card that they draw and must use it in that round"

class LiquoreForte(CardEvent):
    def __init__(self):
        super().__init__("Liquore Forte", "🥃")
        self.desc = "I giocatori possono evitare di pescare per recuperare 1 vita (clicca sulla carta evento per farlo)"
        self.desc_eng = "Players can skip drawing to regain 1 HP (click on the event card to use)"

class MinieraAbbandonata(CardEvent):
    def __init__(self):
        super().__init__("Miniera Abbandonata", "⛏")
        self.desc = "I giocatori pescano dagli scarti e scartano in cima al mazzo"
        self.desc_eng = "Players draw from the discarded pile and discard to the deck"

class PerUnPugnoDiCarte(CardEvent):
    def __init__(self):#TODO
        super().__init__("Per Un Pugno Di Carte", "🎴")
        self.desc = "Nel suo turno giocatore subisce tanti bang quante carte ha in mano"
        self.desc_eng = "On his turn the player is target of as many Bang as how many cards he has in his hand"

class Peyote(CardEvent):
    def __init__(self):
        super().__init__("Peyote", "🌵")
        self.desc = "Invece che pescare il giocatore prova a indovinare il colore del seme, se lo indovina continua"
        self.desc_eng = "Instead of drawing, the player tries to guess the color of the suit, if he's right he repeats"

class Ranch(CardEvent):
    def __init__(self):#TODO
        super().__init__("Ranch", "🐮")
        self.desc = "Dopo aver pescato il giocatore può scartare quante carte vuole dalla mano e pescarne altrettante dal mazzo"
        self.desc_eng = "After drawing, the player can discard as many cards as he wants from his hand and draw as many from the deck"

class Rimbalzo(CardEvent):
    def __init__(self):#TODO
        super().__init__("Rimbalzo", "⏮")
        self.desc = "Il giocatore di turno può giocare bang contro le carte equipaggiate dagli altri giocatori, se non giocano mancato vengono scartate"
        self.desc_eng = "The player can play bang against the cards equipped by the other players, if they do not play miss they are discarded"

class RouletteRussa(CardEvent):
    def __init__(self):#TODO
        super().__init__("Roulette Russa", "🇷🇺")
        self.desc = "A partire dallo sceriffo, ogni giocatore scarta 1 mancato, il primo che non lo fa perde 2 vite"
        self.desc_eng = "Starting from the sheriff, every player discards 1 missed, the first one that doesn't loses 2 HP"

class Vendetta(CardEvent):
    def __init__(self):
        super().__init__("Vendetta", "😤")
        self.desc = "Alla fine del proprio turno il giocatore estrae, se esce ♥️ gioca un altro turno"
        self.desc_eng = "When ending the turn, the player flips a card, if it's ♥️ he plays another turn"

def get_all_events():
    return [
        Agguato(),
        # Cecchino(),
        DeadMan(),
        # FratelliDiSangue(),
        IlGiudice(),
        Lazo(),
        LeggeDelWest(),
        LiquoreForte(),
        MinieraAbbandonata(),
        # PerUnPugnoDiCarte(),
        Peyote(),
        # Ranch(),
        # Rimbalzo(),
        # RouletteRussa(),
        Vendetta(),
    ]