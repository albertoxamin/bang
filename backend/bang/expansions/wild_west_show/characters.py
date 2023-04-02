from typing import List
import bang.cards as cs
from bang.characters import Character


class BigSpencer(Character):
    """
    Inizia con 5 carte. Non può giocare Mancato!
    """

    def __init__(self):
        super().__init__("Big Spencer", max_lives=9)
        self.icon = "🫘"


class FlintWestwood(Character):
    """
    Nel suo turno può scambiare una carta dalla mano con 2 carte a caso dalla mano di un altro giocatore.
    > NOTE: La carta dalla tua mano è a scelta, non a caso. Se il giocatore bersaglio ha una sola carta, ne ricevi solo una.
    """

    def __init__(self):
        super().__init__("Flint Westwood", max_lives=4)
        self.icon = "🔫"

    def special(self, player, data):
        if (
            not player.is_my_turn
            or not any((len(p.hand) > 0 for p in player.game.get_alive_players()))
            or not super().special(player, data)
        ):
            return False
        import bang.players as pls

        player.available_cards = player.hand.copy()
        player.choose_text = "choose_flint_special"
        player.pending_action = pls.PendingAction.CHOOSE
        player.special_use_count += 1
        player.notify_self()


class GaryLooter(Character):
    """
    Pesca tutte le carte in eccesso scartate dagli altri giocatori a fine turno.
    """

    def __init__(self):
        super().__init__("Gary Looter", max_lives=5)
        self.icon = "🥲"


class GreygoryDeckard(Character):
    """
    All'inizio del suo turno può pescare 2 personaggi a caso. Ha tutte le abilità dei personaggi pescati.
    """

    def __init__(self):
        super().__init__("Greygory Deckard", max_lives=4)
        self.icon = "👨‍🦳"


class JohnPain(Character):
    """
    Se ha meno di 6 carte in mano, quando un giocatore "estrae!" John aggiunge alla mano la carta appena estratta.
    """

    def __init__(self):
        super().__init__("John Pain", max_lives=4)
        self.icon = "🤕"


class LeeVanKliff(Character):
    """
    Nel suo turno, può scartare un BANG! per ripetere l'effetto di una carta a bordo marrone che ha appena giocato.
    """

    def __init__(self):
        super().__init__("Lee Van Kliff", max_lives=4)
        self.icon = "👨‍🦲"

    def special(self, player, data):
        if player.last_played_card is None:
            return False
        if (
            player.last_played_card.is_equipment
            or player.last_played_card.usable_next_turn
            or player.last_played_card.number == 42
            or not any(isinstance(c, cs.Bang) for c in player.hand)
            or not super().special(player, data)
        ):
            return False
        bang_index = next(
            (i for i, card in enumerate(player.hand) if isinstance(card, cs.Bang)), -1
        )
        bang_card = player.hand.pop(bang_index)
        print(f"{bang_card=}")
        player.game.deck.scrap(bang_card, player=player)
        player.last_played_card.must_be_used = True
        player.last_played_card.number = 42
        player.hand.append(player.last_played_card)
        print(f"{player.hand=}")
        player.notify_self()


class TerenKill(Character):
    """
    Ogni volta che sarebbe eliminato "estrai!": se non è Picche, Teren resta a 1 punto vita e pesca 1 carta.
    """

    def __init__(self):
        super().__init__("Teren Kill", max_lives=3)
        self.icon = "👨‍🦰"


class YoulGrinner(Character):
    """
    Prima di pescare, i giocatori con più carte in mano di lui devono dargli una carta a scelta.
    """

    def __init__(self):
        super().__init__("Youl Grinner", max_lives=4)
        self.icon = "🤡"


def all_characters() -> List[Character]:
    cards = [
        BigSpencer(),
        FlintWestwood(),
        # GaryLooter(),
        # GreygoryDeckard(),
        JohnPain(),
        LeeVanKliff(),
        TerenKill(),
        YoulGrinner(),
    ]
    for c in cards:
        c.expansion_icon = "🎪"
        c.expansion = "wild_west_show"
    return cards
