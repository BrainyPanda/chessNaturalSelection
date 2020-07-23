import math
import random
import copy
import numpy as np
import chess

MOVEDEPTH = 3
timesCalled = 0

PAWNOPENINGTABLE = [ 0,  0,  0,  0,  0,  0,  0,  0,
                    50, 50, 50, 50, 50, 50, 50, 50,
                    10, 10, 20, 30, 30, 20, 10, 10,
                    5,  5, 10, 25, 25, 10,  5,  5,
                    0,  0,  0, 20, 20,  0,  0,  0,
                    5, -5,-5 ,  0,  0, -5, -5,  5,
                    5, 10, 10,-20,-20, 10, 10,  5,
                    0,  0,  0,  0,  0,  0,  0,  0]

PAWNENDGAMETABLE = [ 0,  0,  0,  0,  0,  0,  0,  0,
                    50, 50, 50, 50, 50, 50, 50, 50,
                    40, 40, 40, 40, 40, 40, 40, 40,
                    30, 30, 30, 30, 30, 30, 30, 30,
                    20, 20, 20, 20, 20, 20, 20, 20,
                    10, 10, 10, 10, 10, 10, 10, 10,
                     0,  5,  5,  5,  5,  5,  5,  5,
                     0,  0,  0,  0,  0,  0,  0,  0]

KNIGHTTABLE = [-50,-40,-30,-30,-30,-30,-40,-50,
            -40,-20,  0,  0,  0,  0,-20,-40,
            -30,  0, 10, 15, 15, 10,  0,-30,
            -30,  5, 15, 20, 20, 15,  5,-30,
            -30,  0, 15, 20, 20, 15,  0,-30,
            -40,  5, 10, 15, 15, 10,  5,-40,
            -40,-20,  0,  5,  5,  0,-20,-40,
            -50,-20,-30,-30,-30,-30,-20,-50,]

BISHOPTABLE = [-20,-10,-10,-10,-10,-10,-10,-20,
            -10,  0,  0,  0,  0,  0,  0,-10,
            -10,  0,  5, 10, 10,  5,  0,-10,
            -10,  5,  5, 10, 10,  5,  5,-10,
            -10,  0, 10, 10, 10, 10,  0,-10,
            -10, 10, 10, 10, 10, 10, 10,-10,
            -10, 10,  0,  5,  5,  0, 10,-10,
            -20,-10,-10,-10,-10,-10,-10,-20,]

ROOKTABLE = [  0,  0,  0,  0,  0,  0,  0,  0,
             5, 10, 10, 10, 10, 10, 10,  5,
            -5,  0,  0,  5,  5,  0,  0, -5,
            -5,  0,  0,  5,  5,  0,  0, -5,
            -5,  0,  0,  5,  5,  0,  0, -5,
            -5,  0,  0,  5,  5,  0,  0, -5,
            -5,  0,  0,  5,  5,  0,  0, -5,
           -15,-15,-10, 10, 10,-10,-15,-15]

QUEENTABLE = [-20,-10,-10, -5, -5,-10,-10,-20,
            -10,  0,  0,  0,  0,  0,  0,-10,
            -10,  0,  5,  5,  5,  5,  0,-10,
             -5,  0,  5,  5,  5,  5,  0, -5,
              0,  0,  5,  5,  5,  5,  0, -5,
            -10,  5,  5,  5,  5,  5,  0,-10,
            -10,  0,  5,  0,  0,  0,  0,-10,
            -20,-10,-10, -5, -5,-10,-10,-20]

KINGMIDDLETABLE = [-30,-40,-40,-50,-50,-40,-40,-30,
                -30,-40,-40,-50,-50,-40,-40,-30,
                -30,-40,-40,-50,-50,-40,-40,-30,
                -30,-40,-40,-50,-50,-40,-40,-30,
                -20,-30,-30,-40,-40,-30,-30,-20,
                -10,-20,-20,-20,-20,-20,-20,-10,
                20, 20,  0,  0,  0,  0, 20, 20,
                30, 50, 10,  0,  0, 10, 50, 30]

KINGENDTABLE = [-50,-40,-30,-20,-20,-30,-40,-50,
                -30, 20, 10,  0,  0, 10, 20,-30,
                -30, 10, 20, 30, 30, 20, 10,-30,
                -30, 10, 30, 40, 40, 30, 10,-30,
                -30, 10, 30, 40, 40, 30, 10,-30,
                -30, 10, 20, 30, 30, 20, 10,-30,
                -30, 30,  0,  0,  0,  0, 30,-30,
                -50,-30,-30,-30,-30,-30,-30,-50]

names = open("Names.txt", "r")
allNames = names.readlines()
names.close()

for i in range(len(allNames)):
    allNames[i] = allNames[i].strip()
    allNames[i] = allNames[i].replace("\n", "")

