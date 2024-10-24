import pygame
import Config

class Piece:

    def __init__(self, row, col, type):
        self.row = row
        self.col = col
        self.type =type
        self.calc_pos()

    def calc_pos(self):
        size = Config.SQUARE_SIZE
        self.x = size * self.col + size // 2
        self.y = size * self.row + size // 2

    def draw(self, screen):
        size = Config.SQUARE_SIZE
        image = pygame.image.load("images/" + self.type + ".png").convert_alpha()
        scaled_image = pygame.transform.scale(image, (size, size))
        screen.blit(scaled_image, (self.col * size, self.row * size))