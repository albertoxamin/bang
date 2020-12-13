from typing import List
from bang.characters import *

class PixiePete(Character):
    def __init__(self):
        super().__init__("Pixie Pete", max_lives=3)
        self.desc = "All'inizio del turno pesca 3 carte invece che 2"
        self.desc_eng = "He draws 3 cards instead of 2"
        self.icon = '☘️'

class TequilaJoe(Character):
    def __init__(self):
        super().__init__("Tequila Joe", max_lives=4)
        self.desc = "Se gioca la carta Birra recupera 2 vite invece che una sola"
        self.desc_eng = "When he plays Beer, he regains 2 Health Points"
        self.icon = '🍻'

class GregDigger(Character):
    def __init__(self):
        super().__init__("Greg Digger", max_lives=4)
        self.desc = "Quando un giocatore muore, recupera fino a 2 vite"
        self.desc_eng = "Whenever a player dies, he regains up to 2 lives"
        self.icon = '🦴'

class HerbHunter(Character):
    def __init__(self):
        super().__init__("HerbHunter", max_lives=4)
        self.desc = "Quando un giocatore muore, pesca 2 carte"
        self.desc_eng = "Whenever a player dies, he draws 2 cards"
        self.icon = '⚰️'

class ElenaFuente(Character):
    def __init__(self):
        super().__init__("Elena Fuente", max_lives=3)
        self.desc = "Può usare una carta qualsiasi nella sua mano come mancato"
        self.desc_eng = "She can use any card of her hand as missed"
        self.icon = '🧘‍♀️'

class BillNoface(Character):
    def __init__(self):
        super().__init__("Bill Noface", max_lives=4)
        self.desc = "All'inizio del turno pesca 1 carta + 1 carta per ogni ferita che ha"
        self.desc_eng = "Draw 1 card + 1 card for each wound he has"
        self.icon = '🙈'

class MollyStark(Character):
    def __init__(self):
        super().__init__("Molly Stark", max_lives=4)
        self.desc = "Quando usa volontariamente una carta che ha in mano, fuori dal suo turno, ne ottiene un'altra dal mazzo"
        self.desc_eng = "When she uses a card from her hand outside her turn, she draws a card."
        self.icon = '🙅‍♀️'

class ApacheKid(Character):
    def __init__(self):
        super().__init__("Apache Kid", max_lives=3)
        self.desc = "Le carte di quadri ♦️ giocate contro di lui non hanno effetto (non vale durante i duelli)"
        self.desc_eng = "Cards of diamonds ♦️ played against him, do no have effect (doesn't work in duels)."
        self.icon = '♦️'

def all_characters() -> List[Character]:
    return [
        PixiePete(),
        TequilaJoe(),
        GregDigger(),
        HerbHunter(),
        ElenaFuente(),
        BillNoface(),
        MollyStark(),
        ApacheKid(),
    ]

#Apache Kid: il suo effetto non conta nei duelli
#belle star: vale solo per le carte blu e verdi
#chuck wengam: può usarlo più volte in un turno, ma non può suicidarsi
#doc holiday: il suo effetto non conta nel limite di un bang per turno,
#             se deve sparare a Apache Kid una delle due carte scartate non deve essere di quadri
#molly stark: le carte scartate che valgono sono solo quelle scartate volontariamente,
#             carte scartate per colpa di can can, cat balou, rissa, panico non valgono,
#             invece carte scartata per indiani, birra(in caso di morte), o un mancato valgono,
#             in un duello pesca solo quando il duello è finito (una carta x ogni bang scartato)
#pat brennan: quando pesca con il suo effetto, pesca solo la carta del giocatore non anche dal mazzo
#vera custer: la scelta può essere fatta solo appena prima di pescare,
#             quando inizia la partita serve farle scegliere, poi può rimanere quello finchè non decide di cambiarlo
#             eventualmente fare una schermata dove vede tutti i personaggi