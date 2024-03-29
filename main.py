import os
import socket
import sys
import threading
from collections import Counter
from random import shuffle, randint

import pygame
import json

from node import Node
from utility import MyThread, Player, load_image, Card, Landmark
from cards import ALL_CARDS


class Notification(pygame.sprite.Sprite):
    '''
    Класс, отвечающий за уведоления на экране
    '''
    def __init__(self, group, text, font='data/DisposableDroidBB.ttf', fontsize=50, color=pygame.Color('black'),
                 add_button=None):
        group.empty()
        super().__init__(group)
        self.image = pygame.transform.scale(
            load_image('button.png'), (880, 320))
        self.rect = self.image.get_rect()
        self.rect.x = 200
        self.rect.y = 200

        self.font = pygame.font.Font(font, fontsize)
        self.color = color
        shift = 280 // (len(text) + 1)
        for i, line in enumerate(text):
            line = self.font.render(line, 1, color)
            self.image.blit(line, (20, shift * (i + 1)))

        self.close_button = Button(group, 910, 450, 'close',
                                   size=(150, 50), fontsize=50)  # кнопка закрытия
        self.add_button = Button(group, 740, 450, add_button, size=(
            150, 50), fontsize=50) if add_button is not None else None  # дополнительная кнопка

    def update(self, *args, **kwargs):
        '''
        Функция обновления текста уведомления
        '''
        if 'text' in kwargs.keys():
            self.image = pygame.transform.scale(
                load_image('button.png'), (880, 320))
            shift = 280 // (len(kwargs['text']) + 1)
            for i, line in enumerate(kwargs['text']):
                line = self.font.render(line, 1, self.color)
                self.image.blit(line, (20, shift * (i + 1)))


class DieRollNotification(Notification):
    '''
    Класс уведомления, связанного с выбором сколько кубиков бросить или перебросить
    ли кубики. Не имеет кнопки закрытия и не может быть закрыт до ответа пользователя
    '''
    def __init__(self, group, text, button_1='roll 1', button_2='roll 2', **kwargs):
        group.empty()
        super().__init__(group, text, **kwargs)
        self.close_button.kill()
        if self.add_button is not None:
            self.add_button.kill()
        self.close_button = Button(group, 910, 450, button_1,
                                   size=(150, 50), fontsize=50)  # первая кнопка
        self.add_button = Button(group, 740, 450, button_2, size=(
            150, 50), fontsize=50)  # вторая кнопка


class ShopNotification(pygame.sprite.Sprite):
    '''
    Класс уведомления, связанного с покупкой карты
    '''
    def __init__(self, group, card_sprite, player, is_active):
        super().__init__(group)
        self.image = pygame.transform.scale(
            load_image('button.png'), (880, 320))
        self.card_image = pygame.transform.scale(
            load_image(card_sprite.card.get_image()), (180, 270))
        self.image.blit(self.card_image, (690, 25))
        self.player = player
        self.is_active = is_active
        self.card = card_sprite.card
        self.sprite = card_sprite
        text = [self.card.get_name()] + self.card.description

        self.font = pygame.font.Font('data/DisposableDroidBB.ttf', 45)
        self.color = pygame.Color('black')
        shift = 220 // (len(text) + 1)
        for i, line in enumerate(text):
            line = self.font.render(line, 1, self.color)
            self.image.blit(line, (20, shift * (i + 1)))

        self.close_button = Button(
            group, 225, 450, 'close', (150, 50), fontsize=50)
        self.buy_button = Button(
            group, 390, 450, 'buy', (150, 50), fontsize=50)
        self.buy_button.make_inactive()

        self.rect = self.image.get_rect()
        self.rect.x = 200
        self.rect.y = 200

    def update(self, is_active):
        if is_active and self.player.get_money() >= self.card.cost and not self.buy_button.active and self.player.buy_flag:
            self.buy_button.make_active()
        elif not is_active and self.player.get_money() < self.card.cost and self.buy_button.active and not self.player.buy_flag:
            self.buy_button.make_inactive()


class Table:
    '''
    Класс стола для отрисовки неизменяемых элементов
    '''
    def __init__(self, surface):
        self.start_x_pos = 200
        self.start_y_pos = 600
        self.shift_x = 105
        self.font = pygame.font.Font('data/DisposableDroidBB.ttf', 25)
        self.color = pygame.Color('black')
        self.surface = surface

        self.wheat = pygame.transform.scale(
            load_image('cards/Wheat.png'), (95, 95))
        self.cow = pygame.transform.scale(
            load_image('cards/Cow.png'), (95, 95))
        self.gear = pygame.transform.scale(
            load_image('cards/Gear.png'), (95, 95))
        self.bread = pygame.transform.scale(
            load_image('cards/Bread.png'), (95, 95))
        self.factory = pygame.transform.scale(
            load_image('cards/Factory.png'), (95, 95))
        self.fruit = pygame.transform.scale(
            load_image('cards/Fruit.png'), (95, 95))
        self.cup = pygame.transform.scale(
            load_image('cards/Cup.png'), (95, 95))
        self.major = pygame.transform.scale(
            load_image('cards/Major.png'), (95, 95))

        self.surface.blit(self.wheat, (self.start_x_pos +
                                       self.shift_x * 0, self.start_y_pos))
        self.surface.blit(self.cow, (self.start_x_pos +
                                     self.shift_x * 1, self.start_y_pos))
        self.surface.blit(self.gear, (self.start_x_pos +
                                      self.shift_x * 2, self.start_y_pos))
        self.surface.blit(self.bread, (self.start_x_pos +
                                       self.shift_x * 3, self.start_y_pos))
        self.surface.blit(self.factory, (self.start_x_pos +
                                         self.shift_x * 4, self.start_y_pos))
        self.surface.blit(self.fruit, (self.start_x_pos +
                                       self.shift_x * 5, self.start_y_pos))
        self.surface.blit(self.cup, (self.start_x_pos +
                                     self.shift_x * 6, self.start_y_pos))
        self.surface.blit(self.major, (self.start_x_pos +
                                       self.shift_x * 7, self.start_y_pos))

    def update(self):
        self.surface.blit(self.wheat, (self.start_x_pos +
                                       self.shift_x * 0, self.start_y_pos))
        self.surface.blit(self.cow, (self.start_x_pos +
                                     self.shift_x * 1, self.start_y_pos))
        self.surface.blit(self.gear, (self.start_x_pos +
                                      self.shift_x * 2, self.start_y_pos))
        self.surface.blit(self.bread, (self.start_x_pos +
                                       self.shift_x * 3, self.start_y_pos))
        self.surface.blit(self.factory, (self.start_x_pos +
                                         self.shift_x * 4, self.start_y_pos))
        self.surface.blit(self.fruit, (self.start_x_pos +
                                       self.shift_x * 5, self.start_y_pos))
        self.surface.blit(self.cup, (self.start_x_pos +
                                     self.shift_x * 6, self.start_y_pos))
        self.surface.blit(self.major, (self.start_x_pos +
                                       self.shift_x * 7, self.start_y_pos))


