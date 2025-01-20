import pygame
import pygamepopup
import sys
import Config
from Board import Board
from Button import Button
from Game import Game
from Menu import Menu
from playsound import playsound

def choose_side(screen):
    board = Board(screen)
    board.draw_board()

    square_size = Config.SQUARE_SIZE
    button_size = (3*square_size)//2
    pos_x1 = (9*square_size)//4
    pos_x2 = (17*square_size)//4
    pos_y = (13*square_size)//4

    white_button = Button(screen, pos_x1, pos_y, button_size, button_size, "images/K.png", None)
    white_button.draw()
    black_button = Button(screen, pos_x2, pos_y, button_size, button_size, "images/k.png", None)
    black_button.draw() 

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                if white_button.button_rect.collidepoint(pos):
                    return 'w'
                elif black_button.button_rect.collidepoint(pos):
                    return 'b'

def choose_mode(screen):
    board = Board(screen)
    board.draw_board()

    square_size = Config.SQUARE_SIZE
    button_width = square_size*3.5
    button_height = square_size*0.75
    pos_x = (9*square_size)//4
    pos_y1 = (25*square_size)//8
    pos_y2 = pos_y1 + square_size

    mode1_button = Button(screen, pos_x, pos_y1, button_width, button_height, None, "Classic")
    mode1_button.draw()
    mode2_button = Button(screen, pos_x, pos_y2, button_width, button_height, None, "960")
    mode2_button.draw() 

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                if mode1_button.button_rect.collidepoint(pos):
                    return 'classic'
                elif mode2_button.button_rect.collidepoint(pos):
                    return '960'

def game():
    pygame.init()
    pygamepopup.init()
    pygame.display.set_caption('Chess')
    screen = pygame.display.set_mode((Config.SCREEN_SIZE + Config.LOG_SIZE, Config.SCREEN_SIZE))
    menu = Menu(screen)
    font = pygame.font.SysFont(Config.FONT, Config.SQUARE_SIZE)
    waiting = False

    while True:
        menu.draw()
        mode = choose_mode(screen)
        player = choose_side(screen)
        playsound(Config.START_SOUND)
        game = Game(screen, menu, player, mode)
        result = game.run()

        if result == "draw":
            msg = "DRAW"
        elif (result == "player" and player == "w") or (result == "opponent" and player == 'b'):
            msg = "WHITE WINS"
        else:
            msg = "BLACK WINS"

        txtsurf = font.render(msg, True, Config.HIGHLIGHT)
        screen.blit(txtsurf,((Config.SCREEN_SIZE - txtsurf.get_width()) // 2, (Config.SCREEN_SIZE - txtsurf.get_height()) // 2))
        pygame.display.update()
        waiting = True
        new_game_button = menu.menu_button(33,"New Game")

        while waiting:
            for event in pygame.event.get():

                if event.type == pygame.QUIT:    
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if new_game_button.button_rect.collidepoint(pygame.mouse.get_pos()):
                        waiting = False

game()