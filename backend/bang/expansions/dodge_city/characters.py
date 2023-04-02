from typing import List
from bang.characters import Character


class PixiePete(Character):
    """All'inizio del turno pesca 3 carte invece che 2

    He draws 3 cards instead of 2"""

    def __init__(self):
        super().__init__("Pixie Pete", max_lives=3)
        self.icon = "☘️"


class TequilaJoe(Character):
    """Se gioca la carta Birra recupera 2 vite invece che una sola

    When he plays Beer, he regains 2 Health Points"""

    def __init__(self):
        super().__init__("Tequila Joe", max_lives=4)
        self.icon = "🍻"


class GregDigger(Character):
    """Quando un giocatore muore, recupera fino a 2 vite

    Whenever a player dies, he regains up to 2 lives"""

    def __init__(self):
        super().__init__("Greg Digger", max_lives=4)
        self.icon = "🦴"


class HerbHunter(Character):
    """Quando un giocatore muore, pesca 2 carte

    Whenever a player dies, he draws 2 cards"""

    def __init__(self):
        super().__init__("Herb Hunter", max_lives=4)
        self.icon = "⚰️"


class ElenaFuente(Character):
    """Può usare una carta qualsiasi nella sua mano come mancato

    She can use any card of her hand as missed"""

    def __init__(self):
        super().__init__("Elena Fuente", max_lives=3)
        self.icon = "🧘‍♀️"


class BillNoface(Character):
    """All'inizio del turno pesca 1 carta + 1 carta per ogni ferita che ha

    Draw 1 card + 1 card for each wound he has"""

    def __init__(self):
        super().__init__("Bill Noface", max_lives=4)
        self.icon = "🙈"


class MollyStark(Character):
    """Quando usa volontariamente una carta che ha in mano, fuori dal suo turno, ne ottiene un'altra dal mazzo

    When she uses a card from her hand outside her turn, she draws a card."""

    def __init__(self):
        super().__init__("Molly Stark", max_lives=4)
        self.icon = "🙅‍♀️"


class ApacheKid(Character):
    """Le carte di quadri ♦️ giocate contro di lui non hanno effetto (non vale durante i duelli)

    Cards of diamonds ♦️ played against him, do no have effect (doesn't work in duels).
    """

    def __init__(self):
        super().__init__("Apache Kid", max_lives=3)
        self.icon = "♦️"


class SeanMallory(Character):
    """Quando finisce il suo turno può tenere fino a 10 carte in mano

    He can keep up to 10 cards in his hand when ending the turn."""

    def __init__(self):
        super().__init__("Sean Mallory", max_lives=3)
        self.icon = "🍟"


class BelleStar(Character):
    """Nel suo turno le carte verdi degli altri giocatori non hanno effetto.

    During her turn the green cards of the other players do not work."""

    def __init__(self):
        super().__init__("Belle Star", max_lives=4)
        self.icon = "❎"


class VeraCuster(Character):
    """Prima di pescare le sue carte può scegliere l'abilità speciale di un altro giocatore fino al prossimo turno.

    Before drawing, she may choose the special ability on another alive player. This ability is used until next turn.
    """

    def __init__(self):
        super().__init__("Vera Custer", max_lives=3)
        self.icon = "🎭"


class ChuckWengam(Character):
    """Durante il suo turno può perdere una vita per pescare 2 carte dal mazzo.

    On his turn he may decide to lose 1 HP to draw 2 cards from the deck."""

    def __init__(self):
        super().__init__("Chuck Wengam", max_lives=4)
        self.icon = "💰"

    def special(self, player, data):
        if super().special(player, data):
            if player.lives > 1 and player.is_my_turn:
                player.lives -= 1
                player.game.deck.draw(True, player=player)
                player.game.deck.draw(True, player=player)
                player.notify_self()
                return True
        return False


class PatBrennan(Character):
    """Invece di pescare può prendere una carta dall'equipaggiamento di un altro giocatore.

    Instead of drawing he can steal a card from the equipment of another player."""

    def __init__(self):
        super().__init__("Pat Brennan", max_lives=4)
        self.icon = "🤗"


class JoseDelgado(Character):
    """Può scartare una carta blu per pescare 2 carte.

    He can discard a blue card to draw 2 cards."""

    def __init__(self):
        super().__init__("José Delgado", max_lives=4)
        self.icon = "🎒"


class DocHolyday(Character):
    """Nel suo turno può scartare 2 carte per fare un bang.

    He can discard 2 cards to play a bang."""

    def __init__(self):
        super().__init__("Doc Holyday", max_lives=4)
        self.icon = "✌🏻"

    def special(self, player, data):
        if super().special(player, data):
            from bang.players import PendingAction

            if (
                player.special_use_count < 1
                and player.pending_action == PendingAction.PLAY
            ):
                player.special_use_count += 1
                cards = sorted(data["cards"], reverse=True)
                for c in cards:
                    player.game.deck.scrap(player.hand.pop(c), True)
                player.notify_self()
                player.game.attack(player, data["against"])
                return True
        return False


# pylint: disable=function-redefined
def all_characters() -> List[Character]:
    cards = [
        PixiePete(),
        TequilaJoe(),
        GregDigger(),
        HerbHunter(),
        ElenaFuente(),
        BillNoface(),
        MollyStark(),
        ApacheKid(),
        SeanMallory(),
        BelleStar(),
        VeraCuster(),
        ChuckWengam(),
        PatBrennan(),
        JoseDelgado(),
        DocHolyday(),
    ]
    for card in cards:
        card.expansion_icon = "🐄️"  # pylint: disable=attribute-defined-outside-init
        card.expansion = "dodge_city"  # pylint: disable=attribute-defined-outside-init
    return cards


# Apache Kid: il suo effetto non conta nei duelli
# belle star: vale solo per le carte blu e verdi
# chuck wengam: può usarlo più volte in un turno, ma non può suicidarsi
# doc holiday: il suo effetto non conta nel limite di un bang per turno,
#             se deve sparare a Apache Kid una delle due carte scartate non deve essere di quadri
# molly stark: le carte scartate che valgono sono solo quelle scartate volontariamente,
#             carte scartate per colpa di can can, cat balou, rissa, panico non valgono,
#             invece carte scartata per indiani, birra(in caso di morte), o un mancato valgono,
#             in un duello pesca solo quando il duello è finito (una carta x ogni bang scartato)
# pat brennan: quando pesca con il suo effetto, pesca solo la carta del giocatore non anche dal mazzo
# vera custer: la scelta può essere fatta solo appena prima di pescare,
#             quando inizia la partita serve farle scegliere, poi può rimanere quello finchè non decide di cambiarlo
#             eventualmente fare una schermata dove vede tutti i personaggi
