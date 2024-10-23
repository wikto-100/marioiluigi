import pygame
import sys
import time
import Config
from Board import Board

def get_tile_pos(pos):
    x, y = pos
    row = y // Config.SQUARE_SIZE
    col = x // Config.SQUARE_SIZE
    return row, col

def get_tile(pos):
    return (8 - pos[0] , chr(pos[1] + 97))

def run():
    pygame.init()
    pygame.display.set_caption('Chess')
    running = True
    screen = pygame.display.set_mode((Config.SCREEN_SIZE, Config.SCREEN_SIZE))
    board = Board(screen)
    player = 'w'
    turn = 1
    selected_piece = None

    board.draw()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:

                if event.button == 1:
                    target = get_tile_pos(pygame.mouse.get_pos())
                    tile = get_tile(target)

                    if selected_piece != None:
                        move_accepted, player_move, winner = board.player_move(selected_piece, tile)
                        if winner is not None:
                            print("Game ended")
                            running = False
                        
                        if move_accepted == True and running:
                            time.sleep(0.3)
                            bot_move, winner = board.bot_move()
                            if winner is not None:
                                print("Game ended")
                                running = False
                            
                            print(str(turn)+".",player_move, bot_move)
                            turn+=1
                            selected_piece = None
                
                    else:
                        piece = board.get_piece(target[0], target[1])
                        if piece != '' and piece[0] == player:
                            selected_piece = (tile)
                            board.higlight(target)
                
                else:
                    selected_piece = None
                    board.draw()

    if winner == "draw":
        msg = "draw"
    elif winner == "player" and player == "w":
        msg = "WHITE WINS"
    else:
        msg = "BLACK WINS"

    font = pygame.font.SysFont("Arial", 100)
    txtsurf = font.render(msg, True, Config.TEXT_COLOR)
    screen.blit(txtsurf,((Config.SCREEN_SIZE - txtsurf.get_width()) // 2, (Config.SCREEN_SIZE - txtsurf.get_height()) // 2))
    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.QUIT:    
                pygame.quit()
                sys.exit()

run()