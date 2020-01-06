from utility import Card


ALL_CARDS = {
    'wheat_field': Card('cards/Wheat_Field.png', 'Wheat Field', 'wheat', (1,), "Get 1 coin (On everyone's turn)", 1),
    'apple_orchard': Card('cards/Apple_Orchard.png', 'Apple Orchard', 'wheat', (10,), "Get 3 coins (On everyone's turn)", 3),
    'ranch': Card('cards/Ranch.png', 'Ranch', 'cow', (2,), "Get 1 coin (On everyone's turn)", 1),
    'forest': Card('cards/Forest.png', 'Forest', 'gear', (5,), "Get 3 coins (On everyone's turn)", 3),
    'mine': Card('cards/Mine.png', 'Mine', 'gear', (9,), "Get 5 coins (On everyone's turn)", 6),
    'bakery': Card('cards/Bakery.png', 'Bakery', 'bread', (2, 3), "Get 1 coin (On your turn only)", 1),
    'convenience_store': Card('cards/Convenience_Store.png', 'Convenience Store', 'bread', (4,), "Get 3 coins (On your turn only)", 2),
    'cheese_factory': Card('cards/Cheese_Factory.png', 'Cheese Factory', 'factory', (7,), "Get 3 coins for every Farm you control (On your turn only)", 5),
    'furniture_factory': Card('cards/Furniture_Factory.png', 'Furniture Factory', 'factory', (8,), "Get 3 coins for every Forest and Mine you control (On your turn only)", 3),
    'market': Card('cards/Fruit_and_Vegetable_Market.png', 'Fruit and Vegetable Market', 'fruit', (11, 12), "Get 3 coins for every Wheat Field and Apple Orchard you control (On your turn only)", 2),
    'cafe': Card('cards/Cafe.png', 'Cafe', 'cup', (3,), "Get 1 coin from player who rolled the dice", 2),
    'family_restaurant': Card('cards/Family_Restaurant.png', 'Family Restaurant', 'cup', (9, 10), "Get 2 coins from player who rolled the dice", 3),
    'stadium': Card('cards/Stadium.png', 'Stadium', 'major', (6,), "Get 2 coins from all players (On your turn only)", 6),
    'business_center': Card('cards/Business_Center.png', 'Business Center', 'major', (6,), "Trade one non-major establishment with another player (On your turn only)", 6),
    'tv_station': Card('cards/TV_Station.png', 'TV Station', 'major', (6,), "Take 5 coins grom any one player (On your turn only)", 7)
}
