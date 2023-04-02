from abc import ABC, abstractmethod
import random
import bang.players as players
import bang.roles as r
import bang.cards as cs

from globals import G


class CardEvent(ABC):
    """Base class for all event cards"""

    def __init__(self, name, icon):
        self.name = name
        self.icon = icon

    def on_flipped(self, game):
        """Default on flipped event

        Args:
            game (Game): the game object
        """
        print(f"{game.name}: flip new event {self.name}")
        G.sio.emit(
            "chat_message",
            room=game.name,
            data={
                "color": "orange",
                "text": f"_flip_event|{self.name}",
            },
        )
        return

    def on_clicked(self, game, player):
        """Default on clicked event

        Args:
            game (Game): the game object
            player (Player): the player that clicked the card
        """
        print(f"{game.name}: {player.name} clicked event {self.name}")
        return


class Agguato(CardEvent):
    """La distanza base tra 2 qualsiasi giocatori è 1

    The distance between 2 players is always 1"""

    def __init__(self):
        super().__init__("Agguato", "🛁")


class Cecchino(CardEvent):
    """Nel proprio turno i giocatori possono
    scartare 2 Bang assieme per sparare un bang che necessita 2 mancato (clicca la carta)

    In your turn you can discard 2 Bang together to shoot a bang that needs 2 miss (click the card)
    """

    def __init__(self):
        super().__init__("Cecchino", "👁")


class DeadMan(CardEvent):
    """Al proprio turno il giocatore che è morto per primo torna in vita con 2 vite e 2 carte

    The first player that died returns back to life with 2 hp and 2 cards"""

    def __init__(self):
        super().__init__("Dead Man", "⚰️")

    def on_flipped(self, game):
        game.did_resuscitate_deadman = False
        return super().on_flipped(game)


class FratelliDiSangue(CardEvent):
    """All'inizio del proprio turno, i giocatori possono perdere 1 vita (tranne l'ultimo) per darla a un altro giocatore"""

    def __init__(self):
        super().__init__("Fratelli Di Sangue", "💉")


class IlGiudice(CardEvent):
    """Non si possono equipaggiare carte a se stessi o agli altri"""

    def __init__(self):
        super().__init__("Il Giudice", "👨‍⚖️")


class Lazo(CardEvent):
    """Le carte equipaggiate non hanno effetto"""

    def __init__(self):
        super().__init__("Lazo", "📿")


class LeggeDelWest(CardEvent):
    """I giocatori mostrano la seconda carta che pescano e sono obbligati a usarla in quel turno (se possibile)"""

    def __init__(self):
        super().__init__("Legge Del West", "⚖️")


class LiquoreForte(CardEvent):
    """I giocatori possono evitare di pescare per recuperare 1 vita (clicca sulla carta evento per farlo)"""

    def __init__(self):
        super().__init__("Liquore Forte", "🥃")


class MinieraAbbandonata(CardEvent):
    """I giocatori pescano dagli scarti nella loro fase 1 e scartano in cima al mazzo nella loro fase 3 (se gli scarti finiscono, è necessario pescare e scartare in cima al mazzo)"""

    def __init__(self):
        super().__init__("Miniera Abbandonata", "⛏")


class PerUnPugnoDiCarte(CardEvent):
    """All'inizio del proprio turno, il giocatore subisce tanti bang quante carte ha in mano"""

    def __init__(self):
        super().__init__("Per Un Pugno Di Carte", "🎴")


class Peyote(CardEvent):
    """Invece che pescare il giocatore prova a indovinare il colore del seme, se lo indovina aggiunge la carta alla mano e continua provando ad indovinare la carta successiva"""

    def __init__(self):
        super().__init__("Peyote", "🌵")


class Ranch(CardEvent):
    """Dopo aver pescato il giocatore può scartare quante carte vuole dalla mano e pescarne altrettante dal mazzo"""

    def __init__(self):
        super().__init__("Ranch", "🐮")


class Rimbalzo(CardEvent):
    """Il giocatore di turno può giocare bang contro le carte equipaggiate dagli altri giocatori, se non giocano mancato vengono scartate (clicca la carta evento)"""

    def __init__(self):
        super().__init__("Rimbalzo", "⏮")

    def on_clicked(self, game, player):
        super().on_clicked(game, player)
        if any((c.name == cs.Bang(0, 0).name for c in player.hand)):
            player.available_cards = [
                {
                    "name": p.name,
                    "icon": p.role.icon
                    if (game.initial_players == 3)
                    else "⭐️"
                    if isinstance(p.role, r.Sheriff)
                    else "🤠",
                    "is_character": True,
                    "avatar": p.avatar,
                    "is_player": True,
                }
                for p in game.get_alive_players()
                if len(p.equipment) > 0 and p != player
            ]
            player.available_cards.append({"icon": "❌", "noDesc": True})
            player.choose_text = "choose_rimbalzo_player"
            player.pending_action = players.PendingAction.CHOOSE
            player.using_rimbalzo = 1
            player.notify_self()


class RouletteRussa(CardEvent):
    """A partire dallo sceriffo, ogni giocatore scarta 1 mancato, il primo che non lo fa perde 2 vite"""

    def __init__(self):
        super().__init__("Roulette Russa", "🇷🇺")
        # self.desc_eng = "Starting from the sheriff, every player discards 1 missed, the first one that doesn't loses 2 HP"


class Vendetta(CardEvent):
    """Alla fine del proprio turno il giocatore estrae dal mazzo, se esce ♥️ gioca un altro turno (ma non estrae di nuovo)"""

    def __init__(self):
        super().__init__("Vendetta", "😤")
        # self.desc_eng = "When ending the turn, the player flips a card from the deck, if it's ♥️ he plays another turn (but he does not flip another card)"


def get_endgame_card():
    end_game = PerUnPugnoDiCarte()
    end_game.expansion = (  # pylint: disable=attribute-defined-outside-init
        "fistful-of-cards"
    )
    return end_game


def get_all_events(rng=random):
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
    rng.shuffle(cards)
    for card in cards:
        card.expansion = (  # pylint: disable=attribute-defined-outside-init
            "fistful-of-cards"
        )
    return cards
