from abc import ABC, abstractmethod

class CardEvent(ABC):
    def __init__(self, name, icon):
        self.name = name
        self.icon = icon

class Agguato(CardEvent):
    def __init__(self):
        super().__init__('Agguato', '🛁')
        self.desc = ''
        self.desc_eng = ''

class Cecchino(CardEvent):
    def __init__(self):
        super().__init__('Cecchino', '👁')
        self.desc = ''
        self.desc_eng = ''

class DeadMan(CardEvent):
    def __init__(self):
        super().__init__('Dead Man', '⚰️')
        self.desc = ''
        self.desc_eng = ''

class FratelliDiSangue(CardEvent):
    def __init__(self):
        super().__init__('Fratelli Di Sangue', '🩸')
        self.desc = ''
        self.desc_eng = ''

class IlGiudice(CardEvent):
    def __init__(self):
        super().__init__('Il Giudice', '👨‍⚖️')
        self.desc = ''
        self.desc_eng = ''

class Lazo(CardEvent):
    def __init__(self):
        super().__init__('Lazo', '📿')
        self.desc = ''
        self.desc_eng = ''

class LeggeDelWest(CardEvent):
    def __init__(self):
        super().__init__('Legge Del West', '⚖️')
        self.desc = ''
        self.desc_eng = ''

class LiquoreForte(CardEvent):
    def __init__(self):
        super().__init__('Liquore Forte', '🥃')
        self.desc = ''
        self.desc_eng = ''

class MinieraAbbandonata(CardEvent):
    def __init__(self):
        super().__init__('Miniera Abbandonata', '⛏')
        self.desc = ''
        self.desc_eng = ''

class PerUnPugnoDiCarte(CardEvent):
    def __init__(self):
        super().__init__('Per Un Pugno Di Carte', '🎴')
        self.desc = ''
        self.desc_eng = ''

class Peyote(CardEvent):
    def __init__(self):
        super().__init__('Peyote', '🌵')
        self.desc = ''
        self.desc_eng = ''

class Ranch(CardEvent):
    def __init__(self):
        super().__init__('Ranch', '🐮')
        self.desc = ''
        self.desc_eng = ''

class Rimbalzo(CardEvent):
    def __init__(self):
        super().__init__('Rimbalzo', '⏮')
        self.desc = ''
        self.desc_eng = ''

class RouletteRussa(CardEvent):
    def __init__(self):
        super().__init__('Roulette Russa', '🇷🇺')
        self.desc = ''
        self.desc_eng = ''

class Vendetta(CardEvent):
    def __init__(self):
        super().__init__('Vendetta', '😤')
        self.desc = ''
        self.desc_eng = ''

def get_all_events():
    return [
        Agguato(),
        Cecchino(),
        DeadMan(),
        FratelliDiSangue(),
        IlGiudice(),
        Lazo(),
        LeggeDelWest(),
        LiquoreForte(),
        MinieraAbbandonata(),
        PerUnPugnoDiCarte(),
        Peyote(),
        Ranch(),
        Rimbalzo(),
        RouletteRussa(),
        Vendetta(),
    ]