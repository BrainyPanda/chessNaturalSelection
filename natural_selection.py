import math
import random
import copy
import numpy as np
import chess

#some constants
MUTATIONPERCENTAGE = 30
DEATHPERCENTAGE = 45 #useless for now
MAXORGANISMS = 70
HIDDENLAYERSIZE = 13
NUMLAYERS = 3
GAMESPERGEN = 3
NUMGENERATION = 30
MUTATIONSTANDARDDEV = 0.2

tagNum = 0

names = open("Names.txt", "r")
allNames = names.readlines()
names.close()

originalNames = []

for i in range(len(allNames)):
    allNames[i] = allNames[i].strip()
    allNames[i] = allNames[i].replace("\n", "")
    originalNames.append(allNames[i])

#stores all current organisms that are alive
class ecosystem():
    def __init__(self): #initialize 100 random organisms
        self.population = []
        for i in range(MAXORGANISMS):
            self.population.append(organism())
            self.population[i].assignName()
    
    #run the simulation
    def runSimulation(self):
        bestOrganisms = []
        for i in range(NUMGENERATION):
            print("Simulating Generation " + str(i + 1))
            self.simulateGeneration()
            print("Reproducing Generation " + str(i + 1))
            self.reproduce()
            print("Mutating Generation " + str(i + 1))
            self.mutateGeneration()
            self.population.sort(key=lambda x: (x.elo, x.score), reverse=True)
            bestOrganisms.append(self.population[0])
            print("Resetting Generation " + str(i + 1))
            self.resetPopulation()
        return bestOrganisms
    
    def resetPopulation(self):
        for organism in self.population:
            organism.newGen()

    #randomly pair off all organisms
    #have them play
    def simulateGeneration(self):
        for game in range(GAMESPERGEN):
            random.shuffle(self.population)
            for i in range(int(len(self.population) / 2)):
                board = chess.Board()
                if random.randint(0, 1) == 1:
                    self.population[2 * i].colorPlaying = chess.BLACK
                    self.population[2 * i + 1].colorPlaying = chess.WHITE
                    playerFirst = self.population[2 * i + 1]
                    playerSecond = self.population[2 * i]
                else:
                    self.population[2 * i + 1].colorPlaying = chess.BLACK
                    self.population[2 * i].colorPlaying = chess.WHITE
                    playerFirst = self.population[2 * i]
                    playerSecond = self.population[2 * i + 1]
                while not board.is_game_over():
                    possibleMoves = [move for move in board.legal_moves]
                    bestMove = [possibleMoves[0], playerFirst.evalMove(possibleMoves[0], board)]
                    for move in possibleMoves:
                        scoreForMove = playerFirst.evalMove(move, board)
                        if scoreForMove > bestMove[1]:
                            bestMove[1] = scoreForMove
                            bestMove[0] = move
                    board.push(bestMove[0])
                    possibleMoves = [move for move in board.legal_moves]
                    if len(possibleMoves) != 0:
                        bestMove = [possibleMoves[0], playerSecond.evalMove(possibleMoves[0], board)]
                        for move in possibleMoves:
                            scoreForMove = playerSecond.evalMove(move, board)
                            if scoreForMove > bestMove[1]:
                                bestMove[1] = scoreForMove
                                bestMove[0] = move
                        board.push(bestMove[0])
                #update their scores and elo and tie number
                playerFirst.totalGamesPlayed += 1
                playerSecond.totalGamesPlayed += 1
                if board.result() == "1-0":
                    playerFirst.score += 1
                    playerFirst.totalWins += 1
                    playerSecond.totalLosses += 1
                elif board.result() == "0-1":
                    playerSecond.score += 1
                    playerSecond.totalWins += 1
                    playerFirst.totalLosses += 1
                elif board.result() == "1/2-1/2":
                    playerFirst.score += 0.5
                    playerSecond.score += 0.5
                    playerFirst.ties += 1
                    playerSecond.ties += 1
                playerFirst.opponentEloTotal += playerSecond.elo
                playerSecond.opponentEloTotal += playerFirst.elo
                playerFirst.elo = int((playerFirst.opponentEloTotal + 400 * (playerFirst.totalWins - playerFirst.totalLosses))/playerFirst.totalGamesPlayed)
                playerSecond.elo = int((playerSecond.opponentEloTotal + 400 * (playerSecond.totalWins - playerSecond.totalLosses))/playerSecond.totalGamesPlayed)
    
    #choose a random amount of organisms to mutate and mutate them
    def mutateGeneration(self):
        random.shuffle(self.population)
        toMutate = int(MUTATIONPERCENTAGE / 100 * MAXORGANISMS)
        for i in range(toMutate):
            for j in range(len(self.population[i].thetas)):
                #random gaussian noise
                self.population[i].thetas[j] += np.random.normal(0, MUTATIONSTANDARDDEV, self.population[i].thetas[j].shape)

    #kill off those with score lower than games per gen / 2
    #kill off those with 3 ties
    #award those with no ties
    #refill organism pool by reproducing
    #asexual reproduction, keep copying by adding top guy, then top 2, etc.
    def reproduce(self):
        countKills = 0
        originalPopulation = []
        for organism in self.population:
            originalPopulation.append(organism)
        self.population.sort(key=lambda x: (x.score, x.elo))
        i = 0
        while i < len(self.population):
            if self.population[i].ties == GAMESPERGEN: #tying all 3 games has a penalty
                #this prevents stalling out games by repetition
                self.population[i].score -= 0.1
            if self.population[i].ties == 0:
                self.population[i].score += 0.1
            if self.population[i].score < float(GAMESPERGEN / 2):
                self.population.remove(self.population[i])
                countKills += 1
                i -= 1
            i += 1
        if len(self.population) == 0: #everyone tied each other
            for organism in originalPopulation:
                self.population.append(organism)
        #display top of the generation
        self.population.sort(key=lambda x: (x.elo, x.score), reverse=True)
        toLoop = 5
        if toLoop > len(self.population):
            toLoop = len(self.population)
        toPrint = "Top " + str(toLoop) + " elos: "
        for k in range(toLoop):
            #toPrint += str(k + 1) + ". Tag " + str(self.population[k].tagNum) + ": " + str(self.population[k].elo) + ", " + str(self.population[k].score) + "   "
            toPrint += str(k + 1) + ". " + str(self.population[k].name) + ": " + str(self.population[k].elo) + ", " + str(self.population[k].score) + "   "
        self.population.sort(key=lambda x: (x.score, x.elo), reverse=True)
        toPrint += "\nTop " + str(toLoop) + " scores: "
        for k in range(toLoop):
            #toPrint += str(k + 1) + ". Tag " + str(self.population[k].tagNum) + ": " + str(self.population[k].elo) + ", " + str(self.population[k].score) + "   "
            toPrint += str(k + 1) + ". " + str(self.population[k].name) + ": " + str(self.population[k].elo) + ", " + str(self.population[k].score) + "   "
        print(toPrint)
        #want to duplicate highest scoring ones, since those that mutated into
        #high score likely will not have high elo yet.
        countBorn = 0
        for i in range(20):
            for j in range(i):
                newBorn = copy.deepcopy(self.population[j])
                newBorn.tag = tagNum
                newBorn.assignName()
                self.population.append(newBorn)
                countBorn += 1
                if countBorn == countKills:
                    break
            if countBorn == countKills:
                break

