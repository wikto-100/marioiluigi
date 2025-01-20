import pygame
import time
import sys
import Config
from Board import Board
from playsound import playsound

class Game():
    def __init__(self, screen, menu, player, mode):
        self.screen = screen
        self.menu = menu
        self.player = player
        self.mode = mode
        self.reverse = False
        self.selected_piece = None
        self.turn = 1

    def get_tile_pos(self, pos):
        x, y = pos
        row = y // Config.SQUARE_SIZE
        col = x // Config.SQUARE_SIZE

        if self.reverse:
            row = 7 - row
            col = 7 - col
        return row, col

    def get_tile(self, pos):
        return (8 - pos[0] , chr(pos[1] + 97))

    def is_allowed(self, board, target):
        piece = board.get_piece(target[0], target[1])
        if piece != '' and piece.isupper() and self.player == 'w':
            return True
        elif piece != '' and piece.islower() and self.player == 'b':
            return True
        else:
            return False

    def handle_move(self, board, tile, target):
        if self.selected_piece != None:
            promotion = self.handle_promotion(target, tile, board)
            move_accepted, player_move, winner = board.player_move(self.selected_piece, tile, promotion)
            
            if move_accepted:
                if not self.reverse:
                    self.menu.moves += str(self.turn) + "." + player_move + " "
                else:
                    self.menu.moves += player_move + "\n"
                    self.turn+=1
                self.menu.update_log()

            if winner is not None:
                return winner
                            
            if move_accepted == True:
                time.sleep(0.6)
                bot_move, winner = board.bot_move()
                
                if not self.reverse:
                    self.menu.moves += bot_move + "\n"
                    self.turn+=1
                else:
                    self.menu.moves += str(self.turn) + "." + bot_move + " "
                self.menu.update_log()

                if winner is not None:
                    return winner
                                
                self.selected_piece = None
                    
        else:
            if self.is_allowed(board, target):
                self.selected_piece = (tile)
                board.higlight(target)

    def handle_promotion(self, target, tile, board):
        piece = str(self.selected_piece[0]) + self.selected_piece[1]
        if board.get_piece_from_string(piece).upper() != 'P':
            return None
        elif target[0] != 0 and target[0] != 7:
            return None
        
        if not board.allowed_move(self.selected_piece, tile):
            return None
        
        promotion = self.menu.promotion_menu(self.player)

        #promotion = input()
        return promotion

    def run(self):
        if self.player == 'b':
            self.reverse = True
        board = Board(self.screen, self.mode, self.reverse)
        surrender_button = self.menu.menu_button(36, 'Surrender')

        board.draw()
        if self.reverse:
            time.sleep(0.5)
            bot_move = board.bot_move()[0]
            self.menu.moves = str(self.turn) + "." + bot_move + " "
            self.menu.update_log()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:

                    if event.button == 1:
                        if surrender_button.button_rect.collidepoint(pygame.mouse.get_pos()):
                            playsound(Config.END_SOUND)
                            return 'opponent'
                        
                        target = self.get_tile_pos(pygame.mouse.get_pos())
                        tile = self.get_tile(target)
                        result = self.handle_move(board, tile, target)
                        if result is not None:
                            return result

                    else:
                        self.selected_piece = None
                        board.draw()