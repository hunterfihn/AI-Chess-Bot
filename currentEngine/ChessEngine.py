
class gameState():
    def __init__(self):
        #8x8 2d list, each element of list is 2 char
        #first char is color, second is piece type
        #"--" is empty sqaure
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.checkmate = False
        self.stalemate = False
        self.enPassantPossible = ()
        self.enPassantPossibleLog = [self.enPassantPossible]

        self.whiteCastleKingside = True
        self.whiteCastleQueenside = True
        self.blackCastleKingside = True
        self.blackCastleQueenside = True
        self.castleRightsLog = [CastleRights(self.whiteCastleKingside, self.blackCastleKingside, 
                                            self.whiteCastleQueenside, self.blackCastleQueenside)]

    def makeMove(self, move, simulating = False):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.toRow][move.toCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.toRow, move.toCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.toRow, move.toCol)

        if move.pieceMoved[1] == 'P' and abs(move.startRow - move.toRow) == 2:
            self.enPassantPossible = ((move.toRow + move.startRow) //2, move.toCol)
        else:
            self.enPassantPossible = ()

        if move.enPassant:
            self.board[move.startRow][move.toCol] = "--"
        
        
        if move.pawnPromotion:
            if simulating:
                self.board[move.toRow][move.toCol] = move.pieceMoved[0] + "Q"
            else:
                '''
                print("Please chose your promotion: (Q, R, B, N): ")
                choice = input()
                '''
                self.board[move.toRow][move.toCol] = move.pieceMoved[0] + "Q"

        self.enPassantPossibleLog.append(self.enPassantPossible)
        

        if move.castle:
            if move.toCol - move.startCol == 2:
                self.board[move.toRow][move.toCol - 1] = self.board[move.toRow][move.toCol + 1]
                self.board[move.toRow][move.toCol + 1] = "--"
            else:
                self.board[move.toRow][move.toCol + 1] = self.board[move.toRow][move.toCol - 2]
                self.board[move.toRow][move.toCol - 2] = "--"
        
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.whiteCastleKingside, self.blackCastleKingside, self.whiteCastleQueenside, self.blackCastleQueenside))

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.toRow][move.toCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)
            if move.enPassant:
                self.board[move.toRow][move.toCol] = "--"
                self.board[move.startRow][move.toCol] = move.pieceCaptured
            
            self.enPassantPossibleLog.pop()
            self.enPassantPossible = self.enPassantPossibleLog[-1]

            self.castleRightsLog.pop()
            castleRights = self.castleRightsLog[-1]
            self.whiteCastleKingside = castleRights.wks
            self.blackCastleKingside = castleRights.bks
            self.whiteCastleQueenside = castleRights.wqs
            self.blackCastleQueenside = castleRights.bqs
            
            if move.castle:
                if move.toCol - move.startCol == 2:
                    self.board[move.toRow][move.toCol + 1] = self.board[move.toRow][move.toCol - 1]
                    self.board[move.toRow][move.toCol - 1] = "--"
                else:
                    self.board[move.toRow][move.toCol - 2] = self.board[move.toRow][move.toCol + 1]
                    self.board[move.toRow][move.toCol + 1] = "--"
            self.checkmate = False
            self.stalemate = False

    def updateCastleRights(self, move):
        if move.pieceMoved =='wK':
            self.whiteCastleKingside = False
            self.whiteCastleQueenside = False
        elif move.pieceMoved == 'bK':
            self.blackCastleKingside = False
            self.blackCastleQueenside = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 7:
                    self.whiteCastleKingside = False
                elif move.startCol == 0:
                    self.whiteCastleQueenside = False
        elif move.pieceMoved =='bR':
            if move.startRow == 0:
                if move.startCol == 7:
                    self.blackCastleKingside = False
                elif move.startCol == 0:
                    self.blackCastleQueenside = False

        if move.pieceCaptured == 'wR':
            if move.toRow == 7:
                if move.toCol == 7:
                    self.whiteCastleKingside = False
                elif move.toCol == 0:
                    self.whiteCastleQueenside = False
        elif move.pieceCaptured == 'bR':
            if move.toRow == 0:
                if move.toCol == 0:
                    self.blackCastleQueenside = False
                elif move.toCol == 7:
                    self.blackCastleKingside = False
            

    def getValidMoves(self):
        moves = []
        self.inCheck, self.pins, self.checks = self.pinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.inCheck:
            if len(self.checks) == 1:
                moves = self.getAllPossibleMoves()
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]
                validSqs = []
                if pieceChecking[1] == 'N':
                    validSqs = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)
                        validSqs.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].pieceMoved[1] != 'K':
                        if not (moves[i].toRow, moves[i].toCol) in validSqs:
                            moves.remove(moves[i])
            else:
                self.getKingMoves(kingRow, kingCol, moves)
        else:
            moves = self.getAllPossibleMoves()

        if len(moves) == 0:
            if self.inCheck:
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False
        return moves
   
    def pinsAndChecks(self):
        pins = []
        checks = []
        inCheck = False
        if self.whiteToMove:
            opColor = 'b'
            selfColor = 'w'
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            opColor = 'w'
            selfColor = 'b'
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), 
                      (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possPin = ()
            for i in range(1, 8):
                toRow = startRow + d[0] * i
                toCol = startCol + d[1] * i 
                if 0 <= toRow < 8 and 0 <= toCol < 8:
                    endPiece = self.board[toRow][toCol]
                    if endPiece[0] == selfColor and endPiece[1] != 'K':
                        if possPin == ():
                            possPin = (toRow, toCol, d[0], d[1])
                        else:
                            break
                    elif endPiece[0] == opColor:
                        type = endPiece[1]
                        if(0 <= j <= 3 and type == 'R') or \
                            (4 <= j <= 7 and type == 'B') or \
                            (i == 1 and  type == 'P' and ((opColor == 'w' and 6 <= j <= 7) or (opColor == 'b' and 4 <= j <= 5))) or \
                            (type == 'Q') or (i == 1 and type == 'K'):
                            if possPin == ():
                                inCheck = True
                                checks.append((toRow, toCol, d[0], d[1]))
                                break
                            else:
                                pins.append(possPin)
                                break
                        else:
                            break
                else:
                    break
        knightmoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2),
                       (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightmoves:
            toRow = startRow + m[0]
            toCol = startCol + m[1]
            if 0 <= toRow < 8 and 0 <= toCol < 8:
                endPiece = self.board[toRow][toCol]
                if endPiece[0] == opColor and endPiece[1] == 'N':
                    inCheck = True
                    checks.append((toRow, toCol, m[0], m[1]))
        return inCheck, pins, checks

    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if(turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    match piece:
                        case "P":
                            self.getPawnMoves(r, c, moves)
                        case "R":
                            self.getRookMoves(r, c, moves)
                        case "N":
                            self.getKnightMoves(r, c, moves)
                        case "B":
                            self.getBishopMoves(r, c, moves)
                        case "K":
                            self.getKingMoves(r, c, moves)
                        case "Q":
                            self.getQueenMoves(r, c, moves)
        return moves

    def getPawnMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) -1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove:
            moveAmount = -1
            startRow = 6
            backRow = 0
            opColor = 'b'
            kingRow, kingCol = self.whiteKingLocation
        else:
            moveAmount = 1
            startRow = 1
            backRow = 7
            opColor = 'w'
            kingRow, kingCol = self.blackKingLocation
        pawnPromotion = False

        if self.board[r+moveAmount][c] == "--":
            if not piecePinned or pinDirection == (moveAmount, 0):
                if r+moveAmount == backRow:
                    pawnPromotion = True
                moves.append(Move((r, c), (r+moveAmount, c), self.board, pawnPromotion=pawnPromotion))
                if r == startRow and self.board[r+2*moveAmount][c] == "--":
                    moves.append(Move((r, c), (r+2*moveAmount, c), self.board))
        if c - 1 >= 0:
            if not piecePinned or pinDirection == (moveAmount, -1):
                if self.board[r+moveAmount][c - 1][0] == opColor:
                    if r+moveAmount == backRow:
                        pawnPromotion = True
                    moves.append(Move((r, c), (r+moveAmount, c-1), self.board, pawnPromotion=pawnPromotion))
                if (r+moveAmount, c - 1) == self.enPassantPossible:
                    attackingPiece = blockingPiece = False
                    if kingRow == r:
                        if kingCol < c:
                            insideRange = range(kingCol + 1, c-1)
                            outsideRange = range(c+1, 8)
                        else:
                            insideRange = range(kingCol - 1, c, -1)
                            outsideRange = range(c-2, -1, -1)
                        for i in insideRange:
                            if self.board[r][i] != "--":
                                blockingPiece = True
                        for i in outsideRange:
                            square = self.board[r][i]
                            if square[0] == opColor and square[1] == "R" or square[1] == "Q":
                                attackingPiece = True
                            elif square != "--":
                                blockingPiece = True
                    if not attackingPiece or blockingPiece:
                        moves.append(Move((r,c), (r+moveAmount, c-1), self.board, enPassant = True))

        if c+1 <= 7:
            if not piecePinned or pinDirection == (moveAmount, 1):
                if self.board[r+moveAmount][c+1][0]==opColor:
                    if r+moveAmount == backRow:
                        pawnPromotion = True
                    moves.append(Move((r, c), (r+moveAmount, c+1), self.board, pawnPromotion=pawnPromotion))
                if (r+moveAmount, c+1) == self.enPassantPossible:
                    attackingPiece = blockingPiece = False
                    if kingRow == r:
                        if kingCol < c:
                            insideRange = range(kingCol + 1, c)
                            outsideRange = range(c+2, 8)
                        else:
                            insideRange = range(kingCol - 1, c+1 , -1)
                            outsideRange = range(c-1, -1, -1)
                        for i in insideRange:
                            if self.board[r][i] != "--":
                                blockingPiece = True
                        for i in outsideRange:
                            square = self.board[r][i]
                            if square[0] == opColor and square[1] == "R" or square[1] == "Q":
                                attackingPiece = True
                            elif square != "--":
                                blockingPiece = True
                    if not attackingPiece or blockingPiece:
                        moves.append(Move((r,c), (r+moveAmount, c+1), self.board, enPassant = True))
                    
     

            #need to add promotion
    def getRookMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) -1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q':
                    self.pins.remove(self.pins[i])
                break
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        opColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1,8):
                toRow = r + d[0] * i
                toCol = c + d[1] * i
                if 0 <= toRow < 8 and 0 <= toCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[toRow][toCol]
                        if endPiece == "--":
                            moves.append(Move((r, c), (toRow, toCol), self.board))
                        elif endPiece[0] == opColor:
                            moves.append(Move((r, c), (toRow, toCol), self.board))
                            break
                        else:
                            break
                else:
                    break
    def getKnightMoves(self, r, c, moves):
        piecePinned = False
        for i in range(len(self.pins) -1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break
        knightmoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2),
                       (1, -2), (1, 2), (2, -1), (2, 1))
        opColor = "b" if self.whiteToMove else "w"
        for m in knightmoves:
            toRow = r + m[0]
            toCol = c + m[1]
            if 0 <= toRow < 8 and 0 <= toCol < 8:
                if not piecePinned:
                    endPiece = self.board[toRow][toCol]
                    if endPiece[0] == opColor or endPiece == "--":
                        moves.append(Move((r, c), (toRow, toCol), self.board))
    def getBishopMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) -1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        opColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1,8):
                toRow = r + d[0] * i
                toCol = c + d[1] * i
                if 0 <= toRow < 8 and 0 <= toCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[toRow][toCol]
                        if endPiece == "--":
                            moves.append(Move((r, c), (toRow, toCol), self.board))
                        elif endPiece[0] == opColor:
                            moves.append(Move((r, c), (toRow, toCol), self.board))
                            break
                        else:
                            break
                else:
                    break
    def getKingMoves(self, r, c, moves):
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        selfColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            toRow = r + rowMoves[i]
            toCol = c + colMoves[i]
            if 0 <= toRow < 8 and 0 <= toCol < 8:
                endPiece = self.board[toRow][toCol]
                if endPiece[0] != selfColor:
                    if selfColor == 'w':
                        self.whiteKingLocation = (toRow, toCol)
                    else:
                        self.blackKingLocation = (toRow, toCol)
                    inCheck, pins, checks = self.pinsAndChecks()
                    if not inCheck:
                        moves.append(Move((r, c), (toRow, toCol), self.board))
                    if selfColor == 'w':
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)
        self.getCastleMoves(r, c, moves, selfColor)
    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getCastleMoves(self, r, c, moves, selfColor):
        inCheck = self.squareUnderAttack(r, c, selfColor)
        if inCheck:
            return
        if (self.whiteToMove and self.whiteCastleKingside) or (not self.whiteToMove and self.blackCastleKingside):
            self.getKingsideCastleMoves(r, c, moves, selfColor)
        if (self.whiteToMove and self.whiteCastleQueenside) or (not self.whiteToMove and self.blackCastleQueenside):
            self.getQueensideCastleMoves(r, c, moves, selfColor)
    
    def getKingsideCastleMoves(self, r, c, moves, selfColor):
        if self.board[r][c+1] == "--" and self.board[r][c+2] == "--" and \
            not self.squareUnderAttack(r, c+1, selfColor) and not self.squareUnderAttack(r, c+2, selfColor):
            moves.append(Move((r, c), (r, c+2,), self.board, castle=True))

    def getQueensideCastleMoves(self, r, c, moves, selfColor):
        if self.board[r][c-1] == "--" and self.board[r][c-2] == "--" and self.board[r][c-3] == "--" and \
            not self.squareUnderAttack(r, c-1, selfColor) and not self.squareUnderAttack(r, c-2, selfColor):
            moves.append(Move((r, c), (r, c-2,), self.board, castle=True))

    def squareUnderAttack(self, r, c, selfColor):
        opColor = 'w' if selfColor =='b' else 'b'
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            for i in range(1, 8):
                toRow = r + d[0] *i
                toCol = c + d[1] *i
                if 0 <= toRow < 8 and 0 <= toCol < 8:
                    endPiece = self.board[toRow][toCol]
                    if endPiece[0] == selfColor:
                        break
                    elif endPiece[0] == opColor:
                        type = endPiece[1]
                        if (0 <= j <= 3 and type =='R') or \
                            (4 <= j <= 7 and type =='B') or \
                                (i == 1 and type =='P' and (
                                    (opColor == 'w' and 6 <= j <= 7) or (opColor == 'b' and 4 <= j <= 5))) or \
                                        (type == 'Q') or (i == 1 and type == 'K'):
                            return True
                        else:
                            break
                else:
                    break
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            toRow = r + m[0] *i
            toCol = c + m[1] *i
            if 0 <= toRow < 8 and 0 <= toCol < 8:
                endPiece = self.board[toRow][toCol]
                if endPiece[0] == opColor and endPiece[1] == 'N':
                    return True
        return False


