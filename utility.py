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

        self.cards = {'wheat': [], 'cow': [], 'gear': [], 'boat': [],  # add wheat field
                      'bread': [], 'factory': [], 'fruit': [],  # add bakery
                      'cup': [],
                      'major': []
                      }
        self.landmarks = ['Something']
        self.money = 3

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

    def __rmul__(self, num):
        return [copy.copy(self) for _ in range(num)]


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name).replace('\\', '/')
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
