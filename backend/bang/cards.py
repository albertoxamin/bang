from typing import List, Set, Dict, Tuple, Optional
from abc import ABC, abstractmethod
from enum import IntEnum
import bang.roles as r

class Suit(IntEnum):
    DIAMONDS = 0  # ♦
    CLUBS = 1  # ♣
    HEARTS = 2  # ♥
    SPADES = 3  # ♠


class Card(ABC):
    sym = {
        'A': 1,
        'J': 11,
        'Q': 12,
        'K': 13
    }

    def __init__(self, suit: Suit, name: str, number, is_equipment: bool = False, is_weapon: bool = False, vis_mod: int = 0, sight_mod: int = 0, range: int = 99, desc: str = ''):
        super().__init__()
        self.name = name
        self.suit = suit
        if type(number) == int:
            self.number = number
        else:
            self.number = self.sym[number]
        self.is_equipment = is_equipment
        self.is_weapon = is_weapon
        self.vis_mod = vis_mod
        self.sight_mod = sight_mod
        self.range = range
        if self.range != 0 and self.range != 99:
            self.alt_text = f'{self.range} 🔍'
        self.desc = desc
        self.need_target = False
        self.can_target_self = False
        self.need_with = False

    def __str__(self):
        char = ['♦️', '♣️', '♥️', '♠️'][int(self.suit)]
        return f'{self.name} {char}{self.number}'
        return super().__str__()

    def play_card(self, player, against=None, _with=None):#self --> carta
        if self.is_equipment:
            if self.is_weapon:
                has_weapon = False
                for i in range(len(player.equipment)):
                    if player.equipment[i].is_weapon:
                        player.game.deck.scrap(player.equipment[i])
                        player.equipment[i] = self
                        has_weapon = True
                        break
                if not has_weapon:
                    player.equipment.append(self)
            elif self.name in [c.name for c in player.equipment if not isinstance(c, Dinamite)]:
                for i in range(len(player.equipment)):
                    print('tipo',type(self))
                    if type(player.equipment[i]) == type(self):
                        player.game.deck.scrap(player.equipment[i])
                        player.equipment[i] = self
                        break
            else:
                player.equipment.append(self)
        contro = f' contro {against}' if against else ''
        player.sio.emit('chat_message', room=player.game.name,
                        data=f'{player.name} ha giocato {self.name}{contro}.')
        return True

    def use_card(self, player):
        pass


