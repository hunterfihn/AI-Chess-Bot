import random as rd
import ChessMain

# Game Values
pieceValues = {
                "P" : 1,
                "N" : 3,
                "B" : 3.5,
                "R" : 5,
                "Q" : 9.7,
                "K" : 0
                }

knightScores = [[1, 1, 1, 1, 1, 1, 1, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 3, 4, 4, 2, 2, 1],
                [1, 2, 3, 4, 4, 2, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 1, 1, 1, 1, 1, 1, 1]]

bishopScores = [[4, 3, 2, 1, 1, 2, 3, 4],
                [3, 4, 3, 2, 2, 3, 4, 3],
                [2, 3, 4, 3, 3, 4, 3, 2],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [2, 3, 4, 3, 3, 4, 3, 2],
                [3, 4, 3, 2, 2, 3, 4, 3],
                [4, 3, 2, 1, 1, 2, 3, 4]]

queenScores = [ [1, 1, 1, 3, 1, 1, 1, 1],
                [1, 2, 3, 3, 3, 1, 1, 1],
                [1, 4, 3, 3, 3, 4, 2, 1],
                [1, 2, 3, 3, 3, 2, 2, 1],
                [1, 2, 3, 3, 3, 2, 2, 1],
                [1, 4, 3, 3, 3, 4, 2, 1],
                [1, 1, 2, 3, 3, 1, 1, 1],
                [1, 1, 1, 3, 1, 1, 1, 1]]

rookScores = [  [4, 3, 4, 4, 4, 4, 3, 4],
                [4, 4, 4, 4, 4, 4, 4, 4],
                [1, 1, 2, 2, 2, 2, 1, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 1, 2, 2, 2, 2, 1, 1],
                [4, 4, 4, 4, 4, 4, 4, 4],
                [4, 3, 4, 4, 4, 4, 3, 4]]

whitePawnScores = [[8, 8, 8, 8, 8, 8, 8, 8],
                   [8, 8, 8, 8, 8, 8, 8, 8],
                   [5, 6, 6, 7, 7, 6, 6, 5],
                   [2, 3, 3, 5, 5, 3, 3, 2],
                   [1, 2, 3, 4, 4, 3, 2, 1],
                   [1, 1, 2, 3, 3, 2, 1, 1],
                   [1, 1, 1, 0, 0, 1, 1, 1],
                   [0, 0, 0, 0, 0, 0, 0, 0]]


blackPawnScores = [[0, 0, 0, 0, 0, 0, 0, 0],
                   [1, 1, 1, 0, 0, 1, 1, 1],
                   [1, 1, 2, 3, 3, 2, 1, 1],
                   [1, 2, 3, 4, 4, 3, 2, 1],
                   [2, 3, 3, 5, 5, 3, 3, 2],
                   [5, 6, 6, 7, 7, 6, 6, 5],
                   [8, 8, 8, 8, 8, 8, 8, 8],
                   [8, 8, 8, 8, 8, 8, 8, 8]]



piecePositionScoresTables = {"N": knightScores,
                             "B": bishopScores,
                             "Q": queenScores,
                             "R": rookScores,
                             "wP": whitePawnScores,
                             "bP": blackPawnScores}

CHECKMATE = 9999
STALEMATE = 0
DEPTH = 3

def findRandomMove(validMoves, returnQueue):
    returnQueue.put(validMoves[rd.randint(0, len(validMoves) - 1)])

def findRandomMoveNoQueue(validMoves):
    return validMoves[rd.randint(0, len(validMoves) - 1)]

    
#helper for negamax/minmax
def findBestMove(gs, validMoves, returnQueue):
    global nextMove, counter
    nextMove = None
    rd.shuffle(validMoves)
    counter = 0
    #negaMax(gs, validMoves, DEPTH, 1 if gs.whiteToMove else -1)
    negaMaxABP(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1)
    print(f"Board States Considered: {counter}")
    returnQueue.put(nextMove)



def negaMax(gs, validMoves, depth, turnMult):
    global nextMove, counter
    counter += 1
    if depth == 0:
        return turnMult * scoreBoard(gs)
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -negaMax(gs, nextMoves, depth-1, -turnMult)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()
    return maxScore

def negaMaxABP(gs, validMoves, depth, alpha, beta, turnMult):
    global nextMove, counter
    counter += 1
    if depth == 0:
        return turnMult * scoreBoard(gs)
    
    #move ordering - implement later
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move, simulating = True)
        nextMoves = gs.getValidMoves()
        score = -negaMaxABP(gs, nextMoves, depth-1, -beta, -alpha, -turnMult)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()
        if maxScore > alpha:
            alpha = maxScore
        if alpha >= beta:
            break
    return maxScore


#positive score = good for white, negative = good for black
#current boardEval method
def scoreBoard(gs):
    if gs.checkmate:
        if gs.whiteToMove:
            return -CHECKMATE
        else:
            return CHECKMATE
    elif gs.stalemate:
        return STALEMATE
    
    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            square = gs.board[row][col]
            if square != "--":
                piecePositionScore = 0 
                if square[1] != "K":
                    if square[1] == "P":
                        piecePositionScore = piecePositionScoresTables[square][row][col]
                    else:
                        piecePositionScore = piecePositionScoresTables[square[1]][row][col]
                        
                if square[0] == 'w':
                    score += pieceValues[square[1]] + piecePositionScore * .4
                elif square[0] == 'b':
                    score -= pieceValues[square[1]] + piecePositionScore * .4
    return score