#the ai
class organism():
    def __init__(self): #initialize randomly if no params passed in
        global allNames
        self.colorPlaying = None
        self.inEndgame = False
        self.name = random.choice(allNames)
    
    def getBestMove(self, board, color, depth=1, minimize=False):
        global timesCalled
        if depth == 1:
            timesCalled = 0
        else:
            timesCalled += 1
        if not minimize:
            bestBoardScore = float("-inf")
        else:
            bestBoardScore = float("inf")
        toReturn = None
        if board.is_game_over(): #game is over, no need for best move
            if (board.result() == "1-0" and self.colorPlaying == chess.WHITE) or (board.result() == "0-1" and self.colorPlaying == chess.BLACK):
                return None, float("inf")
            elif (board.result() == "1-0" and self.colorPlaying == chess.BLACK) or (board.result() == "0-1" and self.colorPlaying == chess.WHITE):
                return None, float("-inf")
            else:
                return None, 0
        possibleMoves = [move for move in board.legal_moves]
        for move in possibleMoves:
            newBoard = board.copy()
            newBoard.push(move)
            #if newBoard.is_repetition(5) and len(possibleMoves) != 1: #prevent 5-fold repetition
                #continue
            boardScore = self.evalBoard(newBoard, color)
            if not minimize and boardScore < bestBoardScore:
                continue
            elif minimize and boardScore > bestBoardScore:
                continue
            if depth < MOVEDEPTH:
                tempMove, boardScore = self.getBestMove(newBoard, color, depth+1, not minimize)
            if not minimize:
                if boardScore > bestBoardScore:
                    toReturn = move
                    bestBoardScore = boardScore
            else:
                if boardScore < bestBoardScore:
                    toReturn = move
                    bestBoardScore = boardScore
        return toReturn, bestBoardScore

    def evalBoard(self, board, color):
        score = 0
        countQueens = 0
        countMinors = 0
        countEnemyQueens = 0
        countEnemyMinors = 0
        for square in chess.SQUARES:
            if color == chess.WHITE:
                toPenalize = chess.square_mirror(square)
            else:
                toPenalize = square
            otherSquare = chess.square_mirror(toPenalize)
            if board.piece_at(square) is not None:
                if board.color_at(square) == color:
                    if board.piece_at(square).piece_type == chess.PAWN:
                        score += 100
                        if self.inEndgame:
                            score += PAWNENDGAMETABLE[toPenalize]
                        else:
                            score += PAWNOPENINGTABLE[toPenalize]
                    elif board.piece_at(square).piece_type == chess.KNIGHT:
                        score += 320
                        score += KNIGHTTABLE[toPenalize]
                        countMinors += 1
                    elif board.piece_at(square).piece_type == chess.BISHOP:
                        score += 320
                        score += BISHOPTABLE[toPenalize]
                        countMinors += 1
                    elif board.piece_at(square).piece_type == chess.ROOK:
                        score += 500
                        score += ROOKTABLE[toPenalize]
                        countMinors += 1
                    elif board.piece_at(square).piece_type == chess.QUEEN:
                        score += 900
                        score += QUEENTABLE[toPenalize]
                        countQueens += 1
                    else:
                        score += 20000
                        if self.inEndgame:
                            score += KINGENDTABLE[toPenalize]
                        else:
                            score += KINGMIDDLETABLE[toPenalize]
                else:
                    if board.piece_at(square).piece_type == chess.PAWN:
                        score -= 100
                        if self.inEndgame:
                            score -= PAWNENDGAMETABLE[otherSquare]
                        else:
                            score -= PAWNOPENINGTABLE[otherSquare]
                    elif board.piece_at(square).piece_type == chess.KNIGHT:
                        score -= 320
                        score -= KNIGHTTABLE[otherSquare]
                        countEnemyMinors += 1
                    elif board.piece_at(square).piece_type == chess.BISHOP:
                        score -= 320
                        score -= BISHOPTABLE[otherSquare]
                        countEnemyMinors += 1
                    elif board.piece_at(square).piece_type == chess.ROOK:
                        score -= 500
                        score -= ROOKTABLE[otherSquare]
                        countEnemyMinors += 1
                    elif board.piece_at(square).piece_type == chess.QUEEN:
                        score -= 900
                        score -= QUEENTABLE[otherSquare]
                        countEnemyQueens += 1
                    else:
                        score -= 20000
                        if self.inEndgame:
                            score -= KINGENDTABLE[otherSquare]
                        else:
                            score -= KINGMIDDLETABLE[otherSquare]
        if self.inEndgame:
            if countQueens > 0 and countEnemyQueens > 0:
                self.inEndgame = False
            elif countQueens >= 1 and countMinors > 1 and countEnemyQueens >= 1 and countEnemyMinors > 1:
                self.inEndgame = False
            elif countQueens == 0 and countEnemyQueens == 0 and (countMinors > 3 or countEnemyMinors > 3):
                self.inEndgame = False
        else:
            if countQueens == 0 and countMinors <= 3 and countEnemyQueens == 0 and countEnemyMinors <= 3:
                self.inEndgame = True
            elif countQueens >= 1 and countMinors <= 1 and countEnemyQueens >= 1 and countEnemyMinors <= 1:
                self.inEndgame = True
        return score

#the function that main will call, returns a list with the best AI from each generation
def main():
    computer = organism()
    return computer

if __name__ == "__main__":
    main()