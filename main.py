import pygame, sys
from pygame.locals import *
import CONSTANTS
import chess
import random
import natural_selection

def main():
    computers = natural_selection.main()
    global FPSCLOCK
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((CONSTANTS.WINDOWWIDTH, CONSTANTS.WINDOWHEIGHT))

    board = chess.Board()

    mouse_x = 0 # used to store x coordinate of mouse event
    mouse_y = 0 # used to store y coordinate of mouse event
    dragging_piece = None
    original_position = None
    piece_x = None
    piece_y = None
    game_over = False
    moved = False
    move_stack = "1. "
    pygame.display.set_caption(CONSTANTS.GAMENAME)

    try:
        toPlay = int(input("Enter the generation you want to play against: "))
        toPlay -= 1
    except ValueError:
        toPlay = len(computers) - 1
    
    if toPlay < 0:
        toPlay = 0
    if toPlay > len(computers) - 1:
        toPlay = len(computers) - 1
    
    print("Best of Generation " + str(toPlay + 1) + " chosen.")

    #decide who goes first
    if random.randint(0, 1) == 1:
        COMPUTER = chess.BLACK
        PLAYER = chess.WHITE
        playerFirst = True
    else:
        COMPUTER = chess.WHITE
        PLAYER = chess.BLACK
        playerFirst = False
    computers[toPlay].colorPlaying = COMPUTER

    while True: # main game loop
        if board.turn == PLAYER:
            for event in pygame.event.get(): # event handling loop
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == MOUSEBUTTONDOWN and dragging_piece is None and not game_over:
                    mouse_x, mouse_y = event.pos
                    square = collidedWithSquare(mouse_x, mouse_y, playerFirst)
                    if square is not None:
                        piece = board.piece_at(square)
                        if piece is not None:
                            dragging_piece = piece
                            piece_x, piece_y = event.pos
                            board.remove_piece_at(square)
                            original_position = square
                elif event.type == MOUSEBUTTONUP and game_over:
                    board = chess.Board()
                    dragging_piece = None
                    original_position = None
                    piece_x = None
                    piece_y = None
                    game_over = False
                    moved = False
                    move_stack = "1. "
                    pygame.display.set_caption(CONSTANTS.GAMENAME)
                    try:
                        toPlay = int(input("Enter the generation you want to play against: "))
                        toPlay -= 1
                    except ValueError:
                        toPlay = len(computers) - 1
                    
                    if toPlay < 0:
                        toPlay = 0
                    if toPlay > len(computers) - 1:
                        toPlay = len(computers) - 1
                    print("Best of Generation " + str(toPlay + 1) + " chosen.")
                    #decide who goes first
                    if random.randint(0, 1) == 1:
                        COMPUTER = chess.BLACK
                        PLAYER = chess.WHITE
                        playerFirst = True
                    else:
                        COMPUTER = chess.WHITE
                        PLAYER = chess.BLACK
                        playerFirst = False
                    computers[toPlay].colorPlaying = COMPUTER
                elif event.type == MOUSEMOTION and dragging_piece is not None and not game_over:
                    #update position of piece being dragged
                    piece_x, piece_y = event.pos
                elif event.type == MOUSEBUTTONUP and dragging_piece is not None and not game_over:
                    #let go of token being dragged
                    mouse_x, mouse_y = event.pos
                    square = collidedWithSquare(mouse_x, mouse_y, playerFirst)
                    if square is not None and chess.square_name(original_position) != chess.square_name(square):
                        move = chess.square_name(original_position) + chess.square_name(square)
                        if (dragging_piece.symbol() == 'p' and move[-1] == '1') or (dragging_piece.symbol() == 'P' and move[-1] == '8'):
                            toPromote = displayAndChoosePromote(DISPLAYSURF, board, move_stack, playerFirst)
                            move += toPromote
                        move = chess.Move.from_uci(move)
                        board.set_piece_at(original_position, dragging_piece)
                        if move in board.legal_moves:
                            move_stack += board.san(move) + " "
                            board.push(move)
                            moved = True
                            board.remove_piece_at(original_position)
                        else:
                            board.set_piece_at(original_position, dragging_piece)
                    else:
                        board.set_piece_at(original_position, dragging_piece)
                    piece_x, piece_y = None, None
                    dragging_piece = None
                    original_position = None
                    if board.is_game_over():
                        game_over = True
                    if not playerFirst and not game_over and moved:
                        move_stack += str(board.fullmove_number) + ". "
                    if game_over:
                        move_stack += board.result()
                    if moved:
                        moved = False
                        board.turn = COMPUTER
        else:
            for event in pygame.event.get(): # event handling loop
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
            if not game_over:
                pygame.time.wait(1000)
                if CONSTANTS.RANDOM_COMPUTER:
                    computer_move = random.choice([move for move in board.legal_moves])
                elif CONSTANTS.BEST_COMPUTER:
                    possibleMoves = [move for move in board.legal_moves]
                    bestMove = [possibleMoves[0], computers[toPlay].evalMove(possibleMoves[0], board)]
                    for move in possibleMoves:
                        scoreForMove = computers[toPlay].evalMove(move, board)
                        if scoreForMove > bestMove[1]:
                            bestMove[1] = scoreForMove
                            bestMove[0] = move
                    computer_move = bestMove[0]
                move_stack += board.san(computer_move) + " "
                board.push(computer_move)
                board.turn = PLAYER
                if board.is_game_over():
                    game_over = True
                if playerFirst and not game_over:
                    move_stack += str(board.fullmove_number) + ". "
                if game_over:
                    move_stack += board.result()
            else:
                board.turn = PLAYER
            
        DISPLAYSURF = drawBoard(DISPLAYSURF, board, playerFirst, move_stack)
        if piece_x is not None and piece_y is not None:
            piece_image = getImage(dragging_piece.symbol())
            draw_x = piece_x - (CONSTANTS.SIZE_OF_SQUARE / 2)
            draw_y = piece_y - (CONSTANTS.SIZE_OF_SQUARE / 2)
            DISPLAYSURF.blit(piece_image, (draw_x, draw_y))

        pygame.display.update()
        FPSCLOCK.tick(CONSTANTS.FPS)

