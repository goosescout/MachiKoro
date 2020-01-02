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
    def __init__(self, group, x, y, text, size=None, font='data/ARCADECLASSIC.TTF', fontsize=100,
                 color=pygame.Color('black')):
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
        self.buttons_group.empty()

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
                                    if i == 0:
                                        pass
                                    elif i == 1:
                                        self.game_rules()
                                    elif i == 2:
                                        self.terminate()
                        self.buttons_group.update()

            update_screen()
            self.buttons_group.draw(self.screen)
            if pygame.mouse.get_focused():
                self.cursor_group.draw(self.screen)
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
                'is not compensated for the lost income. If payment is owed to multiple players',
                'at the same time, payment is processed in reverse player order (counter clockwise).'],
            4: ['Building New Establishments and Completing Landmarks',
                'To conclude a player’s turn, he or she may pay to construct one single',
                'Establishment OR pay to finish construction on a single Landmark by paying',
                'the cost shown on the lower left-hand corner of the card. Once constructed,',
                'an Establishment is taken from the supply and added to the player’s play area.']
        }

        def update_screen():
            background = pygame.transform.scale(load_image(
                'background.jfif'), (self.WIDTH, self.HEIGHT))
            self.screen.blit(background, (0, 0))

            back_image = pygame.transform.scale(load_image('button.png'), (1260, 730))
            self.screen.blit(back_image, (10, -20))
            font = pygame.font.Font(None, 45)
            text_coord = 10
            for line in rules[page_num]:
                string_rendered = font.render(line, 1, pygame.Color('black'))
                intro_rect = string_rendered.get_rect()
                text_coord += 7
                intro_rect.top = text_coord
                intro_rect.x = 25
                text_coord += intro_rect.height
                self.screen.blit(string_rendered, intro_rect)

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

    def mainloop(self):
        pass


def main():
    Game()


if __name__ == '__main__':
    main()
