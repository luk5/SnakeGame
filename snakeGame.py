import pygame
import random
import queue
import threading
import time
from pygame.locals import *

class App:
    # Initial snake settings
    STARTX = 10
    STARTY = 10
    STARTLENGTH = 3

    # Display screen settings
    TILESIZE = 30
    SCREENSIZE = 20

    # Color map = [White, Grey, Blue, Green]
    WHITE = 0
    GREY = 1
    BLUE = 2
    GREEN = 3
    CMAP = [(255,255,255), (200,200,200), (0, 204, 255), (153, 204, 0)]

    # Directions
    LEFT = [0, -1]
    RIGHT = [0, 1]
    UP = [1, -1]
    DOWN = [1, 1]

    RUNNING = 1
    STOPPED = 0

    def __init__(self, ready=None):
        self.running = True
        self.screen = None
        self.clock = None
        self.ready = ready
        self.cookie_position = []
        self.snake_size = None
        self.snake_head = None
        self.head_position = []
        self.snake_body = None
        self.body_position = []
        self.direction = []
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

    def draw_cookie(self):
        # Make sure not on snake
        cookie = pygame.image.load("images/cookie.png")
        cookie = pygame.transform.scale(cookie, (self.TILESIZE, self.TILESIZE))

        x = random.randint(1, self.SCREENSIZE - 2)
        while x == self.head_position[0]:
            x = random.randint(1, self.SCREENSIZE - 2)

        y = random.randint(1, self.SCREENSIZE - 2)
        while y == self.head_position[1]:
            y = random.randint(1, self.SCREENSIZE - 2)

        self.cookie_position = [x, y]
        cookie_positionition = ((x * self.TILESIZE), (y * self.TILESIZE))
        self.screen.blit(cookie, cookie_positionition)
        pygame.display.update()

    def draw_snake_body(self):
        self.snake_body = pygame.image.load("images/body.png")
        self.snake_body = pygame.transform.scale(self.snake_body, (self.TILESIZE, self.TILESIZE))

        for i in range(1, len(self.body_position)):
            rect = pygame.Rect(self.body_position[i][0] * self.TILESIZE, self.body_position[i][1] * self.TILESIZE, self.TILESIZE, self.TILESIZE)
            #pygame.draw.rect(self.screen, self.CMAP[3], rect)
            self.screen.blit(self.snake_body, rect)

    def draw_snake(self):
        # Always starts at same position
        # Draw snake head
        self.snake_head = pygame.image.load("images/head.png")
        self.snake_head = pygame.transform.scale(self.snake_head, (self.TILESIZE, self.TILESIZE))
        rect = (self.head_position[0] * self.TILESIZE, self.head_position[1] * self.TILESIZE)
        #self.screen.fill(self.CMAP[3], (self.head_position[0] * self.TILESIZE, self.head_position[1] * self.TILESIZE, self.TILESIZE, self.TILESIZE))
        self.screen.blit(self.snake_head, rect)

        # Add head to body list
        self.body_position.append(self.head_position[:])
        # Add body parts to body list
        for i in range(1, self.STARTLENGTH+1):
            bod = [self.head_position[0] - i, self.head_position[1]]
            self.body_position.append(bod)

        self.draw_snake_body()
        pygame.display.update()

    def draw_text(self, text, size, color, x, y):
        fontPath = "SnakeChan.ttf"
        fontObj = pygame.font.SysFont(fontPath, size)
        title = fontObj.render(text, True, color)
        rect = title.get_rect(center=(x,y))
        self.screen.blit(title, rect)
        pygame.display.update()

    def setup(self):
        pygame.init()
        pygame.font.init()
        self.running = True

        self.length = self.STARTLENGTH

        self.head_position = [self.STARTX, self.STARTY]
        self.headImage = pygame.image.load("images/head.png")
        self.headImage = pygame.transform.scale(self.headImage, (self.TILESIZE, self.TILESIZE))

        self.bodyImage = pygame.image.load("images/body.png")
        self.bodyImage = pygame.transform.scale(self.bodyImage, (self.TILESIZE, self.TILESIZE))

        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.TILESIZE * self.SCREENSIZE , self.TILESIZE * self.SCREENSIZE))
        self.draw_background()
        self.draw_text("S N A K E   G A M E", self.TILESIZE, (255,255,255), int(self.SCREENSIZE * self.TILESIZE/2), int(self.TILESIZE/2))
        self.draw_snake()
        self.draw_cookie()
        self.state = self.RUNNING

    def game_over(self):
        skull = pygame.image.load("images/dead.png")
        skull = pygame.transform.scale(skull, (self.TILESIZE, self.TILESIZE))
        self.screen.blit(skull,(self.head_position[0] * self.TILESIZE, self.head_position[1] * self.TILESIZE))
        self.state = self.STOPPED
        pygame.display.update()

    #TODO: can still move after death
    def game_over_thread(self):
        self.clock.tick(6)
        t = threading.Thread(target=self.game_over, args=())
        t.start()
        ready.wait()

    def move_snake(self, coord, unit):
        newPos = self.head_position[coord] + (unit * 1)
        checkPos = self.head_position[:]
        checkPos[coord] = newPos
        if newPos < 1 or newPos > self.SCREENSIZE - 2 or checkPos in self.body_position:
            self.direction = []
            self.game_over_thread()
        else:
            # Erase previous snake head
            bgx = self.head_position[0]
            bgy = self.head_position[1]
            tile = (bgx * self.TILESIZE, bgy * self.TILESIZE, self.TILESIZE, self.TILESIZE)
            colorIndex = (bgx +bgy + 1) % 2
            self.screen.fill(self.CMAP[colorIndex], tile)

            # Draw new snake head
            self.head_position[coord] = newPos
            self.screen.blit(self.snake_head,(self.head_position[0] * self.TILESIZE, self.head_position[1] * self.TILESIZE))

            # If snake eats cookie, make a new cookie
            if self.head_position == self.cookie_position:
                self.draw_cookie()
                newbody = [self.head_position[:]] + self.body_position[:]
                self.body_position = newbody
                self.draw_snake_body()

            else:
                # Draw new snake body
                fill = self.body_position.pop()
                newbody = [self.head_position[:]] + self.body_position[:]
                self.body_position = newbody
                self.draw_snake_body()

                # Erase snake tail
                colorIndex = (fill[0] + fill[1] + 1) % 2
                tile = (fill[0] * self.TILESIZE, fill[1] * self.TILESIZE, self.TILESIZE, self.TILESIZE)
                self.screen.fill(self.CMAP[colorIndex], tile)

            pygame.display.update()
            self.ready.set()

    def move_snake_thread(self):
        self.clock.tick(5)
        t = threading.Thread(target=self.move_snake, args=(self.direction[0], self.direction[1]))
        t.start()
        ready.wait()

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False

        elif event.type == KEYDOWN:
            if self.state == self.RUNNING:
                if event.key == K_ESCAPE:
                    self.running = False

                if event.key == K_LEFT and self.direction != self.LEFT:
                    self.direction = self.LEFT
                    self.move_snake_thread()

                if event.key == K_RIGHT and self.direction != self.RIGHT:
                    self.direction = self.RIGHT
                    self.move_snake_thread()

                if event.key == K_UP and self.direction != self.UP:
                    self.direction = self.UP
                    self.move_snake_thread()

                if event.key == K_DOWN and self.direction != self.DOWN:
                    self.direction = self.DOWN
                    self.move_snake_thread()
            else:
                pass
                # Do something

    def cleanup(self):
        pygame.quit()

    def start(self):
        if self.setup() == False:
            self.running = False

        while(self.running):
            for event in pygame.event.get():
                self.on_event(event)

            if len(self.direction) != 0 and self.ready.is_set():
                self.move_snake_thread()

        self.cleanup()

if __name__ == "__main__" :
    ready = threading.Event()
    leggo = App(ready)
    leggo.start()
