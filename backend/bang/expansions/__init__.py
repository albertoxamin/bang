# pylint: skip-file

class DodgeCity():
    def get_characters():
        from bang.expansions.dodge_city import characters
        return characters.all_characters()

    def get_cards():
        from bang.expansions.dodge_city import cards
        return cards.get_starting_deck()
    
    def get_expansion_info(self):
        return {
            "id": "dodge_city", 
            "name": "Dodge City", 
            "cards": [
                {"type": "characters", "cards": DodgeCity.get_characters()},
                {"type": "cards", "cards": DodgeCity.get_cards()}
            ]
        }
    
class HighNoon():
    def get_events():
        from bang.expansions.high_noon import card_events
        return card_events.get_all_events() + [card_events.get_endgame_card()]
    
    def get_expansion_info(self):
        return {
            "id": "high_noon", 
            "name": "High Noon", 
            "cards": [
                {"type": "events", "cards": HighNoon.get_events()}
            ]
        }
class FistfulOfCards():
    def get_events():
        from bang.expansions.fistful_of_cards import card_events
        return card_events.get_all_events() + [card_events.get_endgame_card()]
    
    def get_expansion_info(self):
        return {
            "id": "fistful_of_cards", 
            "name": "Fistful of Cards", 
            "cards": [
                {"type": "events", "cards": FistfulOfCards.get_events()}
            ]
        }
class GoldRush():
    def get_characters():
        from bang.expansions.gold_rush import characters
        return characters.all_characters()
    
    def get_shop_cards():
        from bang.expansions.gold_rush import shop_cards
        return shop_cards.get_cards()
    
    def get_expansion_info(self):
        return {
            "id": "gold_rush", 
            "name": "Gold Rush", 
            "cards": [
                {"type": "characters", "cards": GoldRush.get_characters()},
                {"type": "cards", "cards": GoldRush.get_shop_cards()}
            ]
        }

class TheValleyOfShadows():
    def get_characters():
        from bang.expansions.the_valley_of_shadows import characters
        return characters.all_characters()

    def get_cards():
        from bang.expansions.the_valley_of_shadows import cards
        return cards.get_starting_deck()

    def get_expansion_info(self):
        return {
            "id": "the_valley_of_shadows", 
            "name": "The Valley of Shadows", 
            "cards": [
                {"type": "characters", "cards": TheValleyOfShadows.get_characters()},
                {"type": "cards", "cards": TheValleyOfShadows.get_cards()}
            ]
        }

class WildWestShow():
    def get_characters():
        from bang.expansions.wild_west_show import characters
        return characters.all_characters()
    
    def get_events():
        from bang.expansions.wild_west_show import card_events
        return card_events.get_all_events() + [card_events.get_endgame_card()]
    
    def get_expansion_info(self):
        return {
            "id": "wild_west_show", 
            "name": "Wild West Show", 
            "cards": [
                {"type": "characters", "cards": WildWestShow.get_characters()},
                {"type": "events", "cards": WildWestShow.get_events()}
            ]
        }

class TrainRobbery():
    def get_stations():
        from bang.expansions.train_robbery import stations
        return stations.get_all_stations()
    
    def get_trains():
        from bang.expansions.train_robbery import trains
        return trains.get_all_cards() + trains.get_locomotives()
    
    def get_expansion_info(self):
        return {
            "id": "train_robbery", 
            "name": "Train Robbery", 
            "cards": [
                {"type": "stations", "cards": TrainRobbery.get_stations()},
                {"type": "trains", "cards": TrainRobbery.get_trains()}
            ]
        }

def get_expansion_info(expansion_id):
    expansion_map = {
        "dodge_city": DodgeCity(),
        "high_noon": HighNoon(),
        "fistful_of_cards": FistfulOfCards(),
        "gold_rush": GoldRush(),
        "the_valley_of_shadows": TheValleyOfShadows(),
        "wild_west_show": WildWestShow(),
        "train_robbery": TrainRobbery()
    }

    expansion_info = expansion_map[expansion_id].get_expansion_info()

    for section in expansion_info["cards"]:
        unique_cards = []
        seen_card = set()
        for card in section["cards"]:
            if card.name not in seen_card:
                unique_cards.append(card)
                seen_card.add(card.name)
        section["cards"] = unique_cards

    return expansion_info