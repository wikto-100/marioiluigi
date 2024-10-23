import pygame
import Config
import PlaceholderRules
import PlaceholderBot
from Piece import Piece

class Board:
    def __init__(self, screen):
        self.screen = screen
        self.state = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR'

    def get_piece(self, x, y):
        row = self.state.split('/')[x]
        col = 0
        for tile in row:

            if col == y and not tile.isdigit():
                piece = tile
                if piece.isupper():
                    return 'w' + tile.lower()
                else:
                    return 'b' + tile
            else:
                if tile.isdigit():
                    col += int(tile)
                else:
                    col+=1

        return ''

    def draw(self):
        self.draw_board()

        row_num = 0
        for row in self.state.split('/'):
            col = 0
            for tile in row:
                if tile.isdigit():
                    col += int(tile)
                else:
                    if tile.isupper():
                        piece = Piece(row_num, col, Config.WHITE)
                    else:
                        piece = Piece(row_num, col, Config.BLACK)
                    piece.draw(self.screen)
                    col+=1
            row_num +=1
        pygame.display.flip()

    def draw_board(self):
        self.screen.fill(Config.DARK)
        size = Config.SQUARE_SIZE
        for row in range(Config.BOARD_SIZE):
            for col in range(row % 2, Config.BOARD_SIZE, 2):
                pygame.draw.rect(self.screen, Config.LIGHT, (row * size, col * size, size, size))

    def higlight(self, tile):
        size = Config.SQUARE_SIZE
        row = tile[0]
        col = tile[1]
        pygame.draw.rect(self.screen, Config.HIGHLIGHT, (col * size, row * size, size, size))
        
        p = self.get_piece(row, col)
        if p != '':
            if p[0] == 'w':
                piece = Piece(row, col, Config.WHITE)
            else:
                piece = Piece(row, col, Config.BLACK)

        piece.draw(self.screen)
        pygame.display.flip()
        
    def player_move(self, source, target):
        print(source, target)
        move = str(source[0]) + source[1]+ str(target[0]) + target[1]
        if not PlaceholderRules.canDoMove(move, self.state):
            print("illegal move")
            return False, '', None

        new_state = PlaceholderRules.getAppliedMove(self.state, move)
        self.state = new_state
        self.draw()
        move = self.to_chess_notation(move)

        winner = None
        lost = PlaceholderRules.isLostCondition(self.state)
        if lost:
            winner = "player"
        elif lost == "draw":
            winner = "draw"

        return True, move, winner
    
    def bot_move(self):
        move = PlaceholderBot.get_bot_move(self.state)        
        new_state = PlaceholderRules.getAppliedMove(self.state, move)
        self.state = new_state
        self.draw()
        move = self.to_chess_notation(move)

        winner = None
        lost = PlaceholderRules.isLostCondition(self.state)
        if lost:
            winner = "opponent"
        elif lost == "draw":
            winner = "draw"

        return move, winner
    
    def to_chess_notation(self, move):
        if move == '2e4e':
            return 'Pe4'
        else:
            return 'Pe5'