class Block(pygame.sprite.Sprite):
    '''
    Класс игрового блока Игрока.
    В каждом блоке содержится связка с картой и количество каждой у игрока
    '''
    def __init__(self, group, block, amount, x, y):
        super().__init__(group)
        self.block = block
        self.card_image = self.block.image
        self.amount = amount
        self.image = pygame.transform.scale(load_image('button.png'), (95, 35))
        self.start_x_pos = 200
        self.start_y_pos = 565
        self.shift_x = 105
        self.shift_y = -40
        self.rect = self.image.get_rect()
        self.rect.x = self.start_x_pos + self.shift_x * x
        self.rect.y = self.start_y_pos + self.shift_y * y
        self.font = pygame.font.Font('data/DisposableDroidBB.ttf', 25)
        self.color = pygame.Color('black')
        die_roll_list = list(map(str, list(self.block.die_roll)))
        text = self.font.render(
            f'{" " * (5 - len(die_roll_list))}{"-".join(die_roll_list)} {f"({amount})" if amount > 1 else ""}', 1, self.color)
        self.image.blit(text, (5, 5))


class BlockNotification(pygame.sprite.Sprite):
    '''
    Класс уведомления, связанный с отображением информации об
    уже купленных игроком картах.
    '''
    def __init__(self, group, card):
        super().__init__(group)
        self.image = pygame.transform.scale(
            load_image('button.png'), (880, 320))
        self.card_image = pygame.transform.scale(
            load_image(card.get_image()), (180, 270))
        self.image.blit(self.card_image, (690, 25))
        self.card = card

        text = [self.card.name] + self.card.description
        self.font = pygame.font.Font('data/DisposableDroidBB.ttf', 45)
        self.color = pygame.Color('black')
        shift = 220 // (len(text) + 1)
        for i, line in enumerate(text):
            line = self.font.render(line, 1, self.color)
            self.image.blit(line, (20, shift * (i + 1)))

        self.close_button = Button(
            group, 225, 450, 'close', (150, 50), fontsize=50)

        self.rect = self.image.get_rect()
        self.rect.x = 200
        self.rect.y = 200


class ShopCardSprite(pygame.sprite.Sprite):
    '''
    Класс спрайта карты в магазине.
    Каждая карта в магаззине имеет свои координаты относительно верхнего левого угла.
    Например, самая левая верхняя карта имеет координаты (0;0), а правая нижняя - (2;4)
    '''
    def __init__(self, group, card, row, col):
        super().__init__(group)
        self.card = card
        self.image = pygame.transform.scale(
            load_image(self.card.get_image()), (80, 120))
        self.rect = self.image.get_rect()
        self.row = row
        self.col = col
        self.rect.x = 400 + 110 * row
        self.rect.y = 10 + 130 * col

    def get_coords(self):
        return self.row, self.col


class LandmarkSprite(pygame.sprite.Sprite):
    '''
    Класс Достопримечательности на столе игрока
    '''
    def __init__(self, group, landmark, coord):
        super().__init__(group)
        self.card = landmark
        self.image = pygame.transform.scale(
            load_image(self.card.image), (95, 140))
        self.rect = self.image.get_rect()
        self.rect.x = 1100
        self.rect.y = 145 * coord + 20


class PlayerIcon(pygame.sprite.Sprite):
    '''
    Класс иконки, показывающей состояние игрока
    '''
    def __init__(self, group, is_active, is_myself, player, count, font='data/DisposableDroidBB.ttf'):
        self.player = player
        self.is_myself = is_myself
        super().__init__(group)

        self.image = pygame.transform.scale(load_image('button_press.png'), (
            375, 125)) if is_active else pygame.transform.scale(load_image('button.png'), (375, 125))

        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 125 * count

        self.image.blit(load_image('coin.png'), (20, 65))
        self.image.blit(load_image('landmark.png'), (160, 65))

        self.font = pygame.font.Font(font, 50)
        line = self.font.render(
            f': {self.player.get_money()}', 1, pygame.Color('black'))
        self.image.blit(line, (75, 65))
        line = self.font.render(
            f': {len(self.player.get_active_landmarks())}', 1, pygame.Color('black'))
        self.image.blit(line, (215, 65))
        line = self.font.render(self.player.get_ip(
        ) if not self.is_myself else 'me', 1, pygame.Color('black'))
        self.image.blit(line, (5, 5))

    def update(self, is_active, count=None):
        '''
        Обновляет значения на иконке
        '''
        self.image = pygame.transform.scale(load_image('button_press.png'), (
            375, 125)) if is_active else pygame.transform.scale(load_image('button.png'), (375, 125))

        if count is not None:
            self.rect.y = 125 * count

        self.image.blit(load_image('coin.png', -1), (20, 65))
        self.image.blit(load_image('landmark.png', -1), (160, 65))

        line = self.font.render(
            f': {self.player.get_money()}', 1, pygame.Color('black'))
        self.image.blit(line, (75, 65))
        line = self.font.render(
            f': {len(self.player.get_active_landmarks())}', 1, pygame.Color('black'))
        self.image.blit(line, (215, 65))
        line = self.font.render(self.player.get_ip(
        ) if not self.is_myself else 'me', 1, pygame.Color('black'))
        self.image.blit(line, (5, 5))


class Cursor(pygame.sprite.Sprite):
    '''
    Класс курсора
    '''
    def __init__(self, group):
        super().__init__(group)
        self.group = group
        self.image = load_image('cursor.png', -2)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pygame.mouse.get_pos()

    def update(self):
        self.rect.x, self.rect.y = pygame.mouse.get_pos()


