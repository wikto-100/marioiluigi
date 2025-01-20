import pygame
import random
import Config
from Piece import Piece
from Bot import Bot
from engine import chess_lib
from playsound import playsound

class Board:
    def __init__(self, screen, mode = 'classic', reverse = False):
        self.screen = screen
        self.reverse = reverse
        self.bot = Bot("marioiluigi/machine_learning/models/trained_model.pth")
        if mode == 'classic':
            self.state = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1' 
            #self.state = "3k4/3P4/4K3/8/8/8/8/8 w - - 0 1" #pat
            #self.state = 'rnbqkbnr/PppppppP/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1' #promocja biały
            #self.state = 'rnbqkbnr/pppppppp/8/8/8/8/pPPPPPPp/RNBQKBNR w KQkq - 0 1' #promocja czarny
            #self.state = 'k7/7Q/1Q6/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1' #mat
            #self.state = 'k7/8/1K6/8/8/4R3/8/8 w - - 0 1' #mat w 1
        else:
            pieces = ['r','n','b','q','k','b','n','r']
            random.shuffle(pieces)
            pieces = ''.join(pieces)
            state = pieces + '/pppppppp/8/8/8/8/PPPPPPPP/' + pieces.upper() + ' w - - 0 1'
            self.state = state

    def get_piece(self, x, y):
        row = self.state.split('/')[x]
        col = 0
        for tile in row:

            if col == y and not tile.isdigit():
                return tile
            else:
                if tile.isdigit():
                    col += int(tile)
                else:
                    col+=1

        return ''
    
    def get_piece_from_string(self, name):
        x = name[0]
        y = name[1]
        x1 = 8 - int(x)
        y1 = ord(y) - 97
        return self.get_piece(x1,y1)

    def draw(self):
        self.draw_board()
        state = self.state.split(" ")[0]
        if self.reverse:
            state = state[::-1]

        row_num = 0
        for row in state.split('/'):
            col = 0
            for tile in row:
                if tile.isdigit():
                    col += int(tile)
                else:
                    if tile.isupper():
                        piece = Piece(row_num, col, tile)
                    else:
                        piece = Piece(row_num, col, tile)
                    piece.draw(self.screen)
                    col+=1
            row_num +=1
        pygame.display.flip()

    def draw_board(self):
        board_size = Config.SCREEN_SIZE
        size = Config.SQUARE_SIZE
        pygame.draw.rect(self.screen, Config.DARK, (0, 0, board_size, board_size))
        #self.screen.fill(Config.DARK)
        for row in range(8):
            for col in range(row % 2, 8, 2):
                pygame.draw.rect(self.screen, Config.LIGHT, (row * size, col * size, size, size))

    def higlight(self, tile):
        size = Config.SQUARE_SIZE
        if not self.reverse:
            row = tile[0]
            col = tile[1]
        else:
            row = 7 - tile[0]
            col = 7 - tile[1]
        
        pygame.draw.rect(self.screen, Config.HIGHLIGHT, (col * size, row * size, size, size))
        p = self.get_piece(tile[0], tile[1])
        piece = Piece(row, col, p)
        piece.draw(self.screen)

        if not self.reverse:
            pos = chr(tile[1] + 97)+str(8-tile[0])
        else:
            pos = chr(tile[1] + 97)+str(8-tile[0])
        possible_moves = chess_lib.get_available_moves(self.state)

        surface = pygame.Surface((Config.SCREEN_SIZE+Config.LOG_SIZE,Config.SCREEN_SIZE), pygame.SRCALPHA)
        for move in possible_moves:
            if move.startswith(pos):
                if not self.reverse:
                    x = ord(move[2])-97
                    y = 8-int(move[3])
                else:
                    x = 104-ord(move[2])
                    y = int(move[3])-1
                pygame.draw.circle(surface,Config.CIRCLE_COLOR,[(x+0.5)*Config.SQUARE_SIZE,(y+0.5)*Config.SQUARE_SIZE],Config.SQUARE_SIZE/5)
        
        self.screen.blit(surface, (0,0))
        pygame.display.flip()
        
    def allowed_move(self, source, target):
        move = source[1] + str(source[0]) + target[1] + str(target[0])
        if chess_lib.can_do_move(self.state, move):
            return True
        else:
            return False

    def player_move(self, source, target, promotion):
        move = source[1] + str(source[0]) + target[1] + str(target[0])
        if promotion is not None:
            move += promotion
        elif move in {"e1g1", "e1c1", "e8g8", "e8c8"}:
            move += "c"

        if not chess_lib.can_do_move(self.state, move):
            playsound(Config.INCORRECT_SOUND,False)
            return False, '', None

        new_state = chess_lib.get_applied_move(self.state, move)
        move,capture = self.to_chess_notation(move)
        if promotion is not None:
            move += promotion
        
        self.state = new_state
        self.draw()
        
        winner = None
        lost = chess_lib.is_lost_condition(self.state)
        if lost:
            winner = "player"
            move += "#"
        elif not chess_lib.get_available_moves(self.state):
            winner = "draw"
        elif chess_lib.is_check(self.state):
            move += "+"

        if lost:
            playsound(Config.END_SOUND)
        elif capture:
            playsound(Config.CAPTURE_SOUND)
        else:
            playsound(Config.MOVE_SOUND)

        return True, move, winner
    
    def bot_move(self):
        move = self.bot.move(self.state)
        #move = random.choice(chess_lib.get_available_moves(self.state))
        new_state = chess_lib.get_applied_move(self.state, move)
        move,capture = self.to_chess_notation(move)
        self.state = new_state
        self.draw()

        winner = None
        lost = chess_lib.is_lost_condition(self.state)
        if lost:
            winner = "opponent"
            move += "#"
        elif not chess_lib.get_available_moves(self.state):
            winner = "draw"
        elif chess_lib.is_check(self.state):
            move += "+"

        if lost:
            playsound(Config.END_SOUND)
        elif capture:
            playsound(Config.CAPTURE_SOUND)
        else:
            playsound(Config.OPPONENT_SOUND)

        return move, winner
    
    def to_chess_notation(self, move):
        if move[-1] == "c":
            if move[2] == "g":
                return "o-o",False
            else:
                return "o-o-o",False

        move = move[1] + move[0] + move[3] + move[2]
        p = self.get_piece_from_string(move[:2])
        t = self.get_piece_from_string(move[2:4])

        
        if p.upper() == 'P':
            if t != '' or (t == '' and move[1] != move[3]):
                return move[1] + 'x' + move[3] + move[2],True
            else:
                return move[3] +move[2],False
        else:
            if t != '':
                return p.upper() + 'x' + move[3] +move[2],True
            else:
                return p.upper() + move[3] +move[2],False