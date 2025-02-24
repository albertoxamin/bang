import random
from globals import G

from bang.expansions.fistful_of_cards.card_events import CardEvent


class Benedizione(CardEvent):
    """Tutte le carte sono considerate di cuori ♥️"""

    def __init__(self):
        super().__init__("Benedizione", "🙏")
        # self.desc_eng = "All cards are of hearts ♥️"


class Maledizione(CardEvent):
    """Tutte le carte sono considerate di picche ♠"""

    def __init__(self):
        super().__init__("Maledizione", "🤬")
        # self.desc_eng = "All cards are of spades ♠"


class Sbornia(CardEvent):
    """I personaggi perdono le loro abilità speciali"""

    def __init__(self):
        super().__init__("Sbornia", "🥴")
        # self.desc_eng = "The characters lose their special abilities"


class Sete(CardEvent):
    """I giocatori pescano 1 carta in meno nella loro fase 1"""

    def __init__(self):
        super().__init__("Sete", "🥵")
        # self.desc_eng = "Players only draw 1 card at the start of their turn"


class IlTreno(CardEvent):
    """I giocatori pescano 1 carta extra nella loro fase 1"""

    def __init__(self):
        super().__init__("Il Treno", "🚂")
        # self.desc_eng = "Players draw 1 extra card"


class IlReverendo(CardEvent):
    """Non si possono giocare le carte Birra"""

    def __init__(self):
        super().__init__("Il Reverendo", "⛪️")
        # self.desc_eng = "Beers can't be played"


class IlDottore(CardEvent):
    """Il/i giocatore/i con meno vite ne recupera/no una"""

    def __init__(self):
        super().__init__("Il Dottore", "👨‍⚕️")
        # self.desc_eng = "The player with the least amount of HP gets healed 1"

    def on_flipped(self, game):
        super().on_flipped(game)
        most_hurt = [
            p.lives for p in game.players if p.lives > 0 and p.max_lives > p.lives
        ]
        if len(most_hurt) > 0:
            hurt_players = [p for p in game.players if p.lives == min(most_hurt)]
            for p in hurt_players:
                if p.lives != p.max_lives:
                    p.lives += 1
                    G.sio.emit(
                        "chat_message",
                        room=game.name,
                        data=f"_doctor_heal|{p.name}",
                    )
                    p.notify_self()
        return


class Sermone(CardEvent):
    """I giocatori non possono giocare Bang! durante il loro turno"""

    def __init__(self):
        super().__init__("Sermone", "✝️")
        # self.desc_eng = "Players can't play Bang! during their turn"


class Sparatoria(CardEvent):
    """Il limite di Bang! per turno è 2 invece che 1"""

    def __init__(self):
        super().__init__("Sparatoria", "🔫🔫")
        # self.desc_eng = "The turn Bang! limit is 2"


class CorsaAllOro(CardEvent):
    """Si gioca per un intero giro in senso antiorario, tuttavia gli effetti delle carte rimangono invariati"""

    def __init__(self):
        super().__init__("Corsa All Oro", "🌟")
        # self.desc_eng = "Turns are played counter clockwise"


class IDalton(CardEvent):
    """Chi ha carte blu in gioco ne scarta 1 a sua scelta"""

    def __init__(self):
        super().__init__("I Dalton", "🙇‍♂️")
        # self.desc_eng = "Players that have blue cards equipped, discard 1 of those card of their choice"

    def on_flipped(self, game):
        super().on_flipped(game)
        game.waiting_for = 0
        game.ready_count = 0
        game.dalton_on = True
        
        # Check each player in order
        for p in game.players:
            if p.get_dalton():  # Only increment waiting_for if they actually have blue cards
                game.waiting_for += 1
                p.notify_self()
        
        # If no one has blue cards, end the event immediately
        if game.waiting_for == 0:
            game.dalton_on = False
            game.notify_all()
            return
            
        # Otherwise wait for players to make their choice
        return


class Manette(CardEvent):
    """Dopo aver pescato in fase 1, il giocatore di turno dichiara un seme: potrà usare solamente carte di quel seme nel suo turno"""

    def __init__(self):
        super().__init__("Manette", "🔗")
        # self.desc_eng = "After drawing in phase 1, the player declares a suit. He will be able to use only cards of that suit for that turn"


class NuovaIdentita(CardEvent):
    """All'inizio del proprio turno, ogni giocatore potrà decidere se sostituire il suo personaggio attuale con quello era stato proposto ad inizio partita, se lo fa riparte con 2 punti vita"""

    def __init__(self):
        super().__init__("Nuova Identita", "🕶")
        # self.desc_eng = "At the beginning of their turn, each player can choose to change its character with the other shown at the game start. If he does so he restarts from 2 HP."


class CittaFantasma(CardEvent):
    """Tutti i giocatori morti tornano in vita al proprio turno, non possono morire e pescano 3 carte invece che 2. Quando terminano il turno tornano morti."""

    def __init__(self):
        super().__init__("Città Fantasma", "👻")
        # self.desc_eng = "All dead players come back to life in their turn, they can't die and draw 3 cards instead of 2. When they end their turn the die."


class MezzogiornoDiFuoco(CardEvent):
    """Ogni giocatore perde 1 punto vita all'inizio del turno"""

    def __init__(self):
        super().__init__("Mezzogiorno di Fuoco", "🔥")
        # self.desc_eng = "Every player loses 1 HP when their turn starts"


def get_endgame_card():
    end_game = MezzogiornoDiFuoco()
    end_game.expansion = "high-noon"  # pylint: disable=attribute-defined-outside-init
    return end_game


def get_all_events(rng=random):
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
        Manette(),
        NuovaIdentita(),
    ]
    rng.shuffle(cards)
    for c in cards:
        c.expansion = "high-noon"  # pylint: disable=attribute-defined-outside-init
    return cards
