import random
import bang.cards as cs
import bang.roles as roles
import bang.players as players
from globals import G

from bang.expansions.fistful_of_cards.card_events import CardEvent


class WildWestShowCardEvent(CardEvent):
    """
    Base class for all card events in the Wild West Show expansion
    """

    def __init__(self, name, icon):
        super().__init__(name, icon)
        self.expansion = "wild-west-show"


# class Bavaglio(CardEvent):
#     def __init__(self):
#         super().__init__("Bavaglio", "🤐")
#         # I giocatori non possono parlare (ma possono gesticolare, mugugnare...). Chi parla perde 1 punto vita.
#         # NOT IMPLEMENTED


class Camposanto(WildWestShowCardEvent):
    """
    All'inizio del proprio turno, ogni giocatore eliminato torna in gioco con 1 punto vita. Pesca il ruolo a caso fra quelli dei giocatori eliminati.
    """

    def __init__(self):
        super().__init__("Camposanto", "⚰")


class DarlingValentine(WildWestShowCardEvent):
    """
    All'inizio del proprio turno, ogni giocatore scarta le carte in mano e ne pesca dal mazzo altrettante.
    """

    def __init__(self):
        super().__init__("Darling Valentine", "💋")


class DorothyRage(WildWestShowCardEvent):
    """
    Nel proprio turno, ogni giocatore può obbligarne un altro a giocare una carta.
    """

    def __init__(self):
        super().__init__("Dorothy Rage", "👩‍⚖️")


class HelenaZontero(WildWestShowCardEvent):
    """
    Quando Helena entra in gioco, "estrai!": se esce Cuori o Quadri, rimescola i ruoli attivi tranne lo Sceriffo, e ridistribuiscili a caso.
    """

    def __init__(self):
        super().__init__("Helena Zontero", "💞")

    def on_flipped(self, game):
        c = game.deck.pick_and_scrap()
        G.sio.emit(
            "chat_message",
            room=game.name,
            data=f"_flipped|Helena Zontero|{c.name}|{c.num_suit()}",
        )
        if c.check_suit(game, [cs.Suit.HEARTS, cs.Suit.DIAMONDS]):
            G.sio.emit(
                "chat_message",
                room=game.name,
                data=f"_swapped_roles|Helena Zontero|{c.name}|{c.num_suit()}",
            )
            pls = [p for p in game.players if not isinstance(p.role, roles.Sheriff)]
            newroles = [p.role for p in pls]
            game.rng.shuffle(newroles)
            for p in pls:
                p.set_role(newroles.pop(game.rng.randint(0, len(newroles) - 1)))

        return super().on_flipped(game)


class LadyRosaDelTexas(WildWestShowCardEvent):
    """
    Nel proprio turno, ogni giocatore può scambiarsi di posto con quello alla sua destra, il quale salta il prossimo turno.
    """

    def __init__(self):
        super().__init__("Lady Rosa del Texas", "🩰")

    def on_clicked(self, game, player):
        super().on_clicked(game, player)
        nextp = game.next_player()
        i, j = game.players_map[player.name], game.players_map[nextp.name]
        game.players[i], game.players[j] = nextp, player
        game.players_map[player.name], game.players_map[nextp.name] = j, i
        game.turn = j
        game.notify_all()


class MissSusanna(WildWestShowCardEvent):
    """
    Nel proprio turno ogni giocatore deve giocare almeno 3 carte. Se non lo fa, perde 1 punto vita.
    """

    def __init__(self):
        super().__init__("Miss Susanna", "👩‍🎤")


class RegolamentoDiConti(WildWestShowCardEvent):
    """
    Tutte le carte possono essere giocate come se fossero BANG!. Le carte BANG! come se fossero Mancato!
    """

    def __init__(self):
        super().__init__("Regolamento di Conti", "🤠")

    def on_clicked(self, game, player):
        super().on_clicked(game, player)
        if (
            len(player.hand) > 0
            and not player.has_played_bang
            and any(
                (
                    player.get_sight() >= p["dist"]
                    for p in game.get_visible_players(player)
                )
            )
        ):
            player.available_cards = player.hand.copy()
            player.pending_action = players.PendingAction.CHOOSE
            player.choose_text = "choose_play_as_bang"
            player.notify_self()


class Sacagaway(WildWestShowCardEvent):
    """
    Tutti i giocatori giocano a carte scoperte (tranne il ruolo!).
    """

    def __init__(self):
        super().__init__("Sacagaway", "🌄")


class WildWestShow(WildWestShowCardEvent):
    """
    L'obiettivo di ogni giocatore diventa: "Rimani l'ultimo in gioco!"
    """

    def __init__(self):
        super().__init__("Wild West Show", "🎪")

    def on_flipped(self, game):
        for player in game.players:
            player.set_role(roles.Renegade())
        return super().on_flipped(game)


def get_endgame_card():
    """Return the endgame card for this expansion"""
    return WildWestShow()


def get_all_events(rng=random):
    """Return all the events for this expansion shuffled, excluding the endgame card"""
    cards = [
        Camposanto(),
        DarlingValentine(),
        # DorothyRage(),
        HelenaZontero(),
        LadyRosaDelTexas(),
        MissSusanna(),
        RegolamentoDiConti(),
        Sacagaway(),
    ]
    rng.shuffle(cards)
    return cards
