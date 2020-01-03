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
                'background.jfif'), (self.WIDTH, self.HEIGHT))
            self.screen.blit(background, (0, 0))
            logo = pygame.transform.scale(load_image('logo.png'), (880, 200))
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
                                        pass
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
                'background.jfif'), (self.WIDTH, self.HEIGHT))
            self.screen.blit(background, (0, 0))
            logo = pygame.transform.scale(load_image('logo.png'), (880, 200))
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
                                        Notification(self.notification_group, ('searching for the game.',))
                                        thread = MyThread(self.node.await_recieve, ['searching for players', 'message', [[flags, 'game_found', True], [flags, 'game_host', '__VALUE__'], [flags, 'searching_for_game', False]], 1])
                                        thread.start()
                                    elif i == 1:
                                        Notification(self.notification_group, ('searching for players (1/4).', self.node.ip), add_button='start')
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
                    for elem in self.notification_group:
                        if isinstance(elem, Notification):
                            elem.update(text=('searching for the game' + "." * abs(counter % 3 - 3),))
            if flags['game_found']:
                if not flags['game_connected']:
                    self.stop_threads()
                    flags['game_connected'] = True
                    self.node.send('connect', flags['game_host']['ip'])
                    thread = MyThread(self.node.await_recieve, ['search stopped', 'message', [[flags, 'game_host', {'ip': -1}], [flags, 'game_found', False], [flags, 'searching_for_game', False], [flags, 'game_connected', False], [flags, 'game_closed', True]], 1])
                    thread.start()
                if counter % 20 == 0:
                    for elem in self.notification_group:
                        if isinstance(elem, Notification):
                            elem.update(text=('game is ready', f"game host: {flags['game_host']['ip']}", 'connecting' + "." * abs(counter % 3 - 3)))
            if flags['game_closed']:
                for elem in self.notification_group:
                    if isinstance(elem, Notification):
                        elem.update(text=('host has left the game', 'please restart search'))
                if thread.is_alive():
                    self.stop_threads()
            if flags['searching_for_players']:
                print(thread.is_alive())
                self.node.send('searching for players')
                players = [elem['ip'] for elem in flags['players']]
                if counter % 20 == 0:
                    for elem in self.notification_group:
                        if isinstance(elem, Notification):
                            elem.update(text=[f'searching for players ({len(players)}/4)' + "." * abs(counter % 3 - 3)] + players)
                if len(players) == 4:
                    flags['searching_for_players'] = False
                    print('start game')

            self.notification_group.draw(self.screen)
            if pygame.mouse.get_focused():
                self.cursor_group.draw(self.screen)
            self.clock.tick(self.FPS)
            counter += 1
            pygame.display.flip()

    def game_screen(self):
        pass

    def stop_threads(self):
        self.node.send('exit', self.node.ip)


def main():
    Game()


if __name__ == '__main__':
    main()