#a single neural net. Input is a move, output is a score for that move
class organism():
    def __init__(self): #initialize randomly if no params passed in
        global tagNum
        self.layers = [] #the layers
        firstTheta = np.random.rand(HIDDENLAYERSIZE, 14)
        self.thetas = [] #thetas, each index is the matrix
        self.thetas.append(firstTheta)
        for newTheta in range(NUMLAYERS - 1):
            self.thetas.append(np.random.normal(0, 1, (HIDDENLAYERSIZE, HIDDENLAYERSIZE + 1)))
        self.thetas.append(np.random.rand(1, HIDDENLAYERSIZE + 1))
        self.output = 0
        self.colorPlaying = None
        self.score = 0
        self.elo = 400 #start at 400
        self.ties = 0
        self.totalWins = 0
        self.totalLosses = 0
        self.totalGamesPlayed = 0
        self.opponentEloTotal = 0
        self.tag = tagNum
        tagNum += 1
        self.name = ""
    
    def assignName(self):
        global allNames
        global originalNames
        self.name = random.choice(allNames)
        allNames.remove(self.name)
        if len(allNames) == 0:
            for name in originalNames:
                allNames.append(name)

    #reset self after gen is complete
    def newGen(self):
        self.score = 0
        self.colorPlaying = None
        self.ties = 0
    
    def evalMove(self, move, board): #evaluate a move
        sigmoid_v = np.vectorize(sigmoid) #set up sigmoid function
        #create the input vector by getting information on the move
        whitePoints, blackPoints = sumPoints(board)
        if self.colorPlaying == chess.WHITE:
            otherColor = chess.BLACK
            color = 0
            ownPoints = whitePoints
            opponentPoints = blackPoints
        else:
            color = 1
            otherColor = chess.WHITE
            ownPoints = blackPoints
            opponentPoints = whitePoints
        #pieceType: 1-6 for pawn, knight, bishop, rook, queen, king
        pieceType = board.piece_at(move.from_square).symbol()
        if pieceType == 'p' or pieceType == 'P':
            pieceType = 1
        elif pieceType == 'n' or pieceType == 'N':
            pieceType = 2
        elif pieceType == 'b' or pieceType == 'B':
            pieceType = 3
        elif pieceType == 'r' or pieceType == 'R':
            pieceType = 4
        elif pieceType == 'q' or pieceType == 'Q':
            pieceType = 5
        elif pieceType == 'k' or pieceType == 'K':
            pieceType = 6
        #squares have value 1-64
        squareFrom = move.from_square
        squareTo = move.to_square
        promotion = move.promotion
        if promotion == None:
            promotion = 0
        elif promotion == chess.KNIGHT:
            promotion = 1
        elif promotion == chess.BISHOP:
            promotion = 2
        elif promotion == chess.ROOK:
            promotion = 3
        elif promotion == chess.QUEEN:
            promotion = 4
        toCapture = board.piece_at(move.to_square)
        if toCapture == None:
            toCapture = 0
        else:
            toCapture = toCapture.symbol()
            if toCapture == 'p' or toCapture == 'P':
                toCapture = 1
            elif toCapture == 'n' or toCapture == 'N':
                toCapture = 2
            elif toCapture == 'b' or toCapture == 'B':
                toCapture = 3
            elif toCapture == 'r' or toCapture == 'R':
                toCapture = 4
            elif toCapture == 'q' or toCapture == 'Q':
                toCapture = 5
            else:
                toCapture = 0
        if board.gives_check(move):
            willCheck = 1
        else:
            willCheck = 0
        attackedBy = len(board.attackers(otherColor, move.to_square)) #what the piece is currently attacking
        protecting = len(board.attackers(self.colorPlaying, move.to_square)) #what the piece is currently protecting
        attackingPieces = 0
        protectingPieces = 0
        attacks = board.attacks(move.from_square)
        for square in attacks:
            if board.piece_at(square) != None and board.piece_at(square).color == otherColor: #what the piece will attack
                attackingPieces += 1
            elif board.piece_at(square) != None and board.piece_at(square).color == self.colorPlaying: #what the piece will protect
                protectingPieces += 1
        initial = np.matrix([[1, color, ownPoints, opponentPoints, pieceType, squareFrom, squareTo, promotion, toCapture, willCheck, 
                              attackedBy, protecting, attackingPieces, protectingPieces]])
        previous = initial
        for theta in self.thetas:
            temp = previous * np.transpose(theta)
            temp = sigmoid_v(temp)
            previous = temp
            if not np.array_equal(theta, self.thetas[-1]):
                previous = np.insert(previous, 0, values=1, axis=1)
        return previous.item()

