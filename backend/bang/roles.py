from abc import ABC, abstractmethod 

class Role(ABC):
    def __init__(self, name: str, goal: str, health_mod: int = 0):
        super().__init__()
        self.name = name
        self.goal = goal
        self.health_mod = health_mod

    @abstractmethod
    def on_player_death(self, alive_players: list, initial_players: int, dead_role=None, attacker_role=None):
        pass

class Sheriff(Role):
    def __init__(self):
        super().__init__("Sceriffo", "Elimina tutti i Fuorilegge e il Rinnegato!", health_mod=+1)
        self.goal_eng = "Kill the Outlaws and the Renegade!"
        self.max_players = 1
        self.icon = '⭐️'

    def on_player_death(self, alive_players: list, initial_players: int, dead_role=None, attacker_role=None):
        if initial_players == 3 and len(alive_players) == 1:
            return True
        elif initial_players != 3 and not any((isinstance(p.role, Outlaw) or isinstance(p.role, Renegade) for p in alive_players)):
            print("The Sheriff won!")
            return True
        return False


class Vice(Role):
    def __init__(self, alternative_goal=None, alternative_goal_eng=None):
        super().__init__("Vice", "Proteggi lo Sceriffo! Elimina tutti i Fuorilegge e il Rinnegato!")
        self.goal_eng = "Protect the Sheriff! Kill the Outlaws and the Renegade!"
        if alternative_goal:
            self.goal = alternative_goal
            self.goal_eng = alternative_goal_eng
        self.max_players = 2
        self.icon = '🎖'
    
    def on_player_death(self, alive_players: list, initial_players: int, dead_role=None, attacker_role=None):
        if initial_players == 3 and len(alive_players) == 1:
            return True
        elif initial_players == 3 and attacker_role is not None:
            return isinstance(dead_role, Renegade) and isinstance(attacker_role, Vice)
        elif initial_players != 3 and not any((isinstance(p.role, Outlaw) or isinstance(p.role, Renegade) for p in alive_players)):
            print("The Vice won!")
            return True
        return False

class Outlaw(Role):
    def __init__(self, alternative_goal=None, alternative_goal_eng=None):
        super().__init__("Fuorilegge", "Elimina lo Sceriffo!")
        self.goal_eng = "Kill the Sheriff!"
        if alternative_goal:
            self.goal = alternative_goal
            self.goal_eng = alternative_goal_eng
        self.max_players = 3
        self.icon = '🐺'

    def on_player_death(self, alive_players: list, initial_players: int, dead_role=None, attacker_role=None):
        if initial_players == 3 and len(alive_players) == 1:
            return True
        elif initial_players == 3 and attacker_role is not None:
            return isinstance(dead_role, Vice) and isinstance(attacker_role, Outlaw)
        elif (initial_players != 3 and (not any((isinstance(p.role, Sheriff) for p in alive_players)))
            and (any((isinstance(p.role, Outlaw) for p in alive_players))
                or any((isinstance(p.role, Renegade) for p in alive_players)) and len(alive_players) > 1)):
            print("The Outlaw won!")
            return True
        return False

class Renegade(Role):
    def __init__(self, alternative_goal=None, alternative_goal_eng=None):
        super().__init__("Rinnegato", "Rimani l'ultimo personaggio in gioco!")
        self.goal_eng = "Be the last man standing!"
        if alternative_goal:
            self.goal = alternative_goal
            self.goal_eng = alternative_goal_eng
        self.max_players = 1
        self.icon = '🦅'

    def on_player_death(self, alive_players: list, initial_players: int, dead_role=None, attacker_role=None):
        if initial_players == 3 and len(alive_players) == 1:
            return True
        elif initial_players == 3 and attacker_role is not None:
            return isinstance(dead_role, Outlaw) and isinstance(attacker_role, Renegade)
        elif initial_players != 3 and len(alive_players) == 1 and isinstance(alive_players[0].role, Renegade):
            print("The Renegade won!")
            return True
        return False