#initializes the board with all pieces in their proper positions.
#input: a surface
#output: the same surface, but with stuff drawn all over it
def drawBoard(DISPLAYSURF, board, playerFirst, move_stack, inPromotion=False):
    DISPLAYSURF.fill(CONSTANTS.BGCOLOR)

    x_coord = CONSTANTS.XWHITESPACE
    y_coord = CONSTANTS.YWHITESPACE

    square_color = CONSTANTS.WHITE

    for row in range(8):
        for column in range(8):
            pygame.draw.rect(DISPLAYSURF, square_color, (x_coord, y_coord, CONSTANTS.SIZE_OF_SQUARE, CONSTANTS.SIZE_OF_SQUARE))
            if playerFirst:
                #want 0,7 then 1,7 etc, so need special indexing
                piece = board.piece_at(chess.square(column, 7 - row)) #drawing from top left, want to start from bottom left
            else:
                piece = board.piece_at(chess.square(7 - column, row))
            if piece is not None:
                piece_image = getImage(piece.symbol())
                DISPLAYSURF.blit(piece_image, (x_coord, y_coord))
            if square_color == CONSTANTS.WHITE:
                square_color = CONSTANTS.GREEN
            else:
                square_color = CONSTANTS.WHITE
            x_coord += CONSTANTS.SIZE_OF_SQUARE
        #need to flip color again on new row
        if square_color == CONSTANTS.WHITE:
            square_color = CONSTANTS.GREEN
        else:
            square_color = CONSTANTS.WHITE
        x_coord = CONSTANTS.XWHITESPACE
        y_coord += CONSTANTS.SIZE_OF_SQUARE

    font = pygame.font.SysFont('ComicSansMS', 20)
    blit_text(DISPLAYSURF, move_stack, (950, 50), 1450, font, color=CONSTANTS.BLACK)

    if inPromotion:
        x_coord = int(CONSTANTS.XWHITESPACE + 1.5 * CONSTANTS.SIZE_OF_SQUARE)
        y_coord = CONSTANTS.YWHITESPACE + 3 * CONSTANTS.SIZE_OF_SQUARE
        pygame.draw.rect(DISPLAYSURF, CONSTANTS.PROMOTIONCOLOR, (x_coord, y_coord, CONSTANTS.SIZE_OF_SQUARE * 5, CONSTANTS.SIZE_OF_SQUARE * 2))
        if playerFirst:
            DISPLAYSURF.blit(CONSTANTS.WHITE_QUEEN_IMG, (CONSTANTS.XWHITESPACE + 2 * CONSTANTS.SIZE_OF_SQUARE, int(CONSTANTS.YWHITESPACE + 3.5 * CONSTANTS.SIZE_OF_SQUARE)))
            DISPLAYSURF.blit(CONSTANTS.WHITE_ROOK_IMG, (CONSTANTS.XWHITESPACE + 3 * CONSTANTS.SIZE_OF_SQUARE, int(CONSTANTS.YWHITESPACE + 3.5 * CONSTANTS.SIZE_OF_SQUARE)))
            DISPLAYSURF.blit(CONSTANTS.WHITE_BISHOP_IMG, (CONSTANTS.XWHITESPACE + 4 * CONSTANTS.SIZE_OF_SQUARE, int(CONSTANTS.YWHITESPACE + 3.5 * CONSTANTS.SIZE_OF_SQUARE)))
            DISPLAYSURF.blit(CONSTANTS.WHITE_KNIGHT_IMG, (CONSTANTS.XWHITESPACE + 5 * CONSTANTS.SIZE_OF_SQUARE, int(CONSTANTS.YWHITESPACE + 3.5 * CONSTANTS.SIZE_OF_SQUARE)))
        else:
            DISPLAYSURF.blit(CONSTANTS.BLACK_QUEEN_IMG, (CONSTANTS.XWHITESPACE + 2 * CONSTANTS.SIZE_OF_SQUARE, int(CONSTANTS.YWHITESPACE + 3.5 * CONSTANTS.SIZE_OF_SQUARE)))
            DISPLAYSURF.blit(CONSTANTS.BLACK_ROOK_IMG, (CONSTANTS.XWHITESPACE + 3 * CONSTANTS.SIZE_OF_SQUARE, int(CONSTANTS.YWHITESPACE + 3.5 * CONSTANTS.SIZE_OF_SQUARE)))
            DISPLAYSURF.blit(CONSTANTS.BLACK_BISHOP_IMG, (CONSTANTS.XWHITESPACE + 4 * CONSTANTS.SIZE_OF_SQUARE, int(CONSTANTS.YWHITESPACE + 3.5 * CONSTANTS.SIZE_OF_SQUARE)))
            DISPLAYSURF.blit(CONSTANTS.BLACK_KNIGHT_IMG, (CONSTANTS.XWHITESPACE + 5 * CONSTANTS.SIZE_OF_SQUARE, int(CONSTANTS.YWHITESPACE + 3.5 * CONSTANTS.SIZE_OF_SQUARE)))

    return DISPLAYSURF