class Barile(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Barile', number, is_equipment=True)
        self.icon = '🛢'
        self.desc = "Quando sei bersagliato da un Bang puoi estrarre la prima carta dalla cima del mazzo, se la carta estratta è del seme Cuori allora vale come un Mancato"


class Dinamite(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Dinamite', number, is_equipment=True)
        self.icon = '🧨'
        self.desc = "Giocando la Dinamite, posizionala davanti a te, resterà innocua per un intero giro. All'inizio del prossimo turno prima di pescare e prima di una eventuale estrazione (es. Prigione), estrai una carta dalla cima del mazzo. Se esce una carta tra il 2  il 9 di picche (compresi) allora la dinamite esplode: perdi 3 vite e scarta la carta, altrimenti passa la dinamite al giocatore successivo, il quale estrarà a sua volta dopo che tu avrai passato il tuo turno"


class Mirino(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Mirino', number, is_equipment=True, sight_mod=1)
        self.icon = '🔎'
        self.desc = "Tu vedi gli altri giocatori a distanza -1"


class Mustang(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Mustang', number, is_equipment=True, vis_mod=1)
        self.icon = '🐎'
        self.desc = "Gli altri giocatori ti vedono a distanza +1"


class Prigione(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Prigione', number, is_equipment=True)
        self.icon = '⛓'
        self.desc = "Equipaggia questa carta a un altro giocatore, tranne lo Sceriffo. Il giocatore scelto all'inizio del suo turno, prima di pescare dovrà estrarre: se esce Cuori scarta questa carta e gioca normalmente il turno, altrimenti scarta questa carta e salta il turno"
        self.need_target = True

    def play_card(self, player, against, _with=None):
        if against != None and not isinstance(player.game.get_player_named(against).role, r.Sheriff):
            player.sio.emit('chat_message', room=player.game.name,
                          data=f'{player.name} ha giocato {self.name} contro {against}.')
            player.game.get_player_named(against).equipment.append(self)
            player.game.get_player_named(against).notify_self()
        return False

class Remington(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Remington', number,
                         is_equipment=True, is_weapon=True, range=3)
        self.icon = '🔫'
        self.desc = "Puoi sparare a un giocatore che sia distante 3 o meno"


class RevCarabine(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Rev. Carabine', number,
                         is_equipment=True, is_weapon=True, range=4)
        self.icon = '🔫'
        self.desc = "Puoi sparare a un giocatore che sia distante 4 o meno"


class Schofield(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Schofield', number,
                         is_equipment=True, is_weapon=True, range=2)
        self.icon = '🔫'
        self.desc = "Puoi sparare a un giocatore che sia distante 2 o meno"


class Volcanic(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Volcanic', number,
                         is_equipment=True, is_weapon=True, range=1)
        self.icon = '🔫'
        self.desc = "Puoi sparare a un giocatore che sia distante 1 o meno, tuttavia puoi giocare quanti bang vuoi"


class Winchester(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Winchester', number,
                         is_equipment=True, is_weapon=True, range=5)
        self.icon = '🔫'
        self.desc = "Puoi sparare a un giocatore che sia distante 5 o meno"


class Bang(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Bang!', number)
        self.icon = '💥'
        self.desc = "Spara a un giocatore a distanza raggiungibile. Se non hai armi la distanza di default è 1"
        self.need_target = True

    def play_card(self, player, against, _with=None):
        if player.has_played_bang and not any([isinstance(c, Volcanic) for c in player.equipment]) and against != None:
            return False
        elif against != None:
            import bang.characters as chars
            super().play_card(player, against=against)
            player.has_played_bang = not isinstance(
                player.character, chars.WillyTheKid)
            player.game.attack(player, against)
            return True
        return False


class Birra(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Birra', number)
        self.icon = '🍺'
        self.desc = "Gioca questa carta per recuperare un punto vita. Non puoi andare oltre al limite massimo del tuo personaggio. Se stai per perdere l'ultimo punto vita puoi giocare questa carta anche nel turno dell'avversario. La birra non ha più effetto se ci sono solo due giocatori"

    def play_card(self, player, against, _with=None):
        if len(player.game.players) != 2 and player.lives != player.max_lives:
            super().play_card(player, against=against)
            player.lives = min(player.lives+1, player.max_lives)
            return True
        elif len(player.game.players) == 2:
            player.sio.emit('chat_message', room=player.game.name,
                            data=f'{player.name} ha rovesciato una {self.name}.')
            return True
        return False


class CatBalou(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Cat Balou', number)
        self.icon = '💃'
        self.desc = "Fai scartare una carta a un qualsiasi giocatore, scegli a caso dalla mano, oppure fra quelle che ha in gioco"
        self.need_target = True

    def play_card(self, player, against, _with=None):
        if against != None and (len(player.game.get_player_named(against).hand) + len(player.game.get_player_named(against).equipment)) > 0:
            super().play_card(player, against=against)
            from bang.players import PendingAction
            player.pending_action = PendingAction.CHOOSE
            player.choose_action = 'discard'
            player.target_p = against
            print('choose now')
            return True
        return False


class Diligenza(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Diligenza', number)
        self.icon = '🚡'
        self.desc = "Pesca 2 carte dalla cima del mazzo"

    def play_card(self, player, against, _with=None):
        super().play_card(player, against=against)
        player.sio.emit('chat_message', room=player.game.name,
                        data=f'{player.name} ha giocato {self.name} e ha pescato 2 carte.')
        for i in range(2):
            player.hand.append(player.game.deck.draw())
        return True


class Duello(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Duello', number)
        self.need_target = True
        self.icon = '⚔️'
        self.desc = "Gioca questa carta contro un qualsiasi giocatore. A turno, cominciando dal tuo avversario, potete scartare una carta Bang!, il primo giocatore che non lo fa perde 1 vita"

    def play_card(self, player, against, _with=None):
        if against != None:
            super().play_card(player, against=against)
            player.game.duel(player, against)
            return True
        return False


class Emporio(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Emporio', number)
        self.icon = '🏪'
        self.desc = "Scopri dal mazzo tante carte quanto il numero di giocatori, a turno, partendo da te, scegliete una carta e aggiungetela alla vostra mano"

    def play_card(self, player, against, _with=None):
        super().play_card(player, against=against)
        player.game.emporio()
        return True


class Gatling(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Gatling', number)
        self.icon = '🛰'
        self.desc = "Spara a tutti gli altri giocatori"

    def play_card(self, player, against, _with=None):
        super().play_card(player, against=against)
        player.game.attack_others(player)
        return True


class Indiani(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Indiani!', number)
        self.icon = '🏹'
        self.desc = "Tutti gli altri giocatori devono scartare un Bang! o perdere una vita"

    def play_card(self, player, against, _with=None):
        super().play_card(player, against=against)
        player.game.indian_others(player)
        return True


class Mancato(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Mancato!', number)
        self.icon = '😅'
        self.desc = "Usa questa carta per annullare un bang"

    def play_card(self, player, against, _with=None):
        import bang.characters as chars
        if (not player.has_played_bang and against != None and isinstance(player.character, chars.CalamityJanet)):
            player.sio.emit('chat_message', room=player.game.name,
                            data=f'{player.name} ha giocato {self.name} come un BANG! contro {against}.')
            player.has_played_bang = True
            player.game.attack(player, against)
            return True
        return False


class Panico(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Panico!', number, range=1)
        self.icon = '😱'
        self.need_target = True
        self.desc = "Pesca una carta da un giocatore a distanza 1, scegli a caso dalla mano, oppure fra quelle che ha in gioco"

    def play_card(self, player, against, _with=None):
        if against != None and (len(player.game.get_player_named(against).hand) + len(player.game.get_player_named(against).equipment)) > 0:
            super().play_card(player, against=against)
            from bang.players import PendingAction
            player.pending_action = PendingAction.CHOOSE
            player.choose_action = 'steal'
            player.target_p = against
            print('choose now')
            return True
        return False


class Saloon(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Saloon', number)
        self.desc = "Tutti i giocatori recuperano un punto vita compreso chi gioca la carta"
        self.icon = '🍻'

    def play_card(self, player, against, _with=None):
        player.sio.emit('chat_message', room=player.game.name,
                        data=f'{player.name} ha giocato {self.name} e ha curato 1 punto vita a tutti.')
        for p in player.game.players:
            p.lives = min(p.lives+1, p.max_lives)
            p.notify_self()
        return True


class WellsFargo(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'WellsFargo', number)
        self.desc = "Pesca 3 carte dalla cima del mazzo"
        self.icon = '💸'

    def play_card(self, player, against, _with=None):
        player.sio.emit('chat_message', room=player.game.name,
                        data=f'{player.name} ha giocato {self.name} e ha pescato 3 carte.')
        for i in range(3):
            player.hand.append(player.game.deck.draw())
        return True


def get_starting_deck(expansions:List[str]) -> List[Card]:
    from bang.expansions import DodgeCity
    base_cards = [
        Barile(Suit.SPADES, 'Q'),
        Barile(Suit.SPADES, 'K'),
        Dinamite(Suit.HEARTS, 2),
        Mirino(Suit.SPADES, 'A'),
        Mustang(Suit.HEARTS, 8),
        Mustang(Suit.HEARTS, 9),
        Prigione(Suit.SPADES, 'J'),
        Prigione(Suit.HEARTS, 4),
        Prigione(Suit.SPADES, 10),
        Remington(Suit.CLUBS, 'K'),
        RevCarabine(Suit.CLUBS, 'A'),
        Schofield(Suit.CLUBS, 'J'),
        Schofield(Suit.CLUBS, 'Q'),
        Schofield(Suit.SPADES, 'K'),
        Volcanic(Suit.SPADES, 10),
        Volcanic(Suit.CLUBS, 10),
        Winchester(Suit.SPADES, 8),
        Bang(Suit.SPADES, 'A'),
        Bang(Suit.DIAMONDS, 2),
        Bang(Suit.DIAMONDS, 3),
        Bang(Suit.DIAMONDS, 4),
        Bang(Suit.DIAMONDS, 5),
        Bang(Suit.DIAMONDS, 6),
        Bang(Suit.DIAMONDS, 7),
        Bang(Suit.DIAMONDS, 8),
        Bang(Suit.DIAMONDS, 9),
        Bang(Suit.DIAMONDS, 10),
        Bang(Suit.DIAMONDS, 'J'),
        Bang(Suit.DIAMONDS, 'Q'),
        Bang(Suit.DIAMONDS, 'K'),
        Bang(Suit.DIAMONDS, 'A'),
        Bang(Suit.CLUBS, 2),
        Bang(Suit.CLUBS, 3),
        Bang(Suit.CLUBS, 4),
        Bang(Suit.CLUBS, 5),
        Bang(Suit.CLUBS, 6),
        Bang(Suit.CLUBS, 7),
        Bang(Suit.CLUBS, 8),
        Bang(Suit.CLUBS, 9),
        Bang(Suit.HEARTS, 'Q'),
        Bang(Suit.HEARTS, 'K'),
        Bang(Suit.HEARTS, 'A'),
        Birra(Suit.HEARTS, 6),
        Birra(Suit.HEARTS, 7),
        Birra(Suit.HEARTS, 8),
        Birra(Suit.HEARTS, 9),
        Birra(Suit.HEARTS, 10),
        Birra(Suit.HEARTS, 'J'),
        CatBalou(Suit.HEARTS, 'K'),
        CatBalou(Suit.DIAMONDS, 9),
        CatBalou(Suit.DIAMONDS, 10),
        CatBalou(Suit.DIAMONDS, 'J'),
        Diligenza(Suit.SPADES, 9),
        Diligenza(Suit.SPADES, 9),
        Duello(Suit.DIAMONDS, 'Q'),
        Duello(Suit.SPADES, 'J'),
        Duello(Suit.CLUBS, 8),
        Emporio(Suit.CLUBS, 9),
        Emporio(Suit.SPADES, 'Q'),
        Gatling(Suit.HEARTS, 10),
        Indiani(Suit.DIAMONDS, 'K'),
        Indiani(Suit.DIAMONDS, 'A'),
        Mancato(Suit.CLUBS, 10),
        Mancato(Suit.CLUBS, 'J'),
        Mancato(Suit.CLUBS, 'Q'),
        Mancato(Suit.CLUBS, 'K'),
        Mancato(Suit.CLUBS, 'A'),
        Mancato(Suit.SPADES, 2),
        Mancato(Suit.SPADES, 3),
        Mancato(Suit.SPADES, 4),
        Mancato(Suit.SPADES, 5),
        Mancato(Suit.SPADES, 6),
        Mancato(Suit.SPADES, 7),
        Mancato(Suit.SPADES, 8),
        Panico(Suit.HEARTS, 'J'),
        Panico(Suit.HEARTS, 'Q'),
        Panico(Suit.HEARTS, 'A'),
        Panico(Suit.DIAMONDS, 8),
        Saloon(Suit.HEARTS, 5),
        WellsFargo(Suit.HEARTS, 3),
    ]
    if 'dodge_city' in expansions:
        base_cards.extend(DodgeCity.get_cards())
    return base_cards

