import pygame
import time
import Config
import PlaceholderRules
import PlaceholderBot
from Piece import Piece

class Board:
    def __init__(self, screen):
        self.screen = screen
        self.state = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
            [''  ,  '' ,  '' ,  '' , ''  , ''  ,  '' , ''  ],
            [''  ,  '' ,  '' ,  '' , ''  , ''  ,  '' , ''  ],
            [''  ,  '' ,  '' ,  '' , ''  , ''  ,  '' , ''  ],
            [''  ,  '' ,  '' ,  '' , ''  , ''  ,  '' , ''  ],
            ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR'],
        ]

    def draw(self):
        self.draw_board()
        for row in range(Config.BOARD_SIZE):
            for col in range(Config.BOARD_SIZE):
                if self.state[row][col] == '':
                    piece = 0
                else:
                    if self.state[row][col][0] == 'w':
                        piece = Piece(row, col, Config.WHITE)
                    else:
                        piece = Piece(row, col, Config.BLACK)
                if piece != 0:
                    piece.draw(self.screen)
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
        
        if self.state[row][col] == '':
                piece = 0
        else:
            if self.state[row][col][0] == 'w':
                piece = Piece(row, col, Config.WHITE)
            else:
                piece = Piece(row, col, Config.BLACK)
            if piece != 0:
                piece.draw(self.screen)
        pygame.display.flip()

    #move (source, target) -> (czy zaakceptowany ruch, czy koniec gry, ruch gracza, ruch bota, wynik)
    #Rules.try_move (source, target, state) -> (czy zaakceptowany ruch, czy koniec gry, nowy stan planszy, ruch gracza, wynik)
    #Bot.move (state) -> (czy koniec gry, nowy stan planszy, ruch bota, wynik)
    def move(self, source, target):
        move_result = PlaceholderRules.try_move(source, target, self.state)

        if move_result[0] == True:
            winner = move_result[1]
            player_move = move_result[3]
            self.state = move_result[2]
            self.draw()
        else:
            print("illegal move")
            return False, None, "", ""
        
        if move_result[1] is not None:
            return True, winner, player_move, "-"
        else:
            time.sleep(0.3)
            bot_move_result = PlaceholderBot.move(self.state)
            winner = bot_move_result[0]
            bot_move = bot_move_result[2]
            self.state = bot_move_result[1]
            self.draw()
            return True, winner, player_move, bot_move