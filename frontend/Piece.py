import pygame
import Config

class Piece:
    PADDING = 15
    OUTLINE = 4

    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.calc_pos()

    def calc_pos(self):
        size = Config.SQUARE_SIZE
        self.x = size * self.col + size // 2
        self.y = size * self.row + size // 2

    def draw(self, screen):
        radius = Config.SQUARE_SIZE // 2 - self.PADDING
        pygame.draw.circle(screen, Config.GREY, (self.x, self.y), radius + self.OUTLINE)
        pygame.draw.circle(screen, self.color, (self.x, self.y), radius)