import pygame
import os
import sys
import socket

from utility import load_image, MyThread
from node import Node


class Notification(pygame.sprite.Sprite):
    def __init__(self, group, text, font='data/DisposableDroidBB.ttf', fontsize=50, color=pygame.Color('black'), add_button=None):
        group.empty()
        super().__init__(group)
        self.image = pygame.transform.scale(load_image('button.png'), (880, 320))
        self.rect = self.image.get_rect()
        self.rect.x = 200
        self.rect.y = 200

        self.font = pygame.font.Font(font, fontsize)
        self.color = color
        shift = 280 // (len(text) + 1 )
        for i, line in enumerate(text):
            line = self.font.render(line, 1, color)
            self.image.blit(line, (20, shift * (i + 1)))

        self.button = Button(group, 910, 450, 'close', size=(150, 50), fontsize=50)
        if add_button is not None:
            self.add_button = Button(group, 740, 450, add_button, size=(150, 50), fontsize=50)

    def update(self, *args, **kwargs):
        if 'text' in kwargs.keys():
            self.image = pygame.transform.scale(load_image('button.png'), (880, 320))
            shift = 280 // (len(kwargs['text']) + 1 )
            for i, line in enumerate(kwargs['text']):
                line = self.font.render(line, 1, self.color)
                self.image.blit(line, (20, shift * (i + 1)))
                

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
    def __init__(self, group, x, y, text, size=None, font='data/DisposableDroidBB.ttf', fontsize=100, color=pygame.Color('black')):
        super().__init__(group)
        self.group = group
        self.size = size
        if self.size is None:
            self.image = load_image('button.png')
        else:
            self.image = pygame.transform.scale(load_image('button.png'), self.size)

        self.pressed = False
        self.active = True

        self.text_color = color
        self.font = pygame.font.Font(font, fontsize)
        self.rendered_text = self.render_text(text)
        self.place = self.rendered_text.get_rect(center=self.image.get_rect().center)
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
                self.image = pygame.transform.scale(load_image('button_press.png'), self.size)
            self.image.blit(self.rendered_text, self.place)
            self.pressed = True

    def unpress(self):
        if self.size is None:
            self.image = load_image('button.png')
        else:
            self.image = pygame.transform.scale(load_image('button.png'), self.size)
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

    def make_inactive(self):
        self.active = False


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

        self.start_screen()

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

        update_screen()

        Button(self.buttons_group, 340, 300, 'play')
        Button(self.buttons_group, 340, 420, 'rules')
        Button(self.buttons_group, 340, 540, 'exit')

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()

                if event.type == pygame.MOUSEMOTION:
                    self.cursor_group.update()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        for i, button in enumerate(self.buttons_group):
                            if button.rect.collidepoint(pygame.mouse.get_pos()):
                                button.press()

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        for i, button in enumerate(self.buttons_group):
                            if button.rect.collidepoint(pygame.mouse.get_pos()):
                                if button.unpress():
                                    if i == 0:
                                        self.game_connection_screen()
                                    elif i == 1:
                                        self.game_rules()
                                    elif i == 2:
                                        self.terminate()
                        self.buttons_group.update()

            update_screen()
            self.buttons_group.draw(self.screen)
            if pygame.mouse.get_focused():
                self.cursor_group.draw(self.screen)
            self.clock.tick(self.FPS)
            pygame.display.flip()

    def game_connection_screen(self):
        self.buttons_group.empty()

        def update_screen():
            background = pygame.transform.scale(load_image(
                'background_test.jpg'), (self.WIDTH, self.HEIGHT))
            self.screen.blit(background, (0, 0))
            logo = load_image('logo_test.jpg', -1)
            self.screen.blit(logo, (200, 50))

        update_screen()

        Button(self.buttons_group, 340, 300, 'connect')
        Button(self.buttons_group, 340, 420, 'new game')
        Button(self.buttons_group, 20, 650, 'back', size=(150, 50), fontsize=50)

        counter = 0
        flags = {'searching_for_game': False, 'game_found': False, 'searching_for_players': False, 'players': [{'ip': self.node.ip}], 'game_host': {'ip': -1}, 'game_connected': False, 'game_closed': False}
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()

                if event.type == pygame.MOUSEMOTION:
                    self.cursor_group.update()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        for i, button in enumerate(self.buttons_group):
                            if button.rect.collidepoint(pygame.mouse.get_pos()):
                                button.press()
                        for elem in self.notification_group:
                            if isinstance(elem, Button):
                                if elem.rect.collidepoint(pygame.mouse.get_pos()):
                                    elem.press()

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        for i, button in enumerate(self.buttons_group):
                            if button.rect.collidepoint(pygame.mouse.get_pos()):
                                if button.unpress():
                                    if i == 0:
                                        flags['searching_for_game'] = True
                                        flags['game_found'] = False
                                        flags['game_connected'] = False
                                        flags['game_closed'] = False
                                        notification = Notification(self.notification_group, ('searching for the game.',))
                                        thread = MyThread(self.node.await_recieve, ['searching for players', 'message', [[flags, 'game_found', True], [flags, 'game_host', '__VALUE__'], [flags, 'searching_for_game', False]], 1])
                                        thread.start()
                                    elif i == 1:
                                        notification = Notification(self.notification_group, ('searching for players (1/4).', self.node.ip), add_button='start')
                                        flags['searching_for_players'] = True
                                        thread = MyThread(self.node.await_recieve, ['connect', 'message', [[flags, 'players', '__VALUE__']], -1], ['disconnect', 'message', [[flags, 'players', '__VALUE_DEL__']], -1])
                                        thread.start()
                                    elif i == 2:
                                        self.notification_group.empty()
                                        self.start_screen()
                        for i, elem in enumerate(self.notification_group):
                            if isinstance(elem, Button):
                                if elem.unpress():
                                    if i == 1:
                                        if elem.rect.collidepoint(pygame.mouse.get_pos()):
                                            self.notification_group.empty()
                                            if flags['game_found']:
                                                self.node.send('disconnect', flags['game_host']['ip'])
                                            if flags['searching_for_players']:
                                                self.node.send('search stopped')
                                            flags['searching_for_game'] = False
                                            flags['game_found'] = False
                                            flags['searching_for_players'] = False
                                            flags['players'] = [{'ip': self.node.ip}]
                                            flags['game_host'] = {'ip': -1}
                                            if thread.is_alive():
                                                self.stop_threads()

                                    elif i == 2:
                                        players = [elem['ip'] for elem in flags['players']]
                                        if len(players) > 1:
                                            if thread.id_alive():
                                                self.stop_threads()
                                            print('start game')
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
                    notification.update(text=('searching for the game' + "." * abs(counter % 3 - 3),))
            if flags['game_found']:
                if not flags['game_connected']:
                    if thread.is_alive():
                        self.stop_threads()
                    flags['game_connected'] = True
                    self.node.send('connect', flags['game_host']['ip'])
                    thread = MyThread(self.node.await_recieve, ['search stopped', 'message', [[flags, 'game_host', {'ip': -1}], [flags, 'game_found', False], [flags, 'searching_for_game', False], [flags, 'game_connected', False], [flags, 'game_closed', True]], 1])
                    thread.start()
                if counter % 20 == 0:
                    notification.update(text=('game is ready', f"game host: {flags['game_host']['ip']}", 'connecting' + "." * abs(counter % 3 - 3)))
            if flags['game_closed']:
                notification.update(text=('host has left the game', 'please restart search'))
                if thread.is_alive():
                    self.stop_threads()
            if flags['searching_for_players']:
                self.node.send('searching for players')
                players = [elem['ip'] for elem in flags['players']]
                if counter % 20 == 0:
                    notification.update(text=[f'searching for players ({len(players)}/4)' + "." * abs(counter % 3 - 3)] + players)
                if len(players) == 4:
                    flags['searching_for_players'] = False
                    print('start game')

            self.notification_group.draw(self.screen)
            if pygame.mouse.get_focused():
                self.cursor_group.draw(self.screen)
            self.clock.tick(self.FPS)
            counter += 1
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

            back_image = pygame.transform.scale(load_image('button.png'), (1260, 550))
            self.screen.blit(back_image, (10, -20))
            font = pygame.font.Font('data/DisposableDroidBB.ttf', 35)
            text_coord = -20
            for line in rules[page_num]:
                string_rendered = font.render(line, 1, pygame.Color('black'))
                intro_rect = string_rendered.get_rect()
                text_coord += 30
                intro_rect.top = text_coord
                intro_rect.x = 25
                self.screen.blit(string_rendered, intro_rect)
            '''
            font = pygame.font.Font(None, 50)
            text_coord = 50
            for line in rules[page_num]:
                string_rendered = font.render(line, 1, pygame.Color('black'))
                intro_rect = string_rendered.get_rect()
                text_coord += 10
                intro_rect.top = text_coord
                intro_rect.x = 10
                text_coord += intro_rect.height
            '''


        update_screen()

        Button(self.buttons_group, 940, 650, 'next', (300, 50), fontsize=50)
        Button(self.buttons_group, 540, 650, 'prev', (300, 50), fontsize=50)
        Button(self.buttons_group, 50, 650, 'back', (300, 50), fontsize=50)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                if event.type == pygame.MOUSEMOTION:
                    self.cursor_group.update()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        for i, button in enumerate(self.buttons_group):
                            if button.rect.collidepoint(pygame.mouse.get_pos()):
                                button.press()
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        for i, button in enumerate(self.buttons_group):
                            if button.rect.collidepoint(pygame.mouse.get_pos()):
                                state = button.unpress()
                                if state:
                                    if i == 0:
                                        if page_num < 4:
                                            page_num += 1
                                    elif i == 1:
                                        if page_num > 0:
                                            page_num -= 1
                                    elif i == 2:
                                        self.start_screen()
                        self.buttons_group.update()

            update_screen()
            self.buttons_group.draw(self.screen)
            if pygame.mouse.get_focused():
                self.cursor_group.draw(self.screen)
            pygame.display.flip()

    def game_screen(self):
        pass

    def stop_threads(self):
        self.node.send('exit', self.node.ip)


def main():
    Game()


if __name__ == '__main__':
    main()
