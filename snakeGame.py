import pygame
import random
import queue
import threading
import time
from pygame.locals import *

class Snake:
    # Initial snake settings
    STARTX = 8
    STARTY = 10
    STARTLENGTH = 3

    # Directions
    WAIT = [0, 0]
    LEFT = [0, -1]
    RIGHT = [0, 1]
    UP = [1, -1]
    DOWN = [1, 1]

    # Initialize snake properties
    def __init__(self, tile):
        self.length = self.STARTLENGTH

        self.head_img = pygame.image.load("images/head.png")
        self.head_img = pygame.transform.scale(self.head_img, (tile, tile))
        self.head_position = [self.STARTX, self.STARTY]
        self.head_old = self.head_position[:]

        self.body_img = pygame.image.load("images/body.png")
        self.body_img = pygame.transform.scale(self.body_img, (tile, tile))
        self.body_position = []
        self.body_position.append(self.head_position[:])
        for i in range(1, self.STARTLENGTH+1):
            body_part = [self.head_position[0] - i, self.head_position[1]]
            self.body_position.append(body_part)
        self.tail_old = self.body_position[-1]

        self.skull_img = pygame.image.load("images/dead.png")
        self.skull_img = pygame.transform.scale(self.skull_img, (tile, tile))

        self.direction = self.WAIT
        self.dead = False

    def turn_left(self):
        self.direction = self.LEFT

    def turn_right(self):
        self.direction = self.RIGHT

    def turn_up(self):
        self.direction = self.UP

    def turn_down(self):
        self.direction = self.DOWN

    # Update snake head and body positions based on chosen direction
    def move(self, screen_size, cookie):
        if self.direction != self.WAIT:
            coord = self.direction[0]
            unit = self.direction[1]
            new_head = self.head_position[coord] + unit
            check_position = self.head_position[:]
            check_position[coord] = new_head

            # Check if head hits the border or hits its own body
            if new_head < 1 or new_head > screen_size - 2 or check_position in self.body_position:
                self.dead = True
            else:
                # Update snake head position
                self.head_position[coord] = new_head

                # If snake eats cookie, make a new cookie
                # Extend body length by adding new head to current body
                if self.head_position == cookie:
                    new_body = [self.head_position[:]] + self.body_position[:]
                    self.body_position = new_body
                    return True
                else:
                    # Update snake body
                    # Remove last body part and append remaining body
                    self.tail_old = self.body_position.pop()
                    new_body = [self.head_position[:]] + self.body_position[:]
                    self.body_position = new_body

    # Draw snake head and snake body
    def draw(self, tile, screen):
        for i in range(len(self.body_position)):
            # Draw head first
            if i == 0:
                head_tile = (self.head_position[0] * tile, self.head_position[1] * tile)
                screen.blit(self.head_img, head_tile)
            # Draw body parts
            else:
                body_tile = (self.body_position[i][0] * tile, self.body_position[i][1] * tile)
                screen.blit(self.body_img, body_tile)

    # Erase previous snake head and last body part
    def erase(self, cmap, tile, screen):
        # Erase head
        hx = self.head_old[0]
        hy = self.head_old[1]
        head_tile = (hx * tile, hy * tile, tile, tile)
        hcolor_index = (hx + hy + 1) % 2
        screen.fill(cmap[hcolor_index], head_tile)

        # Erase last body part
        tx = self.tail_old[0]
        ty = self.tail_old[1]
        tail_tile = (tx * tile, ty * tile, tile, tile)
        tcolor_index = (tx + ty + 1) % 2
        screen.fill(cmap[tcolor_index], tail_tile)

    def rip(self, tile, screen):
        skull_tile = (self.head_position[0] * tile, self.head_position[1] * tile)
        screen.blit(self.skull_img, skull_tile)

class Cookie:

    STARTX = 12
    STARTY = 10
    EATEN = 0

    # Initialize cookie properties
    def __init__(self, tile):
        self.cookie_img = pygame.image.load("images/cookie.png")
        self.cookie_img = pygame.transform.scale(self.cookie_img, (tile, tile))

        self.cookie_eaten = self.EATEN
        self.cookie_position = [self.STARTX, self.STARTY]

    def new(self, screen, snake):
        self.cookie_eaten += 1
        x = random.randint(2, screen - 3)
        y = random.randint(2, screen - 3)
        new_cookie = [x, y]

        while new_cookie in snake:
            x = random.randint(2, screen - 3)
            y = random.randint(2, screen - 3)
            new_cookie = [x, y]

        self.cookie_position = new_cookie

    def draw(self, tile, screen):
        cookie_tile = (self.cookie_position[0] * tile, self.cookie_position[1] * tile)
        screen.blit(self.cookie_img, cookie_tile)