#returns the chess square that the mouse has collided with
#or None if no square is found
def collidedWithSquare(x, y, playerFirst):
    x_coord = CONSTANTS.XWHITESPACE
    y_coord = CONSTANTS.YWHITESPACE

    for row in range(8):
        for column in range(8):
            test = pygame.Rect(x_coord, y_coord, CONSTANTS.SIZE_OF_SQUARE, CONSTANTS.SIZE_OF_SQUARE)
            if test.collidepoint(x, y):
                if playerFirst:
                    return chess.square(column, 7-row)
                else:
                    return chess.square(7 - column, row)
            x_coord += CONSTANTS.SIZE_OF_SQUARE
        #need to flip color again on new row
        x_coord = CONSTANTS.XWHITESPACE
        y_coord += CONSTANTS.SIZE_OF_SQUARE
    
    return None

#displays a screen letting you choose what to promote
#returns the chosen piece to promote too
def displayAndChoosePromote(DISPLAYSURF, board, move_stack, playerFirst):
    mouse_x, mouse_y = None, None
    mouse_clicked = False
    #Knight, Bishop, Rook, or Queen.
    while True:
        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                mouse_clicked = True
            elif event.type == MOUSEBUTTONUP and mouse_clicked:
                #let go of token being dragged
                mouse_x, mouse_y = event.pos
                mouse_clicked = False

                for square in range(4):
                    test = pygame.Rect(CONSTANTS.XWHITESPACE + (2 + square) * CONSTANTS.SIZE_OF_SQUARE, int(CONSTANTS.YWHITESPACE + 3.5 * CONSTANTS.SIZE_OF_SQUARE),
                                       CONSTANTS.SIZE_OF_SQUARE, CONSTANTS.SIZE_OF_SQUARE)
                    if test.collidepoint(mouse_x, mouse_y):
                        if square == 0:
                            return 'q'
                        elif square == 1:
                            return 'r'
                        elif square == 2:
                            return 'b'
                        else:
                            return 'n'
                return ''

        DISPLAYSURF = drawBoard(DISPLAYSURF, board, playerFirst, move_stack, inPromotion=True)

        pygame.display.update()
        FPSCLOCK.tick(CONSTANTS.FPS)

