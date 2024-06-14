import random
from bang.cards import Card, Bang, Panico, CatBalou, Mancato
from typing import TYPE_CHECKING

from globals import G, PendingAction

if TYPE_CHECKING:
    from bang.players import Player


class TrainCard(Card):
    def __init__(self, name: str, is_locomotive: bool = False):
        super().__init__(suit=5, number=0, name=name)
        self.expansion_icon = "🚂"
        self.is_equipment = True
        self.is_locomotive = is_locomotive
        self.expansion = "train_robbery"
        self.type = "train"
        self.implemented = True


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
    LOCOMOTIVA: svolgi l'effetto dell'Emporio, cominciando dal giocatore di turno e procedendo in senso orario.
    """

    def __init__(self):
        super().__init__("Leland", is_locomotive=True)
        self.icon = "🚂"

    def play_card(self, player, against=None, _with=None) -> bool:
        player.game.emporio(player)
        return True


class BaggageCar(TrainCard):
    """Scartalo: ottieni l'effetto di un Mancato!, Panico!, Cat Balou o di un BANG! extra.
    Discard this for a Missed! Panic!, Cat Balou, or an extra BANG!"""

    def __init__(self):
        super().__init__("Baggage Car")
        self.icon = "🚋🛄"

    def choose_callback(self, player: 'Player', card_index):
        player.hand.append(player.available_cards[card_index])
        player.pending_action = PendingAction.PLAY

    def play_card(self, player, against=None, _with=None) -> bool:
        player.set_choose_action(
            "choose_baggage_car",
            [Bang(4, 42), Mancato(4, 42), CatBalou(4, 42), Panico(4, 42)],
            self.choose_callback,
        )
        return True


class Caboose(TrainCard):
    """Puoi scartare un altra tua carta bordo blu incuso un vagone come se fosse un Mancato!"""

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

    def choose_card_callback(self, player: 'Player', card_index):
        chosen_card = player.available_cards.pop(card_index)
        player.game.deck.scrap_pile.pop(-card_index)
        player.hand.append(chosen_card)
        player.pending_action = PendingAction.PLAY
        player.notify_self()

    def play_card(self, player, against=None, _with=None) -> bool:
        drawn_cards = player.game.deck.peek_scrap_pile(n_cards=3)
        player.set_choose_action(
            "choose_cattle_truck",
            drawn_cards,
            self.choose_card_callback,
        )
        return True


class CircusWagon(TrainCard):
    """Scartalo: ogni altro giocatore deve scartare una carta che ha in gioco."""

    def __init__(self):
        super().__init__("Circus Wagon", is_locomotive=True)
        self.icon = "🚋🎪"

    def play_card(self, player, against=None, _with=None) -> bool:
        player.game.discard_others(player, card_name=self.name)
        return True

    @classmethod
    def choose_circus_wagon(cls, player: 'Player', card_index):
        player.game.deck.scrap(player.hand.pop(card_index), player=player)
        player.pending_action = PendingAction.WAIT
        player.game.responders_did_respond_resume_turn()
        player.notify_self()



class CoalHopper(TrainCard):
    """Scartalo: pesca una carta e scarta un vagone in gioco davanti a un giocatore a tua scelta."""

    def __init__(self):
        super().__init__("Coal Hopper")
        self.icon = "🚋🔥"
        self.need_target = True

    def play_card(self, player, against=None, _with=None) -> bool:
        if against is not None and len(player.game.get_player_named(against).equipment) > 0:
            player.game.steal_discard(player, against, self)
        return True


class DiningCar(TrainCard):
    """A inizio turno, "estrai!": se è Cuori, recuperi I punto vita."""

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
        while len(player.hand) > 0:
            player.game.deck.scrap(player.hand.pop(0), player=player)
            player.notify_self()
        player.play_turn()
        return True


class GhostCar(TrainCard):
    """Giocalo su chiunque tranne lo Sceritfo. Se vieni eliminato, invece resta in gioco, ma non puo guadagnare ne perdere punti vita."""

    def __init__(self):
        super().__init__("Ghost Car")
        self.icon = "🚋👻"
        self.implemented = False

    def play_card(self, player, against=None, _with=None) -> bool:
        return False


class LoungeCar(TrainCard):
    """Scartalo: pesca 2 vagoni dal mazzo, mettine I in gioco di fronte a te e 1 di fronte a un altro giocatore."""

    def __init__(self):
        super().__init__("Lounge Car")
        self.icon = "🚋🛋"
        self.implemented = False

    def play_card(self, player, against=None, _with=None) -> bool:
        return True


class LumberFlatcar(TrainCard):
    """Giocalo su un qualsiasi giocatore (compreso te). Finché questa carta è in gioco, quel giocatore vede gli altri giocatori a distanza aumentata di 1."""

    def __init__(self):
        super().__init__("Lumber Flatcar")
        self.icon = "🚋🪵"
        self.sight_mod = -1

    def play_card(self, player, against=None, _with=None) -> bool:
        return False


class MailCar(TrainCard):
    """Scartalo: pesca 3 carte e dai 1 di esse a un altro giocatore a tua scelta."""

    def __init__(self):
        super().__init__("Mail Car")
        self.icon = "🚋📮"

    def choose_card_callback(self, player: 'Player', card_index):
        chosen_card = player.available_cards.pop(card_index)
        player.hand.extend(player.available_cards)
        player.set_choose_action(
            "choose_other_player",
            player.game.get_other_players(player),
            lambda p, other_player_index: self.choose_player_callback(p, other_player_index, chosen_card)
        )

    def choose_player_callback(self, player: 'Player', other_player_index, chosen_card):
        pl_name = player.game.get_other_players(player)[other_player_index]["name"]
        other_player = player.game.get_player_named(pl_name)
        other_player.hand.append(chosen_card)
        G.sio.emit(
            "card_drawn",
            room=player.game.name,
            data={"player": pl_name, "pile": player.name},
        )
        other_player.notify_self()
        player.pending_action = PendingAction.PLAY

    def play_card(self, player, against=None, _with=None) -> bool:
        drawn_cards = [player.game.deck.draw(player=player) for _ in range(3)]
        player.set_choose_action(
            "choose_mail_car",
            drawn_cards,
            self.choose_card_callback,
        )
        return True


class ObservationCar(TrainCard):
    """Tu vedi gli altri a distanza -1. Gli altri a vedono a distanza +1."""

    def __init__(self):
        super().__init__("Observation Car")
        self.icon = "🚋👀"
        self.sight_mod = 1
        self.vis_mod = 1

    def play_card(self, player, against=None, _with=None) -> bool:
        return False


class PassengerCar(TrainCard):
    """Scartalo: pesca una carta (o in mano o in gioco) da un altro giocatore"""

    def __init__(self):
        super().__init__("Passenger Car")
        self.icon = "🚋🚶"
        self.range = 99
        self.need_target = True


    def play_card(self, player, against=None, _with=None) -> bool:
        if (
            against is not None
            and (len(player.equipment) > 0 or len(player.equipment) > 0)
        ):
            player.game.steal_discard(player, against, self)
            return True
        return False


class PrisonerCar(TrainCard):
    """Le carte Duello e Indiani! giocate dagli altri giocatori non hanno effetto su di te."""

    def __init__(self):
        super().__init__("Prisoner Car")
        self.icon = "🚋👮🏻‍♂️"

    def play_card(self, player, against=None, _with=None) -> bool:
        return False


class PrivateCar(TrainCard):
    """Se non hai carte in mano, non puoi essere bersaglio di carte BANG"""

    def __init__(self):
        super().__init__("Private Car")
        self.icon = "🚋💁🏻"

    def play_card(self, player, against=None, _with=None) -> bool:
        return False


class SleeperCar(TrainCard):
    """Una volta per turno, puoi scartare un'altra tua carta a bordo blu incluso."""

    def __init__(self):
        super().__init__("Sleeper Car")
        self.icon = "🚋🛌"

    def choose_card_callback(self, player: 'Player', card_index):
        player.game.deck.scrap(player.equipment.pop(card_index), player=player)
        player.pending_action = PendingAction.PLAY
        self.usable_next_turn = True
        self.can_be_used_now = False
        player.notify_self()

    def play_card(self, player, against=None, _with=None) -> bool:
        if not self.can_be_used_now:
            return False
        player.set_choose_action(
            "choose_sleeper_car",
            player.equipment,
            self.choose_card_callback,
        )
        return False


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
    cars = [c for c in cars if c.implemented]
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