class App:
    # Display screen settings
    TILESIZE = 30
    SCREENSIZE = 20

    # Color map = [White, Grey, Blue]
    WHITE = 0
    GREY = 1
    BLUE = 2
    RED = 3
    CMAP = [(255,255,255), (200,200,200), (0, 204, 255), (255,0,0)]

    # Game state
    RUN = 1
    STOP = 0

    def __init__(self):
        self._running = True
        self.screen = None
        self.state = None

    def draw_background(self):
        for row in range(self.SCREENSIZE):
            colorIndex = row % 2
            if row == 0 or row == (self.SCREENSIZE - 1):
                edge = ((0, row * self.TILESIZE), (self.SCREENSIZE * self.TILESIZE, self.TILESIZE))
                self.screen.fill(self.CMAP[2], edge)
            else:
                for col in range(self.SCREENSIZE):
                    tile = (col * self.TILESIZE , row * self.TILESIZE , self.TILESIZE , self.TILESIZE)
                    if col == 0 or col == (self.SCREENSIZE - 1):
                        edge = (col * self.TILESIZE, 0, self.TILESIZE, self.SCREENSIZE * self.TILESIZE)
                        self.screen.fill(self.CMAP[2], edge)
                    else:
                        self.screen.fill(self.CMAP[colorIndex], tile)
                        colorIndex = (colorIndex + 1) % 2
        pygame.display.update()

    def draw_title(self, text):
        font_path = "SnakeChan.ttf"
        font_size = self.TILESIZE
        font_obj = pygame.font.SysFont(font_path, font_size)
        color = self.CMAP[self.WHITE]
        title = font_obj.render(text, True, color)
        x = int(self.SCREENSIZE * self.TILESIZE/2)
        y = int(self.TILESIZE/2)
        rect = title.get_rect(center=(x,y))
        self.screen.blit(title, rect)
        pygame.display.update()

    def draw_score(self, text, score):
        font_path = "SnakeChan.ttf"
        font_size = self.TILESIZE
        font_obj = pygame.font.SysFont(font_path, font_size)
        color = self.CMAP[self.WHITE]
        whole_text = text + str(score)
        title = font_obj.render(whole_text, True, color)
        x = int(self.SCREENSIZE * self.TILESIZE/2)
        y = int((self.SCREENSIZE * self.TILESIZE) - self.TILESIZE/2)
        rect = title.get_rect(center=(x,y))
        self.screen.fill(self.CMAP[self.BLUE], rect)
        self.screen.blit(title, rect)
        pygame.display.update()

    def draw_end(self, text):
        font_path = "SnakeChan.ttf"
        font_size = self.TILESIZE * 3
        font_obj = pygame.font.SysFont(font_path, font_size)
        color = self.CMAP[self.RED]
        title = font_obj.render(text, True, color)
        x = int(self.SCREENSIZE * self.TILESIZE/2)
        y = int((self.SCREENSIZE * self.TILESIZE/2))
        rect = title.get_rect(center=(x,y))
        self.screen.blit(title, rect)
        pygame.display.update()


    def on_init(self):
        pygame.init()
        pygame.font.init()
        self._running = True

        self.screen = pygame.display.set_mode((self.TILESIZE * self.SCREENSIZE , self.TILESIZE * self.SCREENSIZE))
        self.draw_background()
        self.draw_title("S N A K E   G A M E")
        self.snake = Snake(self.TILESIZE)
        self.cookie = Cookie(self.TILESIZE)
        self.state = self.RUN

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False

        elif event.type == KEYDOWN:
            if self.state == self.RUN:
                if event.key == K_ESCAPE:
                    self._running = False

                if event.key == K_LEFT:
                    self.snake.turn_left()

                if event.key == K_RIGHT:
                    self.snake.turn_right()

                if event.key == K_UP:
                    self.snake.turn_up()

                if event.key == K_DOWN:
                    self.snake.turn_down()

    def on_loop(self):
        if self.snake.dead:
            self.state == self.STOP
        else:
            ate_cookie = self.snake.move(self.SCREENSIZE, self.cookie.cookie_position)
            if ate_cookie: self.cookie.new(self.SCREENSIZE, self.snake.body_position)
        pass

    def on_render(self):
        if self.snake.dead:
            self.snake.rip(self.TILESIZE, self.screen)
            self.draw_end("G A M E  O V E R")
        else:
            self.snake.erase(self.CMAP, self.TILESIZE, self.screen)
            self.snake.draw(self.TILESIZE, self.screen)
            self.cookie.draw(self.TILESIZE, self.screen)
            self.draw_score("S C O R E : ", self.cookie.cookie_eaten)

        pygame.display.flip()

    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):
        if self.on_init() == False:
            self._running = False

        while(self._running):
            pygame.event.pump()
            key = pygame.key.get_pressed()

            if (key[K_LEFT]):
                self.snake.turn_left()

            if (key[K_RIGHT]):
                self.snake.turn_right()

            if (key[K_UP]):
                self.snake.turn_up()

            if (key[K_DOWN]):
                self.snake.turn_down()

            if (key[K_ESCAPE]):
                self._running = False

            self.on_loop()
            self.on_render()
            time.sleep(0.15);

        self.on_cleanup()

if __name__ == "__main__" :
    leggo = App()
    leggo.on_execute()
