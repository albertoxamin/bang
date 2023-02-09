from typing import List
from bang.characters import Character
import bang.cards as cs

class BlackFlower(Character):
    def __init__(self):
        super().__init__("Black Flower", max_lives=4)
        # Una volta nel tuo turno, puoi usare una carta di fiori per sparare un BANG! extra.
        self.icon = '🥀'

    def special(self, player, data): #fiori = suit.Clubs
        if player.special_use_count > 0 or not any((c.suit == cs.Suit.CLUBS for c in player.hand)):
            return False
        if any((player.get_sight() >= p['dist'] for p in player.game.get_visible_players(player))) and super().special(player, data):
            from bang.players import PendingAction
            player.available_cards = [c for c in player.hand if c.suit == cs.Suit.CLUBS]
            player.special_use_count += 1
            player.pending_action = PendingAction.CHOOSE
            player.choose_text = 'choose_play_as_bang'
            player.notify_self()

class ColoradoBill(Character):
    def __init__(self):
        super().__init__("Colorado Bill", max_lives=4)
        # Ogni volta che giochi una carta BANG!, "estrai!": se è Picche, il colpo non può essere evitato.
        self.icon = '♠️'

class DerSpotBurstRinger(Character):
    def __init__(self):
        super().__init__("Der Spot Burst Ringer", max_lives=4)
        # Una volta nel tuo turno, puoi usare una carta BANG! come Gatling.
        self.icon = '🫧'

    def special(self, player, data):
        if player.special_use_count == 0 and \
              any((c.name == 'Bang!' for c in player.hand)) and super().special(player, data):
            player.special_use_count += 1
            #get cards from hand of type Bang and sort them by suit
            cards = sorted([c for c in player.hand if c.name == 'Bang!'], key=lambda c: c.suit)
            player.hand.remove(cards[0])
            player.game.deck.scrap(cards[0], True, player=player)
            player.notify_self()
            player.game.attack_others(player, cs.Gatling(0,0).name)

class EvelynShebang(Character):
    def __init__(self):
        super().__init__("Evelyn Shebang", max_lives=4)
        # Puoi rinunciare a pescare carte nella tua fase di pesca. Per ogni carta non pescata, spari un BANG! a distanza raggiungibile, a un diverso bersaglio.
        self.icon = '📵'

class HenryBlock(Character):
    def __init__(self):
        super().__init__("Henry Block", max_lives=4)
        # Chiunque peschi o scarti una tua cartain gioco o in mano) è bersaglio di un BANG!.
        self.icon = '🚯'

class LemonadeJim(Character):
    def __init__(self):
        super().__init__("Lemonade Jim", max_lives=4)
        # Ogni volta che un altro giocatore gioca una Birra, puoi scartare una carta dalla mano per riguadagnare anche tu 1 punto vita.
        self.icon = '🍋'

class MickDefender(Character):
    def __init__(self):
        super().__init__("Mick Defender", max_lives=4)
        # Se sei bersaglio di una carta marrone (non BANG!), puoi usare una carta Mancato! evitarne 1 gli effetti. 
        self.icon = '⛔'

class TucoFranziskaner(Character):
    def __init__(self):
        super().__init__("Tuco Franziskaner", max_lives=4)
        # Durante la tua fase di pesca, se non hai carte blu in gioco, pesca 2 carte extra.
        self.icon = '🥬'

def all_characters() -> List[Character]:
    cards = [
        BlackFlower(),
        ColoradoBill(),
        DerSpotBurstRinger(),
        # EvelynShebang(),
        # HenryBlock(),
        # LemonadeJim(),
        MickDefender(),
        TucoFranziskaner(),
    ]
    for c in cards:
        c.expansion_icon = '👻️'
    return cards
