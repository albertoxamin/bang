from abc import ABC, abstractmethod 

class Role(ABC):
    def __init__(self, name: str, goal: str, health_mod: int = 0):
        super().__init__()
        self.name = name
        self.goal = goal
        self.health_mod = health_mod
    
    @abstractmethod
    def on_player_death(self, alive_players: list):
        pass

class Sheriff(Role):
    def __init__(self):
        super().__init__("Sceriffo", "Elimina tutti i Fuorilegge e il Rinnegato!", health_mod=+1)
        self.max_players = 1

    def on_player_death(self, alive_players: list):
        if not any([isinstance(p.role) == Outlaw or isinstance(p.role) == Renegade for p in alive_players]):
            print("The Sheriff won!")
            pass


class Vice(Role):
    def __init__(self):
        super().__init__("Vice", "Proteggi lo Sceriffo! Elimina tutti i Fuorilegge e il Rinnegato!")
        self.max_players = 2
    
    def on_player_death(self, alive_players: list):
        if not any([isinstance(p.role) == Outlaw or isinstance(p.role) == Renegade for p in alive_players]):
            print("The Vice won!")
            pass

class Outlaw(Role):
    def __init__(self):
        super().__init__("Fuorilegge", "Elimina lo Sceriffo!")
        self.max_players = 3

    def on_player_death(self, alive_players: list):
        if not any([isinstance(p.role) == Sheriff for p in alive_players]):
            print("The Outlaw won!")
            pass

class Renegade(Role):
    def __init__(self):
        super().__init__("Rinnegato", "Rimani l'ultimo personaggio in gioco!")
        self.max_players = 1

    def on_player_death(self, alive_players: list):
        if len(alive_players) == 1 and isinstance(alive_players[0]) == Renegade:
            print("The Renegade won!")
            pass
