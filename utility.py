import os
import sys
import pygame
import threading
import copy


class MyThread(threading.Thread):
    def __init__(self, func, name, *args, **kwargs):
        super().__init__(name=name)
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.killed = False  
        self.flag = False 

    def run(self):
        self.func(*self.args, **self.kwargs)


class Player:
    def __init__(self, ip, host=False):
        self.ip = ip
        self.host = host

        self.cards = {'wheat': [Card('cards/Wheat_Field.png', 'Wheat Field', 'wheat', (1,), ['Get 1 coin', '(On everyone`s turn)'], 1)], 'cow': [], 'gear': [],  # add wheat field
                      'bread': [Card('cards/Bakery.png', 'Bakery', 'bread', (2, 3), ['Get 1 coin', '(On your turn only)'], 1)], 'factory': [], 'fruit': [],  # add bakery
                      'cup': [],
                      'major': []
                      }
        self.landmarks = {
            'station': Landmark('landmarks/Station.png', 'landmarks/Station_WB.png', 'Station', ['You may roll 2 dice'], 4),
            'mall': Landmark('landmarks/Shopping_Mall.png', 'landmarks/Shopping_Mall_WB.png', 'Shopping Mall',
                             ['Earn +1 coin from your own cup', 'and bread establishments'], 10),
            'park': Landmark('landmarks/Amusement_Park.png', 'landmarks/Amusement_Park_WB.png', 'Amusement Park',
                             ['If you roll matching dice, take', 'another turn after this one'], 16),
            'tower': Landmark('landmarks/Radio_Tower.png', 'landmarks/Radio_Tower_WB.png', 'Radio Tower',
                              ['Once every turn, you can', 'choose to re-roll your dice'], 22),
        }
        self.money = 3
        self.buy_flag = True
        self.dice_rolled = False

    def is_host(self):
        return self.host

    def get_ip(self):
        return self.ip

    def get_cards(self):
        return self.cards

    def get_landmarks(self):
        return self.landmarks

    def get_money(self):
        return self.money

    def __str__(self):
        return f"Player('{self.ip}', {self.host})"


class Card:
    def __init__(self, image, name, type_, die_roll, description, cost):
        self.image = image
        self.name = name
        self.type = type_
        self.die_roll = die_roll
        self.description = description
        self.cost = cost

    def get_image(self):
        return self.image

    def get_name(self):
        return self.name

    def __rmul__(self, num):
        return [copy.copy(self) for _ in range(num)]

    def __str__(self):
        #return f'Card("{self.image}", "{self.name}", "{self.type}", "{self.die_roll}", "{self.description}", "{self.cost}")'
        return self.name.lower().replace(' ', '_') if self.name != 'Fruit and Vegetable Market' else 'market'

    def get_production(self):
        return int(self.description[0].split()[1])

def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname).convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey)
        if colorkey == -2:
            colorkey = image.get_at((image.get_rect().width - 1, image.get_rect().height - 1))
            image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Landmark:
    def __init__(self, image, image_wb, name, description, cost, is_active=False):
        self.image_wb = image_wb
        self.image_clr = image
        if is_active:
            self.image = self.image_clr
        else:
            self.image = self.image_wb
        self.name = name
        self.description = description
        self.cost = cost
        self.is_active = is_active

    def build(self):
        self.image = self.image_clr
        self.is_active = True

    def get_image(self):
        return self.image

    def get_name(self):
        return self.name
