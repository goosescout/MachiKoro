import pygame
import os
import sys
import threading
import socket

from utility import load_image


class MyThread(threading.Thread):
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs


    def run(self):
        self.func(*self.args, **self.kwargs)


class Notification(pygame.sprite.Sprite):
    def __init__(self, group, text, font='data/DisposableDroidBB.ttf', fontsize=50, color=pygame.Color('black')):
        super().__init__(group)
        self.image = pygame.transform.scale(load_image('button.png'), (880, 320))
        self.rect = self.image.get_rect()
        self.rect.x = 200
        self.rect.y = 200

        font = pygame.font.Font(font, fontsize)
        shift = 280 // (len(text) + 1 )
        for i, line in enumerate(text):
            line = font.render(line, 1, color)
            self.image.blit(line, (20, shift * (i + 1)))

        Button(group, 910, 450, 'close', size=(150, 50), fontsize=50)


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

    def update(self):
        self.unpress()


class Game:
    def __init__(self):
        pygame.init()
        pygame.mouse.set_visible(False)
        self.WIDTH = 1280
        self.HEIGHT = 720
        self.FPS = 30
        self.clock = pygame.time.Clock()

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
        searching_for_game = False
        game_found = [False]
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
                                state = button.unpress()
                                if state:
                                    if i == 0:
                                        searching_for_game = True
                                        stop = [False]
                                        Notification(self.notification_group, ('searching for the game...',))

                                        def search(stop, game_found):
                                            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                                            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
                                            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)
                                            s.bind(('0.0.0.0', 11719))
                                            while True:
                                                message = s.recv(128).decode('utf-8')
                                                if message.startswith('searching for players'):
                                                    game_found[0] = True
                                                    stop[0] = True
                                                if stop[0]:
                                                    break

                                        thread = MyThread(search, stop, game_found)
                                        thread.start()
                                    elif i == 1:
                                        pass
                                    elif i == 2:
                                        self.notification_group.empty()
                                        self.start_screen()
                        for elem in self.notification_group:
                            if isinstance(elem, Button):
                                    if elem.unpress():
                                        if elem.rect.collidepoint(pygame.mouse.get_pos()):
                                            self.notification_group.empty()
                                            stop = True
                                            searching_for_game = False
                                            game_found = [False]
                        self.buttons_group.update()

            update_screen()
            self.buttons_group.draw(self.screen)
            self.notification_group.draw(self.screen)
            if searching_for_game:
                if counter % 10 == 0:
                    self.notification_group.empty()
                    Notification(self.notification_group, ('searching for the game' + "." * (counter % 3 + 1),))
            if game_found[0]:
                searching_for_game = False
                if counter % 10 == 0:
                    self.notification_group.empty()
                    Notification(self.notification_group, ('game is ready', 'connecting' + "." * (counter % 3 + 1)))
            if pygame.mouse.get_focused():
                self.cursor_group.draw(self.screen)
            self.clock.tick(self.FPS)
            counter += 1
            pygame.display.flip()

    def mainloop(self):
        pass


def main():
    Game()


if __name__ == '__main__':
    main()
