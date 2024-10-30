
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

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.toRow][move.toCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.toRow][move.toCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove

    def getValidMoves(self):
        return self.getAllPossibleMoves()

    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if(turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    if piece == 'P':
                        self.getPawnMoves(r, c, moves)
                    elif piece =='R':
                        self.getRookMoves(r, c, moves)
                    elif piece =='N':
                        self.getKnightMoves(r, c, moves)
                    elif piece =='B':
                        self.getBishopMoves(r, c, moves)
                    elif piece =='K':
                        self.getKingMoves(r, c, moves)
                    elif piece =='Q':
                        self.getQueenMoves(r, c, moves)
        return moves

    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove:
            if self.board[r-1][c] == "--":
                moves.append(Move((r, c), (r-1, c), self.board))
                if r == 6 and self.board[r-2][c] == "--":
                    moves.append(Move((r, c), (r-2, c), self.board))
            if c - 1 >= 0:
                if self.board[r-1][c-1][0] == 'b':
                    moves.append(Move((r, c), (r-1, c-1), self.board))
            if c + 1 <= 7:
                if self.board[r-1][c+1][0] == 'b':
                    moves.append(Move((r, c), (r-1, c+1), self.board))
        else:
            if self.board[r+1][c] == "--":
                moves.append(Move((r, c), (r+1, c), self.board))
                if r == 1 and self.board[r+2][c] == "--":
                    moves.append(Move((r, c), (r+2, c), self.board))
            if c - 1 >= 0:
                if self.board[r+1][c-1][0] == 'w':
                    moves.append(Move((r, c), (r+1, c-1), self.board))
            if c + 1 <= 7:
                if self.board[r+1][c+1][0] == 'w':
                    moves.append(Move((r, c), (r+1, c+1), self.board))

            #need to add promotion
    def getRookMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        opColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1,8):
                toRow = r + d[0] * i
                toCol = c + d[1] * i
                if 0 <= toRow < 8 and 0 <= toCol < 8:
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
        knightmoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2),
                       (1, -2), (1, 2), (2, -1), (2, 1))
        opColor = "b" if self.whiteToMove else "w"
        for m in knightmoves:
            toRow = r + m[0]
            toCol = c + m[1]
            if 0 <= toRow < 8 and 0 <= toCol < 8:
                endPiece = self.board[toRow][toCol]
                if endPiece[0] == opColor or endPiece == "--":
                    moves.append(Move((r, c), (toRow, toCol), self.board))
    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        opColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1,8):
                toRow = r + d[0] * i
                toCol = c + d[1] * i
                if 0 <= toRow < 8 and 0 <= toCol < 8:
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
        kingMoves = ((-1, -1), (-1, 0), (-1, 1), (0, -1),
                     (0, 1), (1, -1), (1, 0), (1, 1))
        opColor = "b" if self.whiteToMove else "w"
        for i in range(8):
            toRow = r + kingMoves[i][0]
            toCol = c + kingMoves[i][1]
            if 0 <= toRow < 8 and 0 <= toCol < 8:
                endPiece = self.board[toRow][toCol]
                if endPiece[0] == opColor or endPiece == "--":
                    moves.append(Move((r, c), (toRow, toCol), self.board))
    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)



class Move():

    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                    "5": 3, "6": 2, "7": 1, "8": 0 }
    rowsToRanks = {v: k for k , v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                    "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k , v in filesToCols.items()}

    def __init__(self, startSq, toSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.toRow = toSq[0]
        self.toCol = toSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.toRow][self.toCol]
        self.moveID = self.startRow * 1000  + self.startCol * 100 + self.toRow * 10 + self.toCol

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False


    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol,) + self.getRankFile(self.toRow, self.toCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]