#given a string character that represents a piece, return its image
def getImage(character):
    if character == '.':
        return None
    elif character == 'r':
        return CONSTANTS.BLACK_ROOK_IMG
    elif character == "R":
        return CONSTANTS.WHITE_ROOK_IMG
    elif character == 'n':
        return CONSTANTS.BLACK_KNIGHT_IMG
    elif character == 'N':
        return CONSTANTS.WHITE_KNIGHT_IMG
    elif character == 'b':
        return CONSTANTS.BLACK_BISHOP_IMG
    elif character == 'B':
        return CONSTANTS.WHITE_BISHOP_IMG
    elif character == 'q':
        return CONSTANTS.BLACK_QUEEN_IMG
    elif character == 'Q':
        return CONSTANTS.WHITE_QUEEN_IMG
    elif character == 'k':
        return CONSTANTS.BLACK_KING_IMG
    elif character == 'K':
        return CONSTANTS.WHITE_KING_IMG
    elif character == 'p':
        return CONSTANTS.BLACK_PAWN_IMG
    elif character == 'P':
        return CONSTANTS.WHITE_PAWN_IMG

#stolen from stack overflow, blits a long text onto a surface
#pos is a tuple of the left, top part to start.
def blit_text(surface, text, pos, maxWidth, font, color=pygame.Color('black')):
    words = [word.split(' ') for word in text.splitlines()]  # 2D array where each row is a list of words.
    space = font.size(' ')[0]  # The width of a space.
    max_width, max_height = surface.get_size()
    max_width = maxWidth
    x, y = pos
    for line in words:
        for word in line:
            word_surface = font.render(word, 0, color)
            word_width, word_height = word_surface.get_size()
            if x + word_width >= max_width:
                x = pos[0]  # Reset the x.
                y += word_height  # Start on new row.
            surface.blit(word_surface, (x, y))
            x += word_width + space
        x = pos[0]  # Reset the x.
        y += word_height  # Start on new row.

if __name__ == '__main__':
    main()