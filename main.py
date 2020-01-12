import os
import socket
import sys
import threading
from random import shuffle
from collections import Counter

import pygame

from node import Node
from utility import MyThread, Player, load_image, Card
from cards import ALL_CARDS


class Notification(pygame.sprite.Sprite):
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

        self.button = Button(group, 910, 450, 'close',
                             size=(150, 50), fontsize=50)
        self.add_button = Button(group, 740, 450, add_button, size=(
            150, 50), fontsize=50) if add_button is not None else None

    def update(self, *args, **kwargs):
        if 'text' in kwargs.keys():
            self.image = pygame.transform.scale(
                load_image('button.png'), (880, 320))
            shift = 280 // (len(kwargs['text']) + 1)
            for i, line in enumerate(kwargs['text']):
                line = self.font.render(line, 1, self.color)
                self.image.blit(line, (20, shift * (i + 1)))


class ShopNotification(pygame.sprite.Sprite):
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
        text = [self.card.name] + self.card.description

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


class TableBlock(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.start_x_pos = 100
        self.start_y_pos = 600
        self.shift_x = 150
        self.shift_y = 80
        self.font = pygame.font.Font('data/DisposableDroidBB.ttf', 25)
        self.color = pygame.Color('black')

        self.bread = pygame.transform.scale(load_image('cards/Bread.png'), (100, 100))
        self.cow = pygame.transform.scale(load_image('cards/Cow.png'), (100, 100))
        self.cup = pygame.transform.scale(load_image('cards/Cup.png'), (100, 100))
        self.factory = pygame.transform.scale(load_image('cards/Factory.png'), (100, 100))
        self.fruit = pygame.transform.scale(load_image('cards/Fruit.png'), (100, 100))
        self.gear = pygame.transform.scale(load_image('cards/Gear.png'), (100, 100))
        self.major = pygame.transform.scale(load_image('cards/Major.png'), (100, 100))
        self.wheat = pygame.transform.scale(load_image('cards/Wheat.png'), (100, 100))

        types_ = [self.bread, self.cow, self.cup, self.factory, self.fruit, self.gear, self.major, self.wheat]

        for i, el in enumerate(types_):
            el.rect = el.get_rect()
            el.rect.x, el.rect.y = self.start_x_pos + self.shift_x * i, self.start_y_pos


class Block:
    def __init__(self, group, block, amount, x, y):
        super().__init__(group)
        self.block = block
        self.card_image = self.block.image
        self.amount = amount
        self.image = pygame.transform.scale(load_image('button.png'), (120, 80))
        self.start_x_pos = 100
        self.start_y_pos = 600
        self.shift_x = 150
        self.shift_y = 80
        self.image.rect = self.image.get_rect()
        self.image.rect.x = self.start_x_pos + self.shift_x * x
        self.image.rect.y = self.start_y_pos + self.shift_y * y
        self.font = pygame.font.Font('data/DisposableDroidBB.ttf', 25)
        self.color = pygame.Color('black')
        text = self.font.render(f'{block.die_roll} {block.name} {amount}', 1, self.color)
        self.image.blit(text, (5, 5))


class BlockNotification:
    def __init__(self, group, card_sprite):
        self.image = pygame.transform.scale(
            load_image('button.png'), (880, 320))
        self.card_image = pygame.transform.scale(
            load_image(card_sprite.card.get_image()), (180, 270))
        self.image.blit(self.card_image, (690, 25))
        self.card = card_sprite.card

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


class PlayerIcon(pygame.sprite.Sprite):
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
            f': {len(self.player.get_landmarks())}', 1, pygame.Color('black'))
        self.image.blit(line, (215, 65))
        line = self.font.render(self.player.get_ip(
        ) if not self.is_myself else 'me', 1, pygame.Color('black'))
        self.image.blit(line, (5, 5))

    def update(self, is_active, count=None):
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
            f': {len(self.player.get_landmarks())}', 1, pygame.Color('black'))
        self.image.blit(line, (215, 65))
        line = self.font.render(self.player.get_ip(
        ) if not self.is_myself else 'me', 1, pygame.Color('black'))
        self.image.blit(line, (5, 5))


