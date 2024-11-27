import pygame as p
import ChessEngine
import chessAI

width = height = 768
dimension = 8
sqSize = height // dimension
maxFPS = 15
images = {}
p.display.set_caption('Chess')
icon = p.image.load('images/bQ.png')
p.display.set_icon(icon)

def loadImgs():
    pieces = ['wP', 'wR', 'wN', 'wB', 'wK', 'wQ',
              'bP', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        images[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (sqSize, sqSize))

def main():
    p.init()
    screen = p.display.set_mode((width, height))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.gameState()

    validMoves = gs.getValidMoves()
    moveMade = False
    animate = False

    loadImgs()

    running = True

    sqSelected = ()
    playerClicks = []
    gameOver = False

    playerOne = True #White -- true if human, false if AI
    playerTwo = False #Black -- true if human, false if AI

    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos()
                    col = location[0] // sqSize
                    row = location[1] // sqSize
                    if sqSelected == (row, col):
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 2:
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                animate = True
                                moveMade = True
                                sqSelected = ()
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]

            elif e.type == p.KEYDOWN:
                if e.key == p.K_LEFT:
                    gs.undoMove()
                    animate = False
                    moveMade = True
                    gameOver = False
                elif e.key == p.K_r:
                    gs = ChessEngine.gameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False

        #AI move finder
        if not gameOver and not humanTurn:
            AiMove = chessAI.findBestMove(gs, validMoves)
            if AiMove is None:
                AiMove = chessAI.findRandomMove(validMoves)
            gs.makeMove(AiMove)
            moveMade = True
            animate = True

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        drawGS(screen, gs, validMoves, sqSelected)

        if gs.checkmate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, "Black wins by checkmate")
            else:
                drawText(screen, "White wins by checkmate")
        elif gs.stalemate:
            gameOver = True
            drawText(screen, "Stalemate")

        clock.tick(maxFPS)
        p.display.flip()

def highlightSq(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            s = p.Surface ((sqSize, sqSize))
            s.set_alpha(150)
            s.fill(p.Color('yellow'))
            screen.blit(s, (c*sqSize, r*sqSize))
            s.fill(p.Color('light green'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.toCol*sqSize, move.toRow*sqSize))


def drawGS(screen, gs, validMoves, sqSelected):
    drawBoard(screen)
    highlightSq(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)


def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("bisque4")]
    for r in range(dimension):
        for c in range(dimension):
            color = colors[((r+c) % 2)]
            p.draw.rect(screen, color, p.Rect(c*sqSize, r*sqSize, sqSize, sqSize))

def drawPieces(screen, board):
    for r in range(dimension):
        for c in range(dimension):
            piece = board[r][c]
            if piece != "--":
                screen.blit(images[piece], p.Rect(c*sqSize, r*sqSize, sqSize, sqSize))

def animateMove(move, screen, board, clock):
    global colors
    dR = move.toRow - move.startRow
    dC = move.toCol - move.startCol
    framePerSquare = 3
    frameCount = (abs(dR) + abs(dC)) * framePerSquare
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        color = colors[(move.toRow + move.toCol) % 2]
        endSquare = p.Rect(move.toCol*sqSize, move.toRow*sqSize, sqSize, sqSize)
        p.draw.rect(screen, color, endSquare)
        if move.pieceCaptured != '--':
            screen.blit(images[move.pieceCaptured], endSquare)
        screen.blit(images[move.pieceMoved], p.Rect(c*sqSize, r*sqSize, sqSize, sqSize))
        p.display.flip()
        clock.tick(60)
    

def drawText(screen, text):
    font = p.font.SysFont("Helvetica", 32, True, False)
    textObject = font.render(text, 0, p.Color("gray"))
    textLocation = p.Rect(0, 0, width, height).move(width/2 - textObject.get_width()/2, height/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color("black"))
    screen.blit(textObject, textLocation.move(2,2))

if __name__ == "__main__":
    main()