def sigmoid(x):
    return 1 / (1 + math.exp(-0.1 * x))

#gets the number of points white and black have respectively
#returns the number of points in same order
def sumPoints(board):
    whiteTotal = 0
    blackTotal = 0

    for square in chess.SQUARES:
        if board.piece_at(square) != None:
            if board.color_at(square) == chess.WHITE:
                if board.piece_at(square) == chess.PAWN:
                    whiteTotal += 1
                if board.piece_at(square) == chess.KNIGHT:
                    whiteTotal += 3
                if board.piece_at(square) == chess.BISHOP:
                    whiteTotal += 3
                if board.piece_at(square) == chess.ROOK:
                    whiteTotal += 5
                if board.piece_at(square) == chess.QUEEN:
                    whiteTotal += 9
            else:
                if board.piece_at(square) == chess.PAWN:
                    blackTotal += 1
                if board.piece_at(square) == chess.KNIGHT:
                    blackTotal += 3
                if board.piece_at(square) == chess.BISHOP:
                    blackTotal += 3
                if board.piece_at(square) == chess.ROOK:
                    blackTotal += 5
                if board.piece_at(square) == chess.QUEEN:
                    blackTotal += 9
    
    return whiteTotal, blackTotal

#the function that main will call, returns a list with the best AI from each generation
def main():
    newEco = ecosystem()
    bestOrganisms = newEco.runSimulation()
    return bestOrganisms

if __name__ == "__main__":
    main()