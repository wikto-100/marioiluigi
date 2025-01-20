import pygame
import Config

class Button:
    def __init__(self, screen, x, y, width, height, image, text, offset=15):
        self.screen = screen
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.image = image
        self.text = text
        self.offset = offset
        self.button_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.button_font = pygame.font.SysFont(Config.FONT, 30)

    def draw(self):
        pygame.draw.rect(self.screen, Config.GREY, self.button_rect, 0, 15)
        pygame.draw.rect(self.screen, Config.BLACK, self.button_rect, self.offset, 15)
        
        if self.image is not None:
            img = pygame.image.load(self.image).convert_alpha()
            scaled_image = pygame.transform.scale(img, (self.width-self.offset, self.height-self.offset))
            self.screen.blit(scaled_image, scaled_image.get_rect(center = self.button_rect.center))
        if self.text is not None:
            text = self.button_font.render(self.text, True, Config.TEXT_COLOR)
            text_rect = text.get_rect(center=(self.x+self.width/2, self.y+self.height/2-4))
            self.screen.blit(text, text_rect)

        pygame.display.update()