class Cursor(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.group = group
        self.image = load_image('cursor.png', -2)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pygame.mouse.get_pos()

    def update(self):
        self.rect.x, self.rect.y = pygame.mouse.get_pos()


class Button(pygame.sprite.Sprite):
    def __init__(self, group, x, y, text, size=None, font='data/DisposableDroidBB.ttf', fontsize=100,
                 color=pygame.Color('black')):
        super().__init__(group)
        self.group = group
        self.size = size
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
        if self.active:
            if self.size is None:
                self.image = load_image('button_press.png')
            else:
                self.image = pygame.transform.scale(
                    load_image('button_press.png'), self.size)
            self.image.blit(self.rendered_text, self.place)
            self.pressed = True

    def unpress(self):
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

    def update(self, *args, **kwargs):
        self.unpress()

    def make_active(self):
        self.active = True
        if self.size is None:
            self.image = load_image('button.png')
        else:
            self.image = pygame.transform.scale(
                load_image('button.png'), self.size)
        self.image.blit(self.rendered_text, self.place)

    def make_inactive(self):
        self.active = False
        if self.size is None:
            self.image = load_image('button_inactive.png')
        else:
            self.image = pygame.transform.scale(
                load_image('button_inactive.png'), self.size)
        self.image.blit(self.rendered_text, self.place)


class Game:
    def __init__(self):
        pygame.init()
        pygame.mouse.set_visible(False)
        self.WIDTH = 1280
        self.HEIGHT = 720
        self.FPS = 60
        self.clock = pygame.time.Clock()
        self.node = Node()

        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))

        self.cursor_group = pygame.sprite.Group()
        self.buttons_group = pygame.sprite.Group()
        self.notification_group = pygame.sprite.Group()
        self.cursor = Cursor(self.cursor_group)

        self.players = []

        next_screen = self.start_screen()
        while True:
            next_screen = next_screen()

    def terminate(self):
        pygame.quit()
        sys.exit()

    def start_screen(self):
        self.buttons_group.empty()

        def update_screen():
            background = pygame.transform.scale(load_image(
                'background_test.jpg'), (self.WIDTH, self.HEIGHT))
            self.screen.blit(background, (0, 0))
            logo = load_image('logo_test.jpg', -1)
            self.screen.blit(logo, (200, 50))

        play = Button(self.buttons_group, 340, 300, 'play')
        rules = Button(self.buttons_group, 340, 420, 'rules')
        exit_btn = Button(self.buttons_group, 340, 540, 'exit')

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
                            if button.rect.collidepoint(pygame.mouse.get_pos()):
                                if button.unpress():
                                    if button == play:
                                        return self.game_connection_screen
                                    elif button == rules:
                                        return self.game_rules
                                    elif button == exit_btn:
                                        self.terminate()
                        self.buttons_group.update()

            update_screen()
            self.buttons_group.draw(self.screen)
            if pygame.mouse.get_focused():
                self.cursor_group.draw(self.screen)
            self.clock.tick(self.FPS)
            pygame.display.flip()

    def game_rules(self):
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
                'background_test.jpg'), (self.WIDTH, self.HEIGHT))
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
                            if button.rect.collidepoint(pygame.mouse.get_pos()):
                                if button.unpress():
                                    if button == next_btn:
                                        if page_num < 4:
                                            page_num += 1
                                    elif button == prev_btn:
                                        if page_num > 0:
                                            page_num -= 1
                                    elif button == back:
                                        return self.start_screen
                        self.buttons_group.update()

            update_screen()
            self.buttons_group.draw(self.screen)
            if pygame.mouse.get_focused():
                self.cursor_group.draw(self.screen)
            pygame.display.flip()

    def game_connection_screen(self):
        self.buttons_group.empty()

        def update_screen():
            background = pygame.transform.scale(load_image(
                'background_test.jpg'), (self.WIDTH, self.HEIGHT))
            self.screen.blit(background, (0, 0))
            logo = load_image('logo_test.jpg', -1)
            self.screen.blit(logo, (200, 50))

        connect = Button(self.buttons_group, 340, 300, 'connect')
        new_game = Button(self.buttons_group, 340, 420, 'new game')
        back = Button(self.buttons_group, 20, 650,
                      'back', size=(150, 50), fontsize=50)

        counter = 0
        flags = {'searching_for_game': False, 'game_found': False, 'searching_for_players': False,
                 'players': [{'ip': self.node.ip}], 'game_host': {'ip': '1'},
                 'game_connected': False,
                 'game_closed': False, 'game_started': {'text': False}}
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
                            if button.rect.collidepoint(pygame.mouse.get_pos()):
                                if button.unpress():
                                    if button == connect:
                                        flags['searching_for_game'] = True
                                        flags['game_found'] = False
                                        flags['game_connected'] = False
                                        flags['game_closed'] = False
                                        notification = Notification(self.notification_group,
                                                                    ('searching for the game.',))
                                        thread = MyThread(self.node.await_recieve, 'serching',
                                                          ['searching for players', 'text',
                                                           [[flags, 'game_found', True],
                                                            [flags, 'game_host',
                                                             '__VALUE__'],
                                                            [flags, 'searching_for_game',
                                                             False]], 1])
                                        thread.start()
                                    elif button == new_game:
                                        notification = Notification(self.notification_group,
                                                                    ('searching for players (1/4).',
                                                                     self.node.ip),
                                                                    add_button='start')
                                        flags['searching_for_players'] = True
                                        thread = MyThread(self.node.await_recieve, 'connection',
                                                          ['connect', 'text', [
                                                              [flags, 'players', '__VALUE__']], -1],
                                                          ['disconnect', 'text',
                                                           [[flags, 'players', '__VALUE_DEL__']], -1])
                                        thread.start()
                                        notification.add_button.make_inactive()
                                    elif button == back:
                                        self.notification_group.empty()
                                        return self.start_screen
                        for elem in self.notification_group:
                            if isinstance(elem, Button):
                                if elem.unpress():
                                    if elem == notification.button:
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
                                            flags['searching_for_players'] = False
                                            flags['players'] = [
                                                {'ip': self.node.ip}]
                                            flags['game_host'] = {'ip': -1}
                                            if thread.is_alive():
                                                self.stop_threads()

                                    elif elem == notification.add_button:
                                        players = [elem['ip']
                                                   for elem in flags['players']]
                                        if len(players) > 1:
                                            if thread.is_alive():
                                                self.stop_threads()
                                            self.players = [
                                                Player(player, player == self.node.ip) for player in players]
                                            shuffle(self.players)
                                            self.deck = 6 * ALL_CARDS['wheat_field'] + 6 * ALL_CARDS['ranch'] + 6 * \
                                                        ALL_CARDS['forest'] + \
                                                        6 * ALL_CARDS['mine'] + 6 * ALL_CARDS['apple_orchard'] + 6 * \
                                                        ALL_CARDS['bakery'] + \
                                                        6 * ALL_CARDS['convenience_store'] + 6 * ALL_CARDS[
                                                            'cheese_factory'] + \
                                                        6 * ALL_CARDS['furniture_factory'] + 6 * ALL_CARDS[
                                                            'market'] + 6 * ALL_CARDS['cafe'] + \
                                                        6 * ALL_CARDS['family_restaurant'] + 4 * ALL_CARDS['stadium'] + \
                                                        4 * \
                                                        ALL_CARDS['tv_station'] + 4 * \
                                                        ALL_CARDS['business_center']
                                            shuffle(self.deck)
                                            self.node.send('start game', map(lambda x: x.ip, self.players),
                                                           players=list(
                                                               map(str, self.players)), deck=list(map(str, self.deck)))
                                            return self.game_screen

                        self.buttons_group.update()

            update_screen()
            if not self.notification_group:
                for elem in self.buttons_group:
                    elem.make_active()
            else:
                for elem in self.buttons_group:
                    elem.make_inactive()
            self.buttons_group.draw(self.screen)
            if flags['searching_for_game']:
                if counter % 20 == 0:
                    notification.update(
                        text=('searching for the game' + "." * abs(counter % 3 - 3),))
            if flags['game_found']:
                if not flags['game_connected']:
                    if thread.is_alive():
                        self.stop_threads()
                    flags['game_connected'] = True
                    self.node.send('connect', flags['game_host']['ip'])
                    thread = MyThread(self.node.await_recieve, 'game_start_stop', ['search stopped', 'text',
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
                    notification.update(text=('game is ready', f"game host: {flags['game_host']['ip']}",
                                              'connecting' + "." * abs(counter % 3 - 3)))
            if flags['game_closed']:
                notification.update(
                    text=('host has left the game', 'please restart search'))
                if thread.is_alive():
                    self.stop_threads()
            if flags['searching_for_players']:
                players = [elem['ip'] for elem in flags['players']]
                if len(players) == 4:
                    self.players = [
                        Player(player, player == self.node.ip) for player in players]
                    shuffle(self.players)
                    self.node.send('start game', map(lambda x: x.ip, self.players), players=list(
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
                self.players = list(
                    map(eval, flags['game_started']['players']))
                self.deck = list(map(eval, flags['game_started']['deck']))
                for card in self.deck:
                    card.cost = int(card.cost)
                    card.die_roll = eval(card.die_roll)
                    card.description = eval(card.description)
                self.stop_threads()
                return self.game_screen

            self.notification_group.draw(self.screen)
            if pygame.mouse.get_focused():
                self.cursor_group.draw(self.screen)
            self.clock.tick(self.FPS)
            counter += 1
            pygame.display.flip()

    def game_screen(self):
        self.buttons_group.empty()
        self.notification_group.empty()
        self.players_icon_group = pygame.sprite.Group()
        self.shop_group = pygame.sprite.Group()
        self.shop_notifications_group = pygame.sprite.Group()
        self.block_notification_group = pygame.sprite.Group()
        self.block_group = pygame.sprite.Group()
        self.table_group = pygame.sprite.Group()
        self.block = TableBlock(self.table_group)

        def update_screen():
            background = pygame.transform.scale(load_image(
                'background_test.jpg'), (self.WIDTH, self.HEIGHT))
            self.screen.blit(background, (0, 0))

        def buy_card(player, card_sprite, is_myself):
            player.get_cards()[card_sprite.card.type].append(card_sprite.card)
            player.money -= card_sprite.card.cost
            player.buy_flag = False

            if self.deck:
                ShopCardSprite(self.shop_group, self.deck.pop(
                ), *card_sprite.get_coords())

            if is_myself:
                self.node.send('buy', map(lambda x: x.ip, self.players),
                               coords=notification.sprite.get_coords())
                notification.sprite.kill()
                self.shop_notifications_group.empty()

        for x in range(5):
            for y in range(3):
                ShopCardSprite(self.shop_group, self.deck.pop(), x, y)

        myself = list(filter(lambda x: x.get_ip() ==
                                       self.node.ip, self.players))[0]

        for i, player in enumerate(self.players):
            PlayerIcon(self.players_icon_group, i ==
                       0, myself == player, player, i)

        exit_btn = Button(self.buttons_group, 20, 650,
                          'exit', (150, 50), fontsize=50)
        end_turn = Button(self.buttons_group, 1060, 650, 'end turn',
                          (200, 50), fontsize=50) if self.players[0] == myself else None

        cur_turn = 0
        latest_message = {'message': {'ip': None}}
        listener_thread = MyThread(
            self.node.recieve, 'reciever', latest_message, 'message')
        listener_thread.start()
        while True:
            cur_player = self.players[cur_turn % len(self.players)]
            cur_player.buy_flag = True
            if cur_player != myself and end_turn is not None:
                self.buttons_group.remove(end_turn)
                end_turn.kill()
                end_turn = None
            elif cur_player == myself and end_turn is None:
                end_turn = Button(self.buttons_group, 1060,
                                  650, 'end turn', (200, 50), fontsize=50)

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
                            for elem in self.shop_notifications_group:
                                if isinstance(elem, Button):
                                    if elem.rect.collidepoint(pygame.mouse.get_pos()):
                                        elem.press()
                            for elem in self.block_notification_group:
                                if isinstance(elem, Button):
                                    if elem.rect.collidepoint(pygame.mouse.get_pos()):
                                        elem.press()

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        for button in self.buttons_group:
                            if button.rect.collidepoint(pygame.mouse.get_pos()):
                                if button.unpress():
                                    if button == exit_btn:
                                        self.stop_threads()
                                        self.node.send(
                                            'exit game', map(lambda x: x.ip, self.players))
                                        self.players = []
                                        self.shop_group.empty()
                                        self.players_icon_group.empty()
                                        return self.start_screen
                                    elif button == end_turn:
                                        self.node.send(
                                            'end turn', map(lambda x: x.ip, self.players))
                                        cur_turn += 1
                        for card in self.shop_group:
                            if card.rect.collidepoint(pygame.mouse.get_pos()):
                                notification = ShopNotification(self.shop_notifications_group, card, myself, myself ==
                                                                cur_player)
                        for elem in self.shop_notifications_group:
                            if isinstance(elem, Button):
                                if elem.unpress():
                                    if elem == notification.buy_button:
                                        if elem.rect.collidepoint(pygame.mouse.get_pos()):
                                            if notification.is_active and myself.buy_flag:
                                                buy_card(
                                                    myself, notification.sprite, True)
                                    elif elem == notification.close_button:
                                        if elem.rect.collidepoint(pygame.mouse.get_pos()):
                                            self.shop_notifications_group.empty()

                        for block in self.block_group:
                            if block.rect.collidepoint(pygame.mouse.get_pos()):
                                block_notification = BlockNotification(self.block_notification_group, block.card_image)
                        for elem in self.block_notification_group:
                            if isinstance(elem, Button):
                                if elem.unpress():
                                    if elem == block_notification.close_button:
                                        if elem.rect.collidepoint(pygame.mouse.get_pos()):
                                            self.block_notification_group.empty()

                        self.buttons_group.update()
            try:
                notification.update(myself == cur_player)
            except Exception:
                pass

            if latest_message['message']['ip'] is not None:
                message = latest_message['message']
                if message['text'] == 'end turn':
                    cur_turn += 1
                elif message['text'] == 'exit game':
                    for i, player in enumerate(self.players):
                        if player.get_ip() == message['ip']:
                            if cur_player == player:
                                cur_turn += 1
                            del self.players[i]
                            break
                    if len(self.players) == 1:
                        return self.start_screen
                elif message['text'] == 'buy':
                    buy_card(list(filter(lambda x: x.ip == message['ip'], self.players))[
                                 0], list(filter(lambda x: x.get_coords() == message['coords'], self.shop_group))[0],
                             False)
                latest_message['message'] = {'ip': None}
                listener_thread = MyThread(
                    self.node.recieve, 'reciever', latest_message, 'message')
                listener_thread.start()

            i = 0
            for elem in self.players_icon_group:
                if elem.player in self.players:
                    elem.update(cur_player == elem.player, i)
                    i += 1

            self.block_group.empty()
            for i, type_ in enumerate(myself.cards):
                c = type_.Counter()
                for j, block in enumerate(c):
                    Block(self.block_group, block, type_[block], i, j)

            update_screen()
            self.players_icon_group.draw(self.screen)
            self.shop_group.draw(self.screen)
            self.buttons_group.draw(self.screen)
            self.shop_notifications_group.draw(self.screen)
            self.block_group.draw(self.screen)
            if pygame.mouse.get_focused():
                self.cursor_group.draw(self.screen)
            self.clock.tick(self.FPS)
            pygame.display.flip()

    def stop_threads(self):
        self.node.send('__STOP_RECIEVE__', self.node.ip)


def main():
    Game()


if __name__ == '__main__':
    main()
