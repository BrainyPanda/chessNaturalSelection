import math
import random
import copy
import numpy as np
import chess

#some constants
MUTATIONPERCENTAGE = 25
DEATHPERCENTAGE = 45 #useless for now
MAXORGANISMS = 10
HIDDENLAYERSIZE = 40
NUMLAYERS = 3
GAMESPERGEN = 1
NUMGENERATION = 10
MUTATIONSTANDARDDEV = 0.05
MOVEDEPTH = 2

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
            countDraws = 0
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
                    toMove = playerFirst.getBestMove(board, playerFirst.colorPlaying)
                    if toMove != None:
                        colorMoving = chess.WHITE
                        board.push(toMove)
                    toMove = playerSecond.getBestMove(board, playerSecond.colorPlaying)
                    if toMove != None:
                        colorMoving = chess.BLACK
                        board.push(toMove)
                #update their scores and elo and tie number
                playerFirst.totalGamesPlayed += 1
                playerSecond.totalGamesPlayed += 1
                result = board.result()
                if board.is_fivefold_repetition() or board.is_seventyfive_moves(): #those responsible for draws will lose instead
                    if colorMoving == chess.WHITE:
                        result = "0-1"
                    else:
                        result = "1-0"
                    countDraws += 1
                if result == "1-0":
                    playerFirst.score += 1
                    playerFirst.totalWins += 1
                    playerSecond.totalLosses += 1
                elif result == "0-1":
                    playerSecond.score += 1
                    playerSecond.totalWins += 1
                    playerFirst.totalLosses += 1
                elif result == "1/2-1/2":
                    playerFirst.score += 0.5
                    playerSecond.score += 0.5
                    playerFirst.ties += 1
                    playerSecond.ties += 1
                playerFirst.opponentEloTotal += playerSecond.elo
                playerSecond.opponentEloTotal += playerFirst.elo
                playerFirst.elo = int((playerFirst.opponentEloTotal + 400 * (playerFirst.totalWins - playerFirst.totalLosses))/playerFirst.totalGamesPlayed)
                playerSecond.elo = int((playerSecond.opponentEloTotal + 400 * (playerSecond.totalWins - playerSecond.totalLosses))/playerSecond.totalGamesPlayed)
            print("Stupid draws: " + str(countDraws))
    
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
            countKills = 0
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
        firstTheta = np.random.rand(HIDDENLAYERSIZE, 32)
        self.thetas = [] #thetas, each index is the matrix
        self.thetas.append(firstTheta)
        for newTheta in range(NUMLAYERS - 1):
            self.thetas.append(np.random.rand(HIDDENLAYERSIZE, HIDDENLAYERSIZE + 1))
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
    
    def getBestMove(self, board, color):
        bestBoardScore = -1
        toReturn = None
        if board.is_game_over(): #game is over, no need for best move
            return toReturn
        possibleMoves = [move for move in board.legal_moves]
        for move in possibleMoves:
            newBoard = board.copy()
            newBoard.push(move)
            #if newBoard.is_repetition(5) and len(possibleMoves) != 1: #prevent 5-fold repetition
                #continue
            newColor = not color
            boardScore = self.evalBoard(newBoard, newColor, 1)
            if boardScore > bestBoardScore:
                toReturn = move
                bestBoardScore = boardScore
        return toReturn

    def evalBoard(self, board, color, depth=1, bestFound=-1):
        global MOVEDEPTH
        sigmoid_v = np.vectorize(sigmoid)
        #score the original board
        initialData = np.matrix([self.getInitialData(board, color)])
        previous = initialData
        for theta in self.thetas:
            temp = previous * np.transpose(theta)
            temp = sigmoid_v(temp)
            previous = temp
            if not np.array_equal(theta, self.thetas[-1]):
                previous = np.insert(previous, 0, values=1, axis=1)
        if depth >= MOVEDEPTH:
            return previous.item()
        if previous.item() < bestFound:
            return bestFound
        bestBoardScore = -1
        possibleMoves = [move for move in board.legal_moves]
        for move in possibleMoves:
            newBoard = board.copy()
            newBoard.push(move)
            #if newBoard.is_repetition(5) and len(possibleMoves) != 1: #prevent 5-fold repetition
                #continue
            newColor = not color
            boardScore = self.evalBoard(newBoard, newColor, depth + 1, bestBoardScore)
            if boardScore > bestBoardScore:
                bestBoardScore = boardScore
        return bestBoardScore
    
    #gets the number of points white and black have respectively
    #returns the number of points in same order
    def getInitialData(self, board, color):
        if color == chess.WHITE:
            otherColor = chess.BLACK
        else:
            otherColor = chess.WHITE
        boardCenter = [chess.D4, chess.D5, chess.E4, chess.E5]
        toReturn = [0] * 31
        maxData = [8, 2, 2, 2, 1, 8, 2, 2, 2, 1, 16, 26, 28, 27, 16, 26, 28, 27, 2, 10, 2, 10, 4, 4, 1, 1, 40, 8, 8, 8, 1]
        #num fPawns, fKnights, bish, rook, queen, EPawns, knights, bish, rook, queen - 10
        #squares attacked by fKnights, bish, rook, queen, EKnights, bish, rook, queen - 8
        #friendly pawns controlling center, friendly pieces, enemy pawns, enemy pieces - 4
        #center squares with friendly color piece on, center squares with enemy color piece on - 2
        #friendly has castled, enemy, move number - 3
        #friendly pawns supporting pawns, avg rank of friendly pawns, avg rank of enemy pawns - 3
        #if current side is on check - 1

        for square in chess.SQUARES:
            if square in boardCenter:
                attackers = list(board.attackers(color, square))
                for i in range(len(attackers)):
                    if board.piece_at(attackers[i]) == chess.PAWN:
                        toReturn[18] += 1
                    else:
                        toReturn[19] += 1
                attackers = list(board.attackers(otherColor, square))
                for i in range(len(attackers)):
                    if board.piece_at(attackers[i]) == chess.PAWN:
                        toReturn[20] += 1
                    else:
                        toReturn[21] += 1
                if board.piece_at(square) != None:
                    if board.piece_at(square) == color:
                        toReturn[22] += 1
                    else:
                        toReturn[23] += 1
            if board.piece_at(square) != None:
                if board.color_at(square) == color:
                    if board.piece_at(square) == chess.PAWN:
                        toReturn[0] += 1
                        attackers = list(board.attackers(color, square))
                        for i in range(len(attackers)):
                            if board.piece_at(attackers[i]) == chess.PAWN:
                                toReturn[27] += 1
                        toReturn[28] += chess.square_rank(square)
                    if board.piece_at(square) == chess.KNIGHT:
                        toReturn[1] += 1
                        toReturn[10] += len(board.attacks(square))
                    if board.piece_at(square) == chess.BISHOP:
                        toReturn[2] += 1
                        toReturn[11] += len(board.attacks(square))
                    if board.piece_at(square) == chess.ROOK:
                        toReturn[3] += 1
                        toReturn[12] += len(board.attacks(square))
                    if board.piece_at(square) == chess.QUEEN:
                        toReturn[4] += 1
                        toReturn[13] += len(board.attacks(square))
                else:
                    if board.piece_at(square) == chess.PAWN:
                        toReturn[5] += 1
                        toReturn[29] += chess.square_rank(square)
                    if board.piece_at(square) == chess.KNIGHT:
                        toReturn[6] += 1
                        toReturn[14] += len(board.attacks(square))
                    if board.piece_at(square) == chess.BISHOP:
                        toReturn[7] += 1
                        toReturn[15] += len(board.attacks(square))
                    if board.piece_at(square) == chess.ROOK:
                        toReturn[8] += 1
                        toReturn[16] += len(board.attacks(square))
                    if board.piece_at(square) == chess.QUEEN:
                        toReturn[9] += 1
                        toReturn[17] += len(board.attacks(square))
        
        if board.has_castling_rights(color):
            toReturn[24] = 1
        if board.has_castling_rights(otherColor):
            toReturn[25] = 1
        toReturn[26] = board.fullmove_number
        if toReturn[26] > 40:
            toReturn[26] = 40
        if toReturn[0] != 0: #pawn rank takes avg
            toReturn[28] /= toReturn[0]
        if toReturn[5] != 0:
            toReturn[29] /= toReturn[5]
        if color == chess.BLACK: #whoever's playing black, their pawn rank has to flip around
            toReturn[28] = 8 - toReturn[28]
        else:
            toReturn[29] = 8 - toReturn[29]
        toReturn[30] = int(board.is_check())

        #for i in range(len(toReturn)):
        #    toReturn[i] = toReturn[i] / maxData[i]

        toReturn.insert(1, 0) #insert 1 as bias variable

        return toReturn

def sigmoid(x):
    return 1 / (1 + math.exp(-0.1 * x))

#the function that main will call, returns a list with the best AI from each generation
def main():
    newEco = ecosystem()
    bestOrganisms = newEco.runSimulation()
    return bestOrganisms

if __name__ == "__main__":
    main()