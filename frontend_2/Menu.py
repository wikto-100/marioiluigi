import pygame
import Config
import sys
from Button import Button
import pygamepopup
from pygamepopup.menu_manager import MenuManager
import pygamepopup.components as popup

class Menu():
    def __init__(self, screen):
        self.screen = screen
        self.moves = ""
        pos_x = Config.SCREEN_SIZE + Config.LOG_SIZE//10
        pos_y = Config.SCREEN_SIZE//40
        width = (4*Config.LOG_SIZE)//5
        heigth = (31*Config.SCREEN_SIZE)//40
        rect = (pos_x,pos_y,width,heigth)
        
        self.log_rect = rect
        self.log_x = Config.SCREEN_SIZE+Config.LOG_SIZE//10+(8*Config.LOG_BUTTON_OFFSET)//5
        self.log_y = (8*Config.LOG_BUTTON_OFFSET)//5+Config.SCREEN_SIZE//40
        self.log = pygame.Surface((width-0.5*(self.log_x-Config.SCREEN_SIZE),heigth-2*self.log_y), pygame.SRCALPHA)
        self.log_font = pygame.font.SysFont(Config.FONT, 3*Config.SCREEN_SIZE//100)
        
        self.manager = MenuManager(screen)
        self.promotion = None

    def draw(self):
        n = Config.LOG_OFFSET
        pygame.draw.rect(self.screen, Config.GREY, (Config.SCREEN_SIZE+n,n,Config.LOG_SIZE-2*n,Config.SCREEN_SIZE-2*n))
        pygame.draw.rect(self.screen, Config.BLACK, self.log_rect, Config.LOG_BUTTON_OFFSET, 15)
        pygame.display.update()
        self.moves=""
        self.log.fill(Config.GREY)
    
    def menu_button(self, y, name):
        button_width = (4*Config.LOG_SIZE)//5
        button_heigth = (Config.SCREEN_SIZE)//15
        pos_x = Config.SCREEN_SIZE + Config.LOG_SIZE//10
        pos_y = (y*Config.SCREEN_SIZE)//40
        button = Button(self.screen, pos_x, pos_y, button_width, button_heigth, None, name, Config.LOG_BUTTON_OFFSET)
        button.draw()
        return button
    
    def update_log(self): 
        self.log.fill(Config.GREY)
        move_list = self.moves.split("\n")
        move_list = move_list[-Config.LOG_LIMIT:]
        y = 0
        for move in move_list:
            move = self.log_font.render(move, True, Config.BLACK)
            self.log.blit(move, (0, y))
            self.screen.blit(self.log, (self.log_x, self.log_y))
            y += 25
        pygame.display.flip()

    def promotion_menu(self, side):
        self.promotion = None
        if side == "w":
            pieces = ["B","N","R","Q"]
        else:
            pieces = ["b","n","r","q"]

        prom_menu = popup.InfoBox(
            "",
            [
                [
                    popup.ImageButton(
                        callback=lambda: self.set_promotion("B"),
                        size = ([1.5*Config.SQUARE_SIZE,1.5*Config.SQUARE_SIZE]),
                        margin = [0,0,0,30],
                        frame_background_path = Config.MENU_BACKGROUND,
                        image_path = "images/"+pieces[0]+".png"
                    ),
                    popup.ImageButton(
                        callback=lambda: self.set_promotion("N"),
                        size = ([1.5*Config.SQUARE_SIZE,1.5*Config.SQUARE_SIZE]),
                        margin = [0,0,0,15],
                        frame_background_path = Config.MENU_BACKGROUND,
                        image_path = "images/"+pieces[1]+".png"
                    ),
                    popup.ImageButton(
                        callback=lambda: self.set_promotion("R"),
                        size = ([1.5*Config.SQUARE_SIZE,1.5*Config.SQUARE_SIZE]),
                        margin = [0,15,0,0],
                        frame_background_path = Config.MENU_BACKGROUND,
                        image_path = "images/"+pieces[2]+".png"
                    ),
                    popup.ImageButton(
                        callback=lambda: self.set_promotion("Q"),
                        size = ([1.5*Config.SQUARE_SIZE,1.5*Config.SQUARE_SIZE]),
                        margin = [0,30,0,0],
                        frame_background_path = Config.MENU_BACKGROUND,
                        image_path = "images/"+pieces[3]+".png"
                    )
                ]
            ],
            width = 7.5*Config.SQUARE_SIZE,
            position = [0.25*Config.SQUARE_SIZE,2.5*Config.SQUARE_SIZE],
            has_close_button = False,
            background_path = Config.MENU_BACKGROUND,
        )
        self.manager.open_menu(prom_menu)
        self.manager.display()
        pygame.draw.rect(self.screen, Config.BLACK, pygame.Rect(0.15*Config.SQUARE_SIZE, 2.5*Config.SQUARE_SIZE, 7.7*Config.SQUARE_SIZE, 200+Config.SQUARE_SIZE), 10, 15)
        pygame.display.update()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:    
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.manager.click(event.button, event.pos)
                    if self.promotion != None:
                        self.manager.close_active_menu()
                        return self.promotion
    
    def set_promotion(self, piece):
        self.promotion = piece