class Button(pygame.sprite.Sprite):
    '''
    Класс кнопки
    '''
    def __init__(self, group, x, y, text, size=None, font='data/DisposableDroidBB.ttf', fontsize=100,
                 color=pygame.Color('black')):
        super().__init__(group)
        self.group = group
        self.size = size
        self.text = text
        if self.size is None:
            self.image = load_image('button.png')
        else:
            self.image = pygame.transform.scale(
                load_image('button.png'), self.size)

        self.pressed = False
        self.active = True

        self.text_color = color
        self.font = pygame.font.Font(font, fontsize)
        self.rendered_text = self.render_text(text)
        self.place = self.rendered_text.get_rect(
            center=self.image.get_rect().center)
        self.image.blit(self.rendered_text, self.place)

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def render_text(self, text):
        return self.font.render(text, 1, self.text_color)

    def get_rect(self):
        return self.rect

    def press(self):
        '''
        Нажатие кнопки (кнопка не нажимается, если не активна)
        '''
        if self.active:
            if self.size is None:
                self.image = load_image('button_press.png')
            else:
                self.image = pygame.transform.scale(
                    load_image('button_press.png'), self.size)
            self.image.blit(self.rendered_text, self.place)
            self.pressed = True

    def unpress(self):
        '''
        Отжатие кнопки (кнопка посчитается отжатой, если она была нажатой и активной)
        '''
        if self.active:
            if self.size is None:
                self.image = load_image('button.png')
            else:
                self.image = pygame.transform.scale(
                    load_image('button.png'), self.size)
            self.image.blit(self.rendered_text, self.place)
            if self.pressed:
                self.pressed = False
                return True
            else:
                return False

    def make_active(self):
        '''
        Делает кнопку активной (доступной для нажатия)
        '''
        self.active = True
        if self.size is None:
            self.image = load_image('button.png')
        else:
            self.image = pygame.transform.scale(
                load_image('button.png'), self.size)
        self.image.blit(self.rendered_text, self.place)

    def make_inactive(self):
        '''
        Делает кнопку не активной (недоступной для нажатия)
        '''
        self.active = False
        if self.size is None:
            self.image = load_image('button_inactive.png')
        else:
            self.image = pygame.transform.scale(
                load_image('button_inactive.png'), self.size)
        self.image.blit(self.rendered_text, self.place)

    def is_active(self):
        return self.active


