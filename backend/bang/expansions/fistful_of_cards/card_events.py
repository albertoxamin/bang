from abc import ABC, abstractmethod
import random

class CardEvent(ABC):
    def __init__(self, name, icon):
        self.name = name
        self.icon = icon

class Agguato(CardEvent):
    def __init__(self):
        super().__init__("Agguato", "🛁")
        #self.desc = "La distanza base tra 2 qualsiasi giocatori è 1"
        #self.desc_eng = "The base distance from any 2 players is 1"

class Cecchino(CardEvent):
    def __init__(self):
        super().__init__("Cecchino", "👁")
        #self.desc = "Nel proprio turno i giocatori possono scartare 2 Bang assieme per sparare un bang che necessita 2 mancato (clicca la carta)"
        #self.desc_eng = "During their turn, players can discard 2 Bang! to shoot a bang that requires 2 missed (click the card)"

class DeadMan(CardEvent):
    def __init__(self):
        super().__init__("Dead Man", "⚰️")
        #self.desc = "Al proprio turno il giocatore che è morto per primo torna in vita con 2 vite e 2 carte"
        #self.desc_eng = "The first player that died returns back to life with 2 hp and 2 cards"

class FratelliDiSangue(CardEvent):
    def __init__(self):
        super().__init__("Fratelli Di Sangue", "💉")
        #self.desc = "All'inizio del proprio turno, i giocatori possono perdere 1 vita (tranne l'ultimo) per darla a un altro giocatore"
        #self.desc_eng = "At the begin of their turn, payers can lose 1 hp (except the last one) to give it to another player"

class IlGiudice(CardEvent):
    def __init__(self):
        super().__init__("Il Giudice", "👨‍⚖️")
        #self.desc = "Non si possono equipaggiare carte a se stessi o agli altri"
        #self.desc_eng = "You can't equip cards on your or other players"

class Lazo(CardEvent):
    def __init__(self):
        super().__init__("Lazo", "📿")
        #self.desc = "Le carte equipaggiate non hanno effetto"
        #self.desc_eng = "Cards in the equipment slot do not work"

class LeggeDelWest(CardEvent):
    def __init__(self):
        super().__init__("Legge Del West", "⚖️")
        #self.desc = "I giocatori mostrano la seconda carta che pescano e sono obbligati a usarla in quel turno (se possibile)"
        #self.desc_eng = "Every player shows the second card that they draw and must use it in that round (if it is possible)"

class LiquoreForte(CardEvent):
    def __init__(self):
        super().__init__("Liquore Forte", "🥃")
        #self.desc = "I giocatori possono evitare di pescare per recuperare 1 vita (clicca sulla carta evento per farlo)"
        #self.desc_eng = "Players can skip drawing to regain 1 HP (click on the event card to use)"

class MinieraAbbandonata(CardEvent):
    def __init__(self):
        super().__init__("Miniera Abbandonata", "⛏")
        #self.desc = "I giocatori pescano dagli scarti nella loro fase 1 e scartano in cima al mazzo nella loro fase 3 (se gli scarti finiscono, è necessario pescare e scartare in cima al mazzo)"
        #self.desc_eng = "Players draw from the discarded pile in their phase 1 and discard to the top of the deck during phase 3 (if the discaded pile runs out, they must draw and discard on top of the deck)"

class PerUnPugnoDiCarte(CardEvent):
    def __init__(self):
        super().__init__("Per Un Pugno Di Carte", "🎴")
        #self.desc = "All'inizio del proprio turno, il giocatore subisce tanti bang quante carte ha in mano"
        #self.desc_eng = "On the beginning of his turn, the player is target of as many Bang as how many cards he has in his hand"

class Peyote(CardEvent):
    def __init__(self):
        super().__init__("Peyote", "🌵")
        #self.desc = "Invece che pescare il giocatore prova a indovinare il colore del seme, se lo indovina aggiunge la carta alla mano e continua provando ad indovinare la carta successiva"
        #self.desc_eng = "Instead of drawing, the player tries to guess the color of the suit, if he's right he adds the card to the hand and continues trying to guess the next card"

class Ranch(CardEvent):
    def __init__(self):
        super().__init__("Ranch", "🐮")
        #self.desc = "Dopo aver pescato il giocatore può scartare quante carte vuole dalla mano e pescarne altrettante dal mazzo"
        #self.desc_eng = "After drawing, the player can discard as many cards as he wants from his hand and draw as many from the deck"

class Rimbalzo(CardEvent):
    def __init__(self):
        super().__init__("Rimbalzo", "⏮")
        #self.desc = "Il giocatore di turno può giocare bang contro le carte equipaggiate dagli altri giocatori, se non giocano mancato vengono scartate (clicca la carta evento)"
        #self.desc_eng = "The player can play bang against the cards equipped by the other players, if they do not play miss they are discarded (click the event card)"

class RouletteRussa(CardEvent):
    def __init__(self):
        super().__init__("Roulette Russa", "🇷🇺")
        #self.desc = "A partire dallo sceriffo, ogni giocatore scarta 1 mancato, il primo che non lo fa perde 2 vite"
        #self.desc_eng = "Starting from the sheriff, every player discards 1 missed, the first one that doesn't loses 2 HP"

class Vendetta(CardEvent):
    def __init__(self):
        super().__init__("Vendetta", "😤")
        #self.desc = "Alla fine del proprio turno il giocatore estrae dal mazzo, se esce ♥️ gioca un altro turno (ma non estrae di nuovo)"
        #self.desc_eng = "When ending the turn, the player flips a card from the deck, if it's ♥️ he plays another turn (but he does not flip another card)"

def get_endgame_card():
    end_game = PerUnPugnoDiCarte()
    end_game.expansion = 'fistful-of-cards'
    return end_game

def get_all_events():
    cards = [
        Agguato(),
        Cecchino(),
        DeadMan(),
        FratelliDiSangue(),
        IlGiudice(),
        Lazo(),
        LeggeDelWest(),
        LiquoreForte(),
        MinieraAbbandonata(),
        Peyote(),
        Ranch(),
        Rimbalzo(),
        RouletteRussa(),
        Vendetta(),
    ]
    random.shuffle(cards)
    for c in cards:
        c.expansion = 'fistful-of-cards'
    return cards