import random
import bang.players as pl
from bang.cards import Card, Bang, Panico, CatBalou, Mancato


class TrainCard(Card):
    def __init__(self, name: str, is_locomotive: bool = False):
        super().__init__(suit=5, number=0, name=name)
        self.expansion_icon = "🚂"
        self.is_equipment = True
        self.is_locomotive = is_locomotive
        self.expansion = "train_robbery"
        self.type = "train"


# Circus Wagon: gli altri giocatori
# scartano una carta, in senso orario, a
# partire dal giocatore alla tua sinistra.
# Express Car: non puoi svolgere
# un altro turno extra dopo quello
# ottenuto da questo effetto, anche se
# riesci a giocare di nuovo Express Car.

# Ghost Car: giocabile su un
# qualsiasi giocatore, anche se già
# eliminato, te compreso. Non può
# essere giocato sullo Sceriffo.
# Se quel giocatore è/viene eliminato,
# invece ritorna/resta in gioco, senza
# punti vita. Non può guadagnare né
# perdere punti vita, e viene considerato
# un personaggio in gioco per tutti gli
# effetti (condizioni di vittoria, distanza
# tra giocatori, abilità dei personaggi,
# ecc.). Non avendo punti vita, deve
# scartare la sua intera mano alla fine
# del turno, ma può tenere qualsiasi
# carta in gioco di fronte a sé, incluso
# Ghost Car. Tuttavia, è eliminato
# dal gioco non appena Ghost Car
# viene scartato: nessuna ricompensa
# viene assegnata in questo caso se il
# giocatore è un Fuorilegge, e le abilità
# dei personaggi (ad es. Vulture Sam)
# non si attivano

# Lounge Car: i vagoni che peschi
# non contano per il normale limite di
# acquisizione di 1 vagone per turno. Se
# sei lo Sceriffo e peschi Ghost Car, devi
# darlo a un altro giocatore.

# Lumber Flatcar: gioca su un
# qualsiasi giocatore (compreso te).
# Finché questa carta è in gioco, quel
# giocatore vede gli altri giocatori a
# distanza aumentata di 1.

# Private Car: questo effetto non
# ti protegge da Gatling, Knife Revolver,
# l’abilità di Evan Babbit, e così via.
# Sleeper Car: puoi anche usare
# l’effetto una volta per turno con
# Indiani!, Duello, ecc.


class Ironhorse(TrainCard):
    """LOCOMOTIVA:
    Ogni giocatore, incluso colui che ha attivato l'effetto, è bersaglio di un BANG!
    Nessun giocatore è responsabile dell'eventuale perdita di punti vita.
    Se tutti i giocatori vengono eliminati allo stesso tempo, i Fuorilegge vincono.
    """

    def __init__(self):
        super().__init__("Ironhorse", is_locomotive=True)
        self.icon = "🚂"

    def play_card(self, player, against=None, _with=None) -> bool:
        player.game.attack(player, player.name, card_name=self.name)
        player.game.attack_others(player, card_name=self.name)
        return True


class Leland(TrainCard):
    """
    LOCOMOTIVA: svolgi l’effetto dell’Emporio, cominciando dal giocatore di turno e procedendo in senso orario.
    """

    def __init__(self):
        super().__init__("Leland", is_locomotive=True)
        self.icon = "🚂"

    def play_card(self, player, against=None, _with=None) -> bool:
        player.game.emporio(player)
        return True


class BaggageCar(TrainCard):
    """Scartalo: ottieni l'effetto di un Mancato!, Panico!, Cat Balou o di un BANG! extra.
    Discard this for a Missed!Panic!, Cat Balou, or an extra BANG!"""

    def __init__(self):
        super().__init__("Baggage Car")
        self.icon = "🚋🛄"

    def choose_callback(self, player: pl.Player, card_index):
        player.hand.append(player.available_cards[card_index])
        player.pending_action = pl.PendingAction.PLAY

    def play_card(self, player, against=None, _with=None) -> bool:
        player.set_choose_action(
            "choose_baggage_car",
            [Bang(4, 42), Mancato(4, 42), CatBalou(4, 42), Panico(4, 42)],
            self.choose_callback,
        )
        return True


class Caboose(TrainCard):
    """Pro scartare un altra tua carta bordo blu incuso un vagone come se fosse un Mancato!"""

    def __init__(self):
        super().__init__("Caboose")
        self.icon = "🚋"

    def play_card(self, player, against=None, _with=None) -> bool:
        return False


class CattleTruck(TrainCard):
    """Scartalo: guarda le 3 carte in cima agli scarti e pescane I"""

    def __init__(self):
        super().__init__("Cattle Truck")
        self.icon = "🚋🐄"

    def play_card(self, player, against=None, _with=None) -> bool:
        return True


