import pygame

WINDOWWIDTH = 1500 #has to be bigger than windowheight
WINDOWHEIGHT = 900
GAMENAME = "Demon-beater"
FPS = 30

RANDOM_COMPUTER = False
BEST_COMPUTER = False
MINIMAX_COMPUTER = True

#            R    G    B
GRAY     = (100, 100, 100)
LIGHTGRAY= (211, 211, 211)
NAVYBLUE = ( 60,  60, 100)
WHITE    = (255, 255, 255)
RED      = (255,   0,   0)
GREEN    = (  0, 128,   0)
BLUE     = (  0,   0, 255)
SEABLUE  = (  0, 119, 190)
YELLOW   = (255, 255,   0)
ORANGE   = (255, 128,   0)
TAN      = (210, 180, 140)
PURPLE   = (255,   0, 255)
CYAN     = (  0, 255, 255)
BLACK    = (  0,   0,   0)
SILVER   = (192, 192, 192)
LIMEGREEN= ( 50, 205,  50)

BGCOLOR = TAN
PROMOTIONCOLOR = GRAY
XWHITESPACE = 50
YWHITESPACE = 50

SIZE_OF_SQUARE = int((WINDOWHEIGHT - (2 * YWHITESPACE)) / 8)

BLACK_BISHOP_IMG = pygame.image.load('black_bishop.png')
BLACK_BISHOP_IMG = pygame.transform.scale(BLACK_BISHOP_IMG, (SIZE_OF_SQUARE, SIZE_OF_SQUARE))
WHITE_BISHOP_IMG = pygame.image.load('white_bishop.png')
WHITE_BISHOP_IMG = pygame.transform.scale(WHITE_BISHOP_IMG, (SIZE_OF_SQUARE, SIZE_OF_SQUARE))
BLACK_KING_IMG = pygame.image.load('black_king.png')
BLACK_KING_IMG = pygame.transform.scale(BLACK_KING_IMG, (SIZE_OF_SQUARE, SIZE_OF_SQUARE))
WHITE_KING_IMG = pygame.image.load('white_king.png')
WHITE_KING_IMG = pygame.transform.scale(WHITE_KING_IMG, (SIZE_OF_SQUARE, SIZE_OF_SQUARE))
BLACK_KNIGHT_IMG = pygame.image.load('black_knight.png')
BLACK_KNIGHT_IMG = pygame.transform.scale(BLACK_KNIGHT_IMG, (SIZE_OF_SQUARE, SIZE_OF_SQUARE))
WHITE_KNIGHT_IMG = pygame.image.load('white_knight.png')
WHITE_KNIGHT_IMG = pygame.transform.scale(WHITE_KNIGHT_IMG, (SIZE_OF_SQUARE, SIZE_OF_SQUARE))
BLACK_PAWN_IMG = pygame.image.load('black_pawn.png')
BLACK_PAWN_IMG = pygame.transform.scale(BLACK_PAWN_IMG, (SIZE_OF_SQUARE, SIZE_OF_SQUARE))
WHITE_PAWN_IMG = pygame.image.load('white_pawn.png')
WHITE_PAWN_IMG = pygame.transform.scale(WHITE_PAWN_IMG, (SIZE_OF_SQUARE, SIZE_OF_SQUARE))
BLACK_QUEEN_IMG = pygame.image.load('black_queen.png')
BLACK_QUEEN_IMG = pygame.transform.scale(BLACK_QUEEN_IMG, (SIZE_OF_SQUARE, SIZE_OF_SQUARE))
WHITE_QUEEN_IMG = pygame.image.load('white_queen.png')
WHITE_QUEEN_IMG = pygame.transform.scale(WHITE_QUEEN_IMG, (SIZE_OF_SQUARE, SIZE_OF_SQUARE))
BLACK_ROOK_IMG = pygame.image.load('black_rook.png')
BLACK_ROOK_IMG = pygame.transform.scale(BLACK_ROOK_IMG, (SIZE_OF_SQUARE, SIZE_OF_SQUARE))
WHITE_ROOK_IMG = pygame.image.load('white_rook.png')
WHITE_ROOK_IMG = pygame.transform.scale(WHITE_ROOK_IMG, (SIZE_OF_SQUARE, SIZE_OF_SQUARE))