class Game:
    '''
    Класс игры. Здесь происходят смены всех экранов и реализованы функции всех экранов
    '''
    def __init__(self):
        pygame.init()
        pygame.mouse.set_visible(False)
        self.WIDTH = 1280
        self.HEIGHT = 720
        self.FPS = 60
        self.clock = pygame.time.Clock()
        self.node = Node()  # ссылка на узел, с которым работает игра

        # на MacBook'ах полный экран работает неправильно, поэтому он не будет включаться на них
        if 'MacBook' in self.node.hostname:
            self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        else:
            self.screen = pygame.display.set_mode(
                (self.WIDTH, self.HEIGHT), pygame.FULLSCREEN)

        self.cursor_group = pygame.sprite.Group()
        self.buttons_group = pygame.sprite.Group()
        self.notification_group = pygame.sprite.Group()
        self.cursor = Cursor(self.cursor_group)

        self.players = []
        # включение музыки
        pygame.mixer.music.load('data/music.mp3')
        pygame.mixer.music.play(-1)

        # основной цикл смены экранов
        next_screen = self.start_screen()
        while True:
            next_screen = next_screen()

    def terminate(self):
        '''
        Функция выхода из игры
        '''
        pygame.quit()
        sys.exit()

    def start_screen(self):
        '''
        Функция, вызывающая стартовый экран
        '''
        self.buttons_group.empty()

        # функция обновления экрана
        def update_screen():
            background = pygame.transform.scale(load_image(
                'background_test.png'), (self.WIDTH, self.HEIGHT))
            self.screen.blit(background, (0, 0))
            logo = pygame.image.load(os.path.join('data', 'logo.png'))
            self.screen.blit(logo, (200, 50))

        play = Button(self.buttons_group, 340, 300, 'play')
        rules = Button(self.buttons_group, 340, 420, 'rules')
        exit_btn = Button(self.buttons_group, 340, 540, 'exit')

        # основной цикл
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()

                if event.type == pygame.MOUSEMOTION:
                    self.cursor_group.update()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        # нажатие кнопок
                        for button in self.buttons_group:
                            if button.rect.collidepoint(pygame.mouse.get_pos()):
                                button.press()

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        # отжатие кнопок
                        for button in self.buttons_group:
                            if button.unpress() and button.rect.collidepoint(pygame.mouse.get_pos()):
                                if button == play:
                                    return self.game_connection_screen
                                elif button == rules:
                                    return self.game_rules
                                elif button == exit_btn:
                                    self.terminate()

            update_screen()
            self.buttons_group.draw(self.screen)
            if pygame.mouse.get_focused():
                self.cursor_group.draw(self.screen)
            self.clock.tick(self.FPS)
            pygame.display.flip()

    def game_rules(self):
        '''
        Функция, вызывающая экран с правилами
        '''
        self.buttons_group.empty()
        page_num = 0
        rules = {
            0: ['Welcome to the city of Machi Koro, the Japanese card game that is sweeping',
                'the world. You’ve just been elected Mayor. Congratulations! Unfortunately,',
                'the citizens have some pretty big demands: jobs, a theme park, a couple of',
                'cheese factories, and maybe even a radio tower. A tough proposition since',
                'the city currently consists of a wheat field, a bakery, and a single die.',
                'Armed only with your trusty die and a dream, you must grow Machi Koro into',
                'the largest city in the region. You will need to collect income from',
                'developments, build public works, and steal from your neighbors’ coffers.',
                'Just make sure they aren’t doing the same to you! Machi Koro is a fast-',
                'paced, lighthearted game for you and up to 3 friends. Once you’ve had a',
                'taste of Machi Koro, this infectiously fun game may have you wondering if',
                'the dinner table ever served another purpose other than gaming. They say',
                'you can’t build Rome in a day, but Machi Koro will be built in less than',
                '30 minutes!'],
            1: ['Goal',
                'The player to construct all four of their Landmarks first wins the game!',
                'Game Components',
                '108 Cards(84 Supply Establishments, 8 Starting Establishments, 16 Landmarks)',
                '72 Coins(worth 210)',
                '2 Dice',
                'Game Flow',
                'Players take turns in clockwise order.',
                'A turn consists of the following three phases:',
                '* Roll Dice',
                '* Earn Income',
                '* Construction',
                'Earn Income',
                'Players earn income based on the dice roll and the effects of the',
                'Establishments that they own that match the dice roll.'],
            2: ['Types of income',
                'Blue: Primary Industry',
                'Get income from the bank, during anyone’s turn.',
                'Red: Restaurants',
                'Take coins from the person who rolled the dice.',
                'Green: Secondary Industry',
                'Get income from the bank, during your turn only.',
                'Purple: Major Establishments',
                'Get income from all other players, but during your turn only.'],
            3: ['Order of activation',
                'It is possible that multiple types of Establishments are activated by the',
                'same die roll, in this case the Establishments are activated in the',
                'following order:',
                '1. Restaurants (Red)',
                '2. Secondary Industry (Green) and Primary Industry (Blue)',
                '3. Major Establishments (Purple)',
                'If a player owns multiple copies of a single Establishment, the effects are',
                'multiplied by the number of Establishments of that type owned. Players may',
                'not construct more than one of each of the purple Establishments in their town.',
                'A player may construct as many unique cards as they choose, but may never',
                'construct a second of the same purple card. If a player owes another player',
                'money and cannot afford to pay it, they pay what they can and the rest is',
                'exempted (a player’s coin total can never go below zero), the receiving player',
                'is not compensated for the lost income. If payment is owed to multiple players at',
                'the same time, payment is processed in reverse player order (counter clockwise).'],
            4: ['Building New Establishments and Completing Landmarks',
                'To conclude a player’s turn, he or she may pay to construct one single',
                'Establishment OR pay to finish construction on a single Landmark by paying',
                'the cost shown on the lower left-hand corner of the card. Once constructed,',
                'an Establishment is taken from the supply and added to the player’s play area.']
        }

        def update_screen():
            background = pygame.transform.scale(load_image(
                'background_test.png'), (self.WIDTH, self.HEIGHT))
            self.screen.blit(background, (0, 0))

            back_image = pygame.transform.scale(
                load_image('button.png'), (1260, 550))
            self.screen.blit(back_image, (10, 50))
            font = pygame.font.Font('data/DisposableDroidBB.ttf', 35)
            text_coord = 50
            for line in rules[page_num]:
                string_rendered = font.render(line, 1, pygame.Color('black'))
                intro_rect = string_rendered.get_rect()
                text_coord += 30
                intro_rect.top = text_coord
                intro_rect.x = 25
                self.screen.blit(string_rendered, intro_rect)

        next_btn = Button(self.buttons_group, 940, 650,
                          'next', (300, 50), fontsize=50)
        prev_btn = Button(self.buttons_group, 540, 650,
                          'prev', (300, 50), fontsize=50)
        back = Button(self.buttons_group, 20, 650,
                      'back', (150, 50), fontsize=50)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                if event.type == pygame.MOUSEMOTION:
                    self.cursor_group.update()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        for button in self.buttons_group:
                            if button.rect.collidepoint(pygame.mouse.get_pos()):
                                button.press()
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        for button in self.buttons_group:
                            if button.unpress() and button.rect.collidepoint(pygame.mouse.get_pos()):
                                if button == next_btn:
                                    if page_num < 4:
                                        page_num += 1
                                elif button == prev_btn:
                                    if page_num > 0:
                                        page_num -= 1
                                elif button == back:
                                    return self.start_screen

            update_screen()
            self.buttons_group.draw(self.screen)
            if pygame.mouse.get_focused():
                self.cursor_group.draw(self.screen)
            pygame.display.flip()

    def game_connection_screen(self):
        '''
        Функция, вызывающая экран поиска игры
        '''
        self.buttons_group.empty()

        def update_screen():
            background = pygame.transform.scale(load_image(
                'background_test.png'), (self.WIDTH, self.HEIGHT))
            self.screen.blit(background, (0, 0))
            logo = pygame.image.load(os.path.join('data', 'logo.png'))
            self.screen.blit(logo, (200, 50))

        connect = Button(self.buttons_group, 340, 300, 'connect')
        new_game = Button(self.buttons_group, 340, 420, 'new game')
        back = Button(self.buttons_group, 20, 650,
                      'back', size=(150, 50), fontsize=50)

        counter = 0
        # флаги, с которыми работают потоки
        flags = {'searching_for_game': False, 'game_found': False, 'searching_for_players': False,
                 'players': [{'ip': self.node.ip}], 'game_host': {'ip': '1'},
                 'game_connected': False,
                 'game_closed': False, 'game_started': {'text': False}}

        # основной цикл
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()

                if event.type == pygame.MOUSEMOTION:
                    self.cursor_group.update()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        for button in self.buttons_group:
                            if button.rect.collidepoint(pygame.mouse.get_pos()):
                                button.press()
                            for elem in self.notification_group:
                                if isinstance(elem, Button):
                                    if elem.rect.collidepoint(pygame.mouse.get_pos()):
                                        elem.press()

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        for button in self.buttons_group:
                            if button.unpress() and button.rect.collidepoint(pygame.mouse.get_pos()):
                                if button == connect:
                                    # начало поиска игры
                                    flags['searching_for_game'] = True
                                    flags['game_found'] = False
                                    flags['game_connected'] = False
                                    flags['game_closed'] = False
                                    notification = Notification(self.notification_group,
                                                                ('searching for the game.',))
                                    thread = MyThread(self.node.await_receive, 'serching',
                                                        ['searching for players', 'text',
                                                        [[flags, 'game_found', True],
                                                        [flags, 'game_host',
                                                            '__VALUE__'],
                                                        [flags, 'searching_for_game',
                                                            False]], 1])
                                    thread.start()
                                elif button == new_game:
                                    # начало поиска игроков
                                    notification = Notification(self.notification_group,
                                                                ('searching for players (1/4).',
                                                                    self.node.ip),
                                                                add_button='start')
                                    flags['searching_for_players'] = True
                                    thread = MyThread(self.node.await_receive, 'connection',
                                                        ['connect', 'text', [
                                                            [flags, 'players', '__VALUE__']], -1],
                                                        ['disconnect', 'text',
                                                        [[flags, 'players', '__VALUE_DEL__']], -1])
                                    thread.start()
                                    notification.add_button.make_inactive()
                                elif button == back:
                                    # перемещение на стартовый экран
                                    self.notification_group.empty()
                                    return self.start_screen
                        for elem in self.notification_group:
                            if isinstance(elem, Button):
                                if elem.unpress():
                                    if elem == notification.close_button:
                                        # закрытие уведомления и отмена поиска игры или отмена подключения
                                        if elem.rect.collidepoint(pygame.mouse.get_pos()):
                                            self.notification_group.empty()
                                            if flags['game_found']:
                                                self.node.send(
                                                    'disconnect', flags['game_host']['ip'])
                                            if flags['searching_for_players']:
                                                self.node.send(
                                                    'search stopped')
                                            flags['searching_for_game'] = False
                                            flags['game_found'] = False
                                            flags['game_closed'] = False
                                            flags['searching_for_players'] = False
                                            flags['players'] = [
                                                {'ip': self.node.ip}]
                                            flags['game_host'] = {'ip': -1}
                                            if thread.is_alive():
                                                self.stop_threads()

                                    elif elem == notification.add_button:
                                        # начало игры, если достаточно игроков
                                        players = [elem['ip']
                                                   for elem in flags['players']]
                                        if len(players) > 1:
                                            if thread.is_alive():
                                                self.stop_threads()
                                            self.players = [
                                                Player(player, player == self.node.ip) for player in players]
                                            shuffle(self.players)
                                            self.deck = 6 * ALL_CARDS['wheat_field'] + 6 * ALL_CARDS['ranch'] + 6 * ALL_CARDS['forest'] + \
                                                6 * ALL_CARDS['mine'] + 6 * ALL_CARDS['apple_orchard'] + 6 * ALL_CARDS['bakery'] + \
                                                6 * ALL_CARDS['convenience_store'] + 6 * ALL_CARDS['cheese_factory'] + \
                                                6 * ALL_CARDS['furniture_factory'] + 6 * ALL_CARDS['market'] + 6 * ALL_CARDS['cafe'] + \
                                                6 * ALL_CARDS['family_restaurant'] + 4 * ALL_CARDS['stadium'] + \
                                                4 * \
                                                ALL_CARDS['tv_station'] + 4 * \
                                                ALL_CARDS['business_center']
                                            shuffle(self.deck)
                                            self.node.send('start game', map(lambda x: x.get_ip(), self.players), players=list(
                                                map(str, self.players)), deck=list(map(str, self.deck)))
                                            return self.game_screen

            update_screen()
            if not self.notification_group:
                for elem in self.buttons_group:
                    if not elem.is_active():
                        elem.make_active()
            else:
                for elem in self.buttons_group:
                    if elem.is_active():
                        elem.make_inactive()
            self.buttons_group.draw(self.screen)
            if flags['searching_for_game']:
                # обновление текста о поиске
                if counter % 20 == 0:
                    notification.update(
                        text=('searching for the game' + "." * abs(counter % 3 - 3),))
            if flags['game_found']:
                if not flags['game_connected']:
                    # подключение к игре
                    if thread.is_alive():
                        self.stop_threads()
                    flags['game_connected'] = True
                    self.node.send('connect', flags['game_host']['ip'])
                    thread = MyThread(self.node.await_receive, 'game_start_stop', ['search stopped', 'text',
                                                                                   [[flags, 'game_host', {'ip': -1}],
                                                                                    [flags, 'game_found', False],
                                                                                    [flags, 'searching_for_game',
                                                                                     False],
                                                                                    [flags, 'game_connected', False],
                                                                                    [flags, 'game_closed', True]], 1],
                                      ['start game', 'text',
                                       [[flags, 'game_started', '__VALUE__']], 1])
                    thread.start()
                if counter % 20 == 0:
                    # обновдление текста об игре
                    notification.update(text=('game is ready', f"game host: {flags['game_host']['ip']}",
                                              'connecting' + "." * abs(counter % 3 - 3)))
            if flags['game_closed']:
                # обновление текста о том, что игрок вышел
                notification.update(
                    text=('host has left the game', 'please restart search'))
                if thread.is_alive():
                    self.stop_threads()
            if flags['searching_for_players']:
                # обновление текста об игре
                players = [elem['ip'] for elem in flags['players']]
                if len(players) == 4:
                    # начало игры
                    self.players = [
                        Player(player, player == self.node.ip) for player in players]
                    shuffle(self.players)
                    self.node.send('start game', map(lambda x: x.get_ip(), self.players), players=list(
                        map(str, self.players)), deck=list(map(str, self.deck)))
                    return self.game_screen
                if counter % 20 == 0:
                    self.node.send('searching for players')
                    notification.update(
                        text=[f'searching for players ({len(players)}/4)' + "." * abs(counter % 3 - 3)] + players)
                    if len(players) > 1:
                        notification.add_button.make_active()
                    else:
                        notification.add_button.make_inactive()
            if flags['game_started']['text']:
                # начало игры (на принимающей стороне)
                self.players = list(
                    map(json.loads, flags['game_started']['players']))
                self.deck = list(
                    map(lambda x: ALL_CARDS[x], flags['game_started']['deck']))
                for card in self.deck:
                    card.cost = card.cost
                    card.die_roll = card.get_die_roll()
                    card.description = card.description
                self.stop_threads()
                return self.game_screen

            self.notification_group.draw(self.screen)
            if pygame.mouse.get_focused():
                self.cursor_group.draw(self.screen)
            self.clock.tick(self.FPS)
            counter += 1
            pygame.display.flip()

    def game_screen(self):
        '''
        Функция, вызывающая экран игры
        '''
        latest_message = {'message': {'ip': None}}
        # создание потока, принимающего сообщения
        listener_thread = MyThread(
            self.node.receive, 'receiver', latest_message, 'message')
        listener_thread.start()
        self.buttons_group.empty()
        self.notification_group.empty()
        self.players_icon_group = pygame.sprite.Group()
        self.shop_group = pygame.sprite.Group()
        self.shop_notifications_group = pygame.sprite.Group()
        self.block_notification_group = pygame.sprite.Group()
        self.roll_notification_group = pygame.sprite.Group()
        self.block_group = pygame.sprite.Group()
        self.table_group = pygame.sprite.Group()
        self.landmark_group = pygame.sprite.Group()
        self.block = Table(self.screen)
        self.take_money = 0
        self.extra_turn = False

        def update_screen():
            background = pygame.transform.scale(load_image(
                'background_test.png'), (self.WIDTH, self.HEIGHT))
            self.screen.blit(background, (0, 0))

        # покупка карты из магазина
        def buy_card(player, card_sprite, is_myself):
            player.get_cards()[card_sprite.card.type].append(card_sprite.card)
            player.money -= card_sprite.card.cost
            player.buy_flag = False

            if self.deck:
                ShopCardSprite(self.shop_group, self.deck.pop(
                ), *card_sprite.get_coords())

            if is_myself:
                self.node.send('buy', map(lambda x: x.get_ip(), self.players),
                               coords=shop_notification.sprite.get_coords())
                shop_notification.sprite.kill()
                self.shop_notifications_group.empty()

        # постройка достропримечательности
        def build(player, landmark_sprite, is_myself):
            if isinstance(landmark_sprite, Landmark):
                player.get_landmarks()[landmark_sprite.short_name].build()
                player.money -= landmark_sprite.cost
                player.buy_flag = False

                if is_myself:
                    self.node.send('landmark', map(
                        lambda x: x.get_ip(), self.players), name=landmark_sprite.short_name)
                    shop_notification.sprite.kill()
                    self.shop_notifications_group.empty()
            else:
                player.get_landmarks()[landmark_sprite.card.short_name].build()
                player.money -= landmark_sprite.card.cost
                player.buy_flag = False

                if is_myself:
                    self.node.send('landmark', map(
                        lambda x: x.get_ip(), self.players), name=landmark_sprite.card.short_name)
                    shop_notification.sprite.kill()
                    self.shop_notifications_group.empty()

            for i, key in enumerate(self.myself.landmarks):
                LandmarkSprite(self.landmark_group,
                               self.myself.landmarks[key], i)

        # обработка срабатывающих карт на бросок кубика
        def trigger_cards(die_roll, cur_player):
            result = 0
            for player in self.players:
                for type_ in player.get_cards().keys():
                    if type_ == 'cup' and cur_player != player:
                        if player.get_landmarks()['mall'].get_active():
                            for card in player.get_cards()[type_]:
                                if die_roll in card.get_die_roll():
                                    if player == self.myself:
                                        result += take_money(
                                            card.get_production() + 1)
                        else:
                            for card in player.get_cards()[type_]:
                                if die_roll in card.get_die_roll():
                                    if player == self.myself:
                                        result += take_money(card.get_production())

                    elif type_ in {'wheat', 'cow', 'gear'}:
                        for card in player.get_cards()[type_]:
                            if die_roll in card.get_die_roll():
                                if player == self.myself:
                                    result += card.get_production()
                                player.money += card.get_production()
                    elif type_ == 'bread' and cur_player == player:
                        if player.get_landmarks()['mall'].get_active():
                            for card in player.get_cards()[type_]:
                                if die_roll in card.get_die_roll():
                                    if player == self.myself:
                                        result += card.get_production() + 1
                                    player.money += card.get_production() + 1
                        else:
                            for card in player.get_cards()[type_]:
                                if die_roll in card.get_die_roll():
                                    if player == self.myself:
                                        result += card.get_production()
                                    player.money += card.get_production()
                    elif type_ == 'fruit' and cur_player == player:
                        for card in player.get_cards()[type_]:
                            if die_roll in card.get_die_roll():
                                if player == self.myself:
                                    result += len(player.get_cards()
                                                  ['wheat']) * 3
                                player.money += len(player.get_cards()
                                                    ['wheat']) * 3
                    elif type_ == 'factory' and cur_player == player:
                        for card in player.get_cards()[type_]:
                            if card.get_name() == 'Cheese Factory':
                                if die_roll in card.get_die_roll():
                                    if player == self.myself:
                                        result += len(player.get_cards()
                                                      ['cow']) * 3
                                    player.money += len(player.get_cards()
                                                        ['cow']) * 3
                            else:  # Furniture Factory
                                if die_roll in card.get_die_roll():
                                    if player == self.myself:
                                        result += len(player.get_cards()
                                                      ['gear']) * 3
                                    player.money += len(player.get_cards()
                                                        ['gear']) * 3
                    elif type_ == 'major' and cur_player == player:
                        for card in player.get_cards()[type_]:
                            if card.get_name() == 'TV station':
                                if die_roll in card.get_die_roll():
                                    if player == self.myself:
                                        result += take_money(card.get_production())
                            elif card.get_name() == 'Stadium':
                                if die_roll in card.get_die_roll():
                                    if player == self.myself:
                                        result += (len(self.players) - 1) * 2
                                    player.money += (len(self.players) - 1) * 2
                                    for inner_player in self.players:
                                        if inner_player != cur_player:
                                            inner_player.money -= 2
                            else:  # Business Center
                                if die_roll in card.get_die_roll():
                                    if player == self.myself:
                                        result += card.get_production()
                                    player.money += card.get_production()
            return result

        # отнятие монет у игрока (за красные здания)
        def take_money(amount):
            s = '' if amount == 1 else 's'
            notification = Notification(self.notification_group, [
                                        f'Click on another player to take {amount}', f'coin{s} from them'])
            self.take_money = True
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.terminate()

                    if event.type == pygame.MOUSEMOTION:
                        self.cursor_group.update()

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            for elem in self.notification_group:
                                if isinstance(elem, Button):
                                    if elem.rect.collidepoint(pygame.mouse.get_pos()):
                                        elem.press()

                    if event.type == pygame.MOUSEBUTTONUP:
                        if event.button == 1:
                            if self.take_money:
                                for icon in self.players_icon_group:
                                    if icon.rect.collidepoint(pygame.mouse.get_pos()) and icon.player != self.myself:
                                        minus = amount if amount <= icon.player.get_money() else icon.player.get_money()
                                        victim = list(filter(lambda x: x == icon.player, self.players))[0]
                                        victim.money -= minus
                                        self.myself.money += minus
                                        self.take_money = False
                                        self.node.send('take', map(lambda x: x.get_ip(
                                        ), self.players), coins=minus, victim_ip=icon.player.get_ip())
                                        self.notification_group.empty()
                                        return minus

                            for elem in self.notification_group:
                                if isinstance(elem, Button):
                                    if elem.unpress() and elem.rect.collidepoint(pygame.mouse.get_pos()):
                                        if elem == notification.close_button:
                                            self.notification_group.empty()

                update_screen()
                self.players_icon_group.draw(self.screen)
                self.shop_group.draw(self.screen)
                self.buttons_group.draw(self.screen)
                self.notification_group.draw(self.screen)
                if pygame.mouse.get_focused():
                    self.cursor_group.draw(self.screen)
                self.clock.tick(self.FPS)
                pygame.display.flip()
        
        self.prev_roll = 0

        # бросок кубика
        def dice_roll(amount, get_same=False):
            if get_same:
                cur_die_roll = self.prev_roll
                self.node.send(f'roll {cur_die_roll}', map(
                        lambda x: x.get_ip(), self.players))
                result = trigger_cards(cur_die_roll, self.myself)
                s = '' if result == 1 else 's'
                notification = Notification(self.notification_group, [
                                                    f'You rolled {cur_die_roll}', f'You got {result} coin{s}'])
                return str(self.prev_roll), notification
            if amount == 2 and self.myself.get_landmarks()['park'].get_active():
                roll_1 = randint(1, 6)
                roll_2 = randint(1, 6)
                cur_die_roll = roll_1 + roll_2
                self.myself.dice_rolled = True
                if self.myself.get_landmarks()['tower'].get_active() and self.myself.can_reroll():
                    self.prev_roll = cur_die_roll
                else:
                    result = trigger_cards(cur_die_roll, self.myself)
                    s = '' if result == 1 else 's'
                if roll_1 == roll_2:
                    self.node.send(f'roll {cur_die_roll} __EXTRA_TURN__', map(
                        lambda x: x.get_ip(), self.players))
                    notification = Notification(self.notification_group, [
                                                f'You rolled {cur_die_roll}', f'You got {result} coin{s}',
                                                'You take an extra turn'])
                    return str(cur_die_roll) + ' __EXTRA_TURN__', notification
                else:
                    if self.myself.get_landmarks()['tower'].get_active() and self.myself.can_reroll():
                        notification = DieRollNotification(self.roll_notification_group, [
                            f'You rolled {cur_die_roll}'], 'reroll', 'pass')
                    else:
                        notification = Notification(self.notification_group, [
                                                    f'You rolled {cur_die_roll}', f'You got {result} coin{s}'])
                    return cur_die_roll, notification
            else:
                cur_die_roll = sum([randint(1, 6) for _ in range(amount)])
                if self.myself.get_landmarks()['tower'].get_active() and self.myself.can_reroll():
                    self.prev_roll = cur_die_roll
                else:
                    self.node.send(f'roll {cur_die_roll}', map(
                        lambda x: x.get_ip(), self.players))
                    cur_player.dice_rolled = True
                    result = trigger_cards(cur_die_roll, cur_player)
                    s = '' if result == 1 else 's'
                if self.myself.get_landmarks()['tower'].get_active() and self.myself.can_reroll():
                    notification = DieRollNotification(self.roll_notification_group, [
                        f'You rolled {cur_die_roll}'], 'reroll', 'pass')
                else:
                    notification = Notification(self.notification_group, [
                                                f'You rolled {cur_die_roll}', f'You got {result} coin{s}'])
                return cur_die_roll, notification

        # создание магазина
        for x in range(5):
            for y in range(3):
                ShopCardSprite(self.shop_group, self.deck.pop(), x, y)

        # определения себя в пуле игроков
        self.myself = list(filter(lambda x: x.get_ip() ==
                                  self.node.ip, self.players))[0]

        # создание иконок игроков
        for i, player in enumerate(self.players):
            PlayerIcon(self.players_icon_group, i ==
                       0, self.myself == player, player, i)

        exit_btn = Button(self.buttons_group, 20, 650,
                          'exit', (150, 50), fontsize=50)
        end_turn = Button(self.buttons_group, 1060, 650, 'end turn',
                          (200, 50), fontsize=50) if self.players[0] == self.myself else None

        # создание спрайтов достопримечательносей
        for i, key in enumerate(self.myself.landmarks):
            LandmarkSprite(self.landmark_group, self.myself.landmarks[key], i)

        # переменная текущего хода
        cur_turn = 0

        # основной цикл
        while True:
            # определение текущего игрока
            cur_player = self.players[cur_turn % len(self.players)]

            # определение, нужно ли включать кнопку передачи хода
            if cur_player != self.myself and end_turn is not None:
                end_turn.kill()
                end_turn = None
            elif cur_player == self.myself and end_turn is None:
                end_turn = Button(self.buttons_group, 1060,
                                  650, 'end turn', (200, 50), fontsize=50)

            # бросок кубика, если вы - активный игрок
            if cur_player == self.myself and not cur_player.dice_rolled:
                self.myself.reroll = True
                cur_player.dice_rolled = True
                if not self.myself.get_landmarks()['station'].get_active():
                    cur_die_roll, notification = dice_roll(1)
                else:
                    notification = DieRollNotification(
                        self.roll_notification_group, ('How many dice you', 'want to roll?'))

            # создание спрайтов блоков игрока
            self.block_group.empty()
            for i, type_ in enumerate(self.myself.cards):
                counter = Counter(
                    [card.name for card in self.myself.cards[type_]])
                for j, block in enumerate(counter.most_common()):
                    Block(self.block_group,
                          self.myself.cards[type_][j], block[1], i, j)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()

                if event.type == pygame.MOUSEMOTION:
                    self.cursor_group.update()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if not self.notification_group and not self.roll_notification_group:
                            for button in self.buttons_group:
                                if button.rect.collidepoint(pygame.mouse.get_pos()):
                                    button.press()
                            for elem in self.shop_notifications_group:
                                if isinstance(elem, Button):
                                    if elem.rect.collidepoint(pygame.mouse.get_pos()):
                                        elem.press()
                            for elem in self.block_notification_group:
                                if isinstance(elem, Button):
                                    if elem.rect.collidepoint(pygame.mouse.get_pos()):
                                        elem.press()
                        for elem in self.notification_group:
                            if isinstance(elem, Button):
                                if elem.rect.collidepoint(pygame.mouse.get_pos()):
                                    elem.press()
                        for elem in self.roll_notification_group:
                            if isinstance(elem, Button):
                                if elem.rect.collidepoint(pygame.mouse.get_pos()):
                                    elem.press()

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        if not self.notification_group and not self.roll_notification_group:
                            for button in self.buttons_group:
                                if button.unpress() and button.rect.collidepoint(pygame.mouse.get_pos()):
                                    if button == exit_btn:
                                        self.stop_threads()
                                        self.node.send(
                                            'exit game', map(lambda x: x.get_ip(), self.players))
                                        self.players = []
                                        self.shop_group.empty()
                                        self.players_icon_group.empty()
                                        return self.start_screen
                                    elif button == end_turn:
                                        self.node.send(
                                            'end turn', map(lambda x: x.get_ip(), self.players))
                                        if not self.extra_turn:
                                            cur_turn += 1
                                        else:
                                            self.extra_turn = False
                                        cur_player = self.players[cur_turn % len(
                                            self.players)]
                                        cur_player.buy_flag = True
                            for card in self.shop_group:
                                # открытие уведомления при клике на карту
                                if card.rect.collidepoint(pygame.mouse.get_pos()):
                                    shop_notification = ShopNotification(self.shop_notifications_group, card, self.myself, self.myself ==
                                                                         cur_player)
                            for landmark in self.landmark_group:
                                # открытие уведомления при клике на достопримечательность
                                if landmark.rect.collidepoint(pygame.mouse.get_pos()):
                                    shop_notification = ShopNotification(self.shop_notifications_group, landmark,
                                                                         self.myself, self.myself ==
                                                                         cur_player)
                            for elem in self.shop_notifications_group:
                                if isinstance(elem, Button):
                                    if elem.unpress() and elem.rect.collidepoint(pygame.mouse.get_pos()):
                                        if elem == shop_notification.buy_button:
                                            if shop_notification.is_active and self.myself.buy_flag:
                                                if isinstance(shop_notification.card, Card):
                                                    buy_card(
                                                        self.myself, shop_notification.sprite, True)
                                                elif isinstance(shop_notification.card, Landmark):
                                                    build(
                                                        self.myself, shop_notification.sprite, True)
                                            else:
                                                elem.make_inactive()
                                        elif elem == shop_notification.close_button:
                                            self.shop_notifications_group.empty()
                            for block in self.block_group:
                                if block.rect.collidepoint(pygame.mouse.get_pos()):
                                    block_notification = BlockNotification(
                                        self.block_notification_group, block.block)
                            for elem in self.block_notification_group:
                                if isinstance(elem, Button):
                                    if elem.unpress() and elem.rect.collidepoint(pygame.mouse.get_pos()):
                                        if elem == block_notification.close_button:
                                            self.block_notification_group.empty()
                        for elem in self.notification_group:
                            if isinstance(elem, Button):
                                if elem.unpress() and elem.rect.collidepoint(pygame.mouse.get_pos()):
                                    if elem == notification.close_button:
                                        self.notification_group.empty()
                                    elif elem == notification.add_button:
                                        self.notification_group.empty()
                                        return self.start_screen
                            elif not elem.rect.collidepoint(pygame.mouse.get_pos()):
                                self.notification_group.empty()
                        for elem in self.roll_notification_group:
                            # вопрос игроку о том, сколько кубов кидать и нужно ли их перебрасывать
                            if isinstance(elem, Button):
                                if elem.unpress() and elem.rect.collidepoint(pygame.mouse.get_pos()):
                                    if elem == notification.close_button:
                                        if notification.close_button.text == 'roll 1':
                                            self.roll_notification_group.empty()
                                            cur_die_roll, notification = dice_roll(
                                                1)
                                        elif notification.close_button.text == 'reroll' and self.myself.can_reroll():
                                            self.myself.reroll = False
                                            self.roll_notification_group.empty()
                                            if not self.myself.get_landmarks()['station'].get_active():
                                                cur_die_roll, notification = dice_roll(
                                                    1)
                                            else:
                                                notification = DieRollNotification(
                                                    self.roll_notification_group, ('How many dice you', 'want to roll?'))
                                    elif elem == notification.add_button:
                                        if notification.add_button.text == 'roll 2':
                                            self.roll_notification_group.empty()
                                            cur_die_roll, notification = dice_roll(
                                                2)
                                        elif notification.add_button.text == 'pass':
                                            cur_die_roll, notification = dice_roll(
                                                0, True)



            # обновление группы уведомлений и покупке карт, если она существует
            try:
                shop_notification.update(self.myself == cur_player)
            except Exception:
                pass

            # обработка прищедших сообщений
            if latest_message['message']['ip'] is not None:
                message = latest_message['message']
                if message['text'] == 'end turn':
                    # передача хода
                    self.notification_group.empty()
                    if not self.extra_turn:
                        cur_turn += 1
                    else:
                        self.extra_turn = False
                    cur_player = self.players[cur_turn % len(self.players)]
                    cur_player.buy_flag = True
                    cur_player.dice_rolled = False
                elif message['text'] == 'exit game':
                    # выход игрока из игры
                    for i, player in enumerate(self.players):
                        if player.get_ip() == message['ip']:
                            if cur_player == player:
                                cur_turn += 1
                            del self.players[i]
                            break
                    if len(self.players) == 1:
                        self.notification_group.empty()
                        return self.start_screen
                elif message['text'] == 'buy':
                    # покупка карты
                    buy_card(list(filter(lambda x: x.get_ip() == message['ip'], self.players))[
                             0], list(filter(lambda x: x.get_coords() == message['coords'], self.shop_group))[0], False)
                elif 'roll' in message['text']:
                    # бросок кубика
                    cur_die_roll = int(message['text'].split()[1])
                    cur_player.dice_rolled = True
                    result = trigger_cards(
                        cur_die_roll, cur_player)
                    s = '' if result == 1 else 's'
                    if '__EXTRA_TURN__' not in message['text']:
                        notification = Notification(self.notification_group, [
                                                    f'{cur_player.get_ip()} rolled {cur_die_roll}', f'You got {result} coin{s}'])
                    else:
                        notification = Notification(self.notification_group, [
                                                    f'{cur_player.get_ip()} rolled {cur_die_roll}', f'You got {result} coin{s}',
                                                    'That player takes an extra turn'])
                        self.extra_turn = True
                elif 'take' in message['text']:
                    # отнятие монет
                    player = list(filter(lambda x: x.get_ip() ==
                                         message['ip'], self.players))[0]
                    victim = list(filter(lambda x: x.get_ip() ==
                                         message['victim_ip'], self.players))[0]
                    player.money += message['coins']
                    victim.money -= message['coins']
                    s = '' if message['coins'] == 1 else 's'
                    if victim == self.myself:
                        notification = Notification(self.notification_group, [
                                                    f'{player.get_ip()} took {message["coins"]} coin{s}', 'from you'])
                    else:
                        notification = Notification(self.notification_group, [
                                                    f'{player.get_ip()} took {message["coins"]} coin{s}', f'from {victim.get_ip()}'])
                elif message['text'] == 'landmark':
                    # покупка достопримечательностей
                    player = list(filter(lambda x: x.get_ip() ==
                                         message['ip'], self.players))[0]

                    build(player, player.get_landmarks()
                          [message['name']], False)

                    if len(player.get_active_landmarks()) == 4:
                        notification = Notification(self.notification_group, [
                                                    f'{player} has won the game!'], add_button='exit')

                latest_message['message'] = {'ip': None}
                # перезапуск потока
                listener_thread = MyThread(
                    self.node.receive, 'receiver', latest_message, 'message')
                listener_thread.start()

            # обновление иконок игроков
            i = 0
            for elem in self.players_icon_group:
                if elem.player in self.players:
                    elem.update(cur_player == elem.player, i)
                    i += 1

            update_screen()
            self.block.update()
            self.players_icon_group.draw(self.screen)
            self.shop_group.draw(self.screen)
            self.buttons_group.draw(self.screen)
            self.block_group.draw(self.screen)
            self.landmark_group.draw(self.screen)
            self.notification_group.draw(self.screen)
            self.shop_notifications_group.draw(self.screen)
            self.block_notification_group.draw(self.screen)
            self.roll_notification_group.draw(self.screen)
            if pygame.mouse.get_focused():
                self.cursor_group.draw(self.screen)
            self.clock.tick(self.FPS)
            pygame.display.flip()

    def stop_threads(self):
        '''
        Функция остановке приёма всех сообщений
        '''
        self.node.send('__STOP_RECEIVE__', self.node.ip)


def main():
    Game()  # начало игры


if __name__ == '__main__':
    main()