class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

class Move():

    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                    "5": 3, "6": 2, "7": 1, "8": 0 }
    rowsToRanks = {v: k for k , v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                    "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k , v in filesToCols.items()}

    def __init__(self, startSq, toSq, board, enPassant = False, pawnPromotion = False, castle = False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.toRow = toSq[0]
        self.toCol = toSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.toRow][self.toCol]
        self.pawnPromotion = pawnPromotion 
        self.enPassant = enPassant
        self.castle = castle
        if enPassant:
            self.pieceCaptured = 'bP' if self.pieceMoved == 'wP' else 'wP'
        
        self.isCapture = self.pieceCaptured != "--"
        self.moveID = self.startRow * 1000  + self.startCol * 100 + self.toRow * 10 + self.toCol

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False


    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol,) + self.getRankFile(self.toRow, self.toCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
    
    def __str__(self):
        if self.castle:
            return "O-O" if self.toCol == 6 else "O-O-O"

        endSquare = self.getRankFile(self.toRow, self.toCol)

        if self.pieceMoved[1] == "P":
            if self.isCapture:
                return self.colsToFiles[self.startCol] + "x" + endSquare 
            else:
                return endSquare
            
        moveString = self.pieceMoved[1]
        if self.isCapture:
            moveString += "x"
        return moveString + endSquare













