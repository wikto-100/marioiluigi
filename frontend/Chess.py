import pygame
import sys
import Config
from Board import Board

def get_tile_pos(pos):
    x, y = pos
    row = y // Config.SQUARE_SIZE
    col = x // Config.SQUARE_SIZE
    return row, col

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

                    if selected_piece != None:
                        print(selected_piece,"to",target)
                        move_accepted, winner, player_move, bot_move = board.move(selected_piece, target)
                        
                        if move_accepted == True:
                            selected_piece = None
                            print(str(turn)+".",player_move, bot_move)
                            turn+=1
                        if winner is not None:
                            print("Game ended")
                            running = False
                    else:
                        piece = board.state[target[0]][target[1]]
                        if piece != '' and piece[0] == player:
                            selected_piece = (target)
                            board.higlight(target)
                
                else:
                    selected_piece = None
                    board.draw()

    if winner == "black":
        msg = "BLACK WINS"
    elif winner == "white":
        msg = "WHITE WINS"
    else:
        msg = "DRAW"

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