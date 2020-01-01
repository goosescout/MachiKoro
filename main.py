import pygame
import os
import sys

from utility import load_image


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
    def __init__(self, group, x, y, text, size=None, font='data/ARCADECLASSIC.TTF', fontsize=100, color=pygame.Color('black')):
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

        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))

        self.cursor_group = pygame.sprite.Group()
        self.buttons_group = pygame.sprite.Group()
        self.cursor = Cursor(self.cursor_group)

        self.start_screen()
        self.mainloop()

    def terminate(self):
        pygame.quit()
        sys.exit()

    def start_screen(self):
        def update_screen():
            background = pygame.transform.scale(load_image(
                'background.jfif'), (self.WIDTH, self.HEIGHT))
            self.screen.blit(background, (0, 0))
            logo = pygame.transform.scale(load_image('logo.png'), (880, 200))
            self.screen.blit(logo, (200, 50))

        update_screen()

        Button(self.buttons_group, 440, 300, 'play')
        Button(self.buttons_group, 440, 420, 'rules')
        Button(self.buttons_group, 440, 540, 'exit')

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
                                    print(i)
                        self.buttons_group.update()

            update_screen()
            self.buttons_group.draw(self.screen)
            if pygame.mouse.get_focused():
                self.cursor_group.draw(self.screen)
            pygame.display.flip()

    def mainloop(self):
        pass


def main():
    Game()


if __name__ == '__main__':
    main()
