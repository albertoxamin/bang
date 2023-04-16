from bang.cards import Card


class TrainCard(Card):
    def __init__(self, name: str, is_locomotive: bool = False):
        super().__init__(suit=5, number="", name=name)
        self.expansion_icon = "🚂"
        self.is_equipment = True
        self.is_locomotive = is_locomotive
        self.expansion = "train_robbery"


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


class CircusWagon(TrainCard):
    def __init__(self):
        super().__init__("Circus Wagon", is_locomotive=True)
        self.icon = "🚋🎪"

    def play_card(self, player, against=None, _with=None) -> bool:
        return True
