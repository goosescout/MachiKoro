import os
import pygame


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
