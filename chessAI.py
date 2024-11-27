import random as rd

# Game Values
pieceValues = {
                "P" : 1,
                "B" : 3,
                "N" : 3,
                "R" : 5,
                "Q" : 9,
                "K" : 0
                }

CHECKMATE = 1000
STALEMATE = 0
DEPTH = 3


def findRandomMove(validMoves):
    return validMoves[rd.randint(0, len(validMoves) - 1)]

'''
def findBestMoveOld(gs, validMoves):
    turnMultiplier = 1 if gs.whiteToMove else -1
    opMinMax = CHECKMATE #from black perspective
    bestPlayerMove = None
    rd.shuffle(validMoves)
    for playerMove in validMoves:
        gs.makeMove(playerMove)
        opMoves = gs.getValidMoves()
        if gs.stalemate:
            opMaxScore = STALEMATE
        elif gs.checkmate:
            opMaxScore = -CHECKMATE
        else:
            opMaxScore = -CHECKMATE
            for move in opMoves:
                gs.makeMove(move)
                gs.getValidMoves()
                if gs.checkmate:
                    score = CHECKMATE
                elif gs.stalemate:
                    score = STALEMATE
                else:
                    score = -turnMultiplier * scoreMaterial(gs.board)
                if score > opMaxScore:
                    opMaxScore = score
                gs.undoMove()
        if opMaxScore < opMinMax:
            opMinMax = opMaxScore
            bestPlayerMove = playerMove
        gs.undoMove()
    return bestPlayerMove



def greedyMove(gs, validMoves):
    turnMultiplier = 1 if gs.whiteToMove else -1

    maxScore = -CHECKMATE #from black perspective
    bestMove = None
    for playerMove in validMoves:
        gs.makeMove(playerMove)
        if gs.checkmate:
            score = CHECKMATE
        elif gs.stalemate:
            score = 0
        else:
            score = turnMultiplier * scoreMaterial(gs.board)
        if score > maxScore:
            maxScore = score
            bestMove = playerMove
        gs.undoMove()
    return bestMove
'''
    
#helper for negamax/minmax
def findBestMove(gs, validMoves):
    global nextMove, counter
    nextMove = None
    rd.shuffle(validMoves)
    counter = 0
    #findMoveMinMax(gs, validMoves, DEPTH, gs.whiteToMove)
    #negaMax(gs, validMoves, DEPTH, 1 if gs.whiteToMove else -1)
    negaMaxABP(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1)
    print(f"Board States Considered: {counter}")
    return nextMove

'''
def findMoveMinMax(gs, validMoves, depth, whiteToMove):
    global nextMove
    if depth == 0:
        return scoreMaterial(gs.board)
    
    if whiteToMove:
        maxScore = -CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth - 1, False)
            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return maxScore

    else:
        minScore = CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth - 1, True)
            if score < minScore:
                minScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return minScore
'''

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
    for row in gs.board:
        for square in row:
            if square[0] == 'w':
                score += pieceValues[square[1]]
            elif square[0] == 'b':
                score-= pieceValues[square[1]]
    return score


#old scoring method (basic)
def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += pieceValues[square[1]]
            elif square[0] == 'b':
                score-= pieceValues[square[1]]
    return score