class CircusWagon(TrainCard):
    """Scartalo: ogni altro giocatore deve scartare una carta che ha in gioco."""

    def __init__(self):
        super().__init__("Circus Wagon", is_locomotive=True)
        self.icon = "🚋🎪"

    def play_card(self, player, against=None, _with=None) -> bool:
        return True


class CoalHopper(TrainCard):
    """Scartalo: pesca una carta e scarta un vagone in gioco davanti a un giocatore a ma scelta."""

    def __init__(self):
        super().__init__("Coal Hopper")
        self.icon = "🚋🔥"

    def play_card(self, player, against=None, _with=None) -> bool:
        return True


class DiningCar(TrainCard):
    """A inizio turno, "estrai!": se è Cnori, recuperi I punto vita."""

    def __init__(self):
        super().__init__("Dining Car")
        self.icon = "🚋🍽"

    def play_card(self, player, against=None, _with=None) -> bool:
        return False


class ExpressCar(TrainCard):
    """Scarta tutte le carte in mano, poi gioca un altro turno"""

    def __init__(self):
        super().__init__("Express Car")
        self.icon = "🚋⚡"

    def play_card(self, player, against=None, _with=None) -> bool:
        return True


class GhostCar(TrainCard):
    """Giocalo su chiunque tranne lo Sceritfo. Se vieni eliminato, invece resti in gioco, ma non puo guadagnare ne perdere punti vita."""

    def __init__(self):
        super().__init__("Ghost Car")
        self.icon = "🚋👻"

    def play_card(self, player, against=None, _with=None) -> bool:
        return True


class LoungeCar(TrainCard):
    """Scartalo: pesca 2 vagoni dal mazzo, mettine I in gioco di fronte a te e 1 di fronte a un altro giocatore."""

    def __init__(self):
        super().__init__("Lounge Car")
        self.icon = "🚋🛋"

    def play_card(self, player, against=None, _with=None) -> bool:
        return True


class LumberFlatcar(TrainCard):
    """Giocalo su un qualsiasi giocatore (compreso te). Finché questa carta è in gioco, quel giocatore vede gli altri giocatori a distanza aumentata di 1."""

    def __init__(self):
        super().__init__("Lumber Flatcar")
        self.icon = "🚋🪵"

    def play_card(self, player, against=None, _with=None) -> bool:
        return True


class MailCar(TrainCard):
    """Scartalo: pesca 3 carte e dai 1 di esse a un altro giocatore a tua scelta."""

    def __init__(self):
        super().__init__("Mail Car")
        self.icon = "🚋📮"

    def play_card(self, player, against=None, _with=None) -> bool:
        return True


class ObservationCar(TrainCard):
    """Tu vedi gli altri a distanza -1. Gli altri a vedono a distanza +1."""

    def __init__(self):
        super().__init__("Observation Car")
        self.icon = "🚋👀"

    def play_card(self, player, against=None, _with=None) -> bool:
        return True


class PassengerCar(TrainCard):
    """Scartalo: pesca una carta (in mano o in gioco) da un altro giocatore"""

    def __init__(self):
        super().__init__("Passenger Car")
        self.icon = "🚋🚶"

    def play_card(self, player, against=None, _with=None) -> bool:
        return True


class PrisonerCar(TrainCard):
    """Le carte Duello e Indiani! giocate dagli altri giocatori non hanno effetto su di te."""

    def __init__(self):
        super().__init__("Prisoner Car")
        self.icon = "🚋👮🏻‍♂️"

    def play_card(self, player, against=None, _with=None) -> bool:
        return True


class PrivateCar(TrainCard):
    """se non hai carte in mano. non puoi essere bersaelio di carte BANG"""

    def __init__(self):
        super().__init__("Private Car")
        self.icon = "🚋💁🏻"

    def play_card(self, player, against=None, _with=None) -> bool:
        return True


class SleeperCar(TrainCard):
    """Una volta per turno, puoi scartare un'altra tua carta a bordo blu incluso."""

    def __init__(self):
        super().__init__("Sleeper Car")
        self.icon = "🚋🛌"

    def play_card(self, player, against=None, _with=None) -> bool:
        return True


def get_all_cards(rng=random):
    """Return a list of all train cards in the expansion"""
    cars = [
        BaggageCar(),
        Caboose(),
        CattleTruck(),
        CircusWagon(),
        CoalHopper(),
        DiningCar(),
        ExpressCar(),
        GhostCar(),
        LoungeCar(),
        LumberFlatcar(),
        MailCar(),
        ObservationCar(),
        PassengerCar(),
        PrisonerCar(),
        PrivateCar(),
        SleeperCar(),
    ]
    rng.shuffle(cars)
    return cars


def get_locomotives(rng=random):
    """Return a list of all locomotive cards in the expansion"""
    locs = [
        Ironhorse(),
        Leland(),
    ]
    rng.shuffle(locs)
    return locs
