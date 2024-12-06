import pygame as p
import ChessEngine
import chessAI
from multiprocessing import Process, Queue
import PIL
import os
import sys
import random as rd

boardWidth = boardHeight = 512
menuWidth = menuHeight = 512

labelPadding = 30

moveLogPanelWidth = 165
moveLogPanelHeight = boardHeight

totalWidth = boardWidth + moveLogPanelWidth + labelPadding
totalHeight = boardHeight + labelPadding


dimension = 8
sqSize = boardHeight // dimension
maxFPS = 15
images = {}


def resource_path(relative_path):
    try:
        # When running as a bundled executable
        base_path = sys._MEIPASS
    except AttributeError:
        # When running as a script
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

p.display.set_caption('Chess')
icon = p.image.load(resource_path('images/bQ.png'))
p.display.set_icon(icon)

def loadImgs():
    pieces = ['wP', 'wR', 'wN', 'wB', 'wK', 'wQ',
              'bP', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        images[piece] = p.transform.scale(
            p.image.load(resource_path(f"images/{piece}.png")), (sqSize, sqSize)
            )


def main():
    p.init()
    global running
    global playerOne
    global playerTwo
    global difficulty
    global difficultyChoice

    running = False
    playerOne = True #White -- true if human, false if AI
    playerTwo = False #Black -- true if human, false if AI
    
    difficulty = {0: "Easy",
                  1: "Medium",
                  2: "Hard",
                  3: "Expert"}
    
    difficultyChoice = 0
    

    def loadMenu():
        global running
        global playerOne
        global playerTwo
        global difficultyChoice

        menuScreen = p.display.set_mode((menuWidth, menuHeight))
        font = p.font.SysFont("Helvetica", 20, True, False)

        buttonWidth = 200
        buttonHeight = 50
        buttonColor = (0, 128, 255)  # Blue button

        # Button positions
        whitePlayerbuttonRect = p.Rect((menuWidth // 2 - buttonWidth // 2, menuHeight // 4), (buttonWidth, buttonHeight))
        blackPlayerbuttonRect = p.Rect((menuWidth // 2 - buttonWidth // 2, (menuHeight // 4) + 62), (buttonWidth, buttonHeight))
        difficultyButtonRect = p.Rect((menuWidth // 2 - buttonWidth // 2, (menuHeight // 4) + 125), (buttonWidth, buttonHeight))
        startButtonRect = p.Rect((menuWidth // 2 - buttonWidth // 2, menuHeight // 2 + 65), (buttonWidth, buttonHeight))


        def drawMenu():
            # Clear the screen
            menuScreen.fill("black")
            drawMenuText(menuScreen)

            # Update Player 1 button
            whitePlayerText = f"White: {'Human' if playerOne else 'AI'}"
            whitePlayerbuttonText = font.render(whitePlayerText, True, "white")
            whitePlayertextRect = whitePlayerbuttonText.get_rect(center=whitePlayerbuttonRect.center)
            p.draw.rect(menuScreen, buttonColor, whitePlayerbuttonRect)
            menuScreen.blit(whitePlayerbuttonText, whitePlayertextRect)

            # Update Player 2 button
            blackPlayerText = f"Black: {'Human' if playerTwo else 'AI'}"
            blackPlayerbuttonText = font.render(blackPlayerText, True, "white")
            blackPlayertextRect = blackPlayerbuttonText.get_rect(center=blackPlayerbuttonRect.center)
            p.draw.rect(menuScreen, buttonColor, blackPlayerbuttonRect)
            menuScreen.blit(blackPlayerbuttonText, blackPlayertextRect)


            # Update AI Difficulty button
            difficultText = f"AI Difficulty: {difficulty[difficultyChoice]}"
            difficultyButtonText = font.render(difficultText, True, "white")
            difficultyTextRect = difficultyButtonText.get_rect(center=difficultyButtonRect.center)
            p.draw.rect(menuScreen, buttonColor, difficultyButtonRect)
            menuScreen.blit(difficultyButtonText, difficultyTextRect)

            # Draw Start Game button
            buttonText = font.render("Start Game", True, "white")
            textRect = buttonText.get_rect(center=startButtonRect.center)
            p.draw.rect(menuScreen, buttonColor, startButtonRect)
            menuScreen.blit(buttonText, textRect)

            # Update the display
            p.display.flip()

        drawMenu()  # Initial menu draw

        runMenu = True
        while runMenu:
            for event in p.event.get():
                if event.type == p.QUIT:
                    runMenu = False
                if event.type == p.MOUSEBUTTONDOWN:
                    if startButtonRect.collidepoint(event.pos):  # Start game button
                        runMenu = False
                        running = True
                    if whitePlayerbuttonRect.collidepoint(event.pos):  # Player 1 button
                        playerOne = not playerOne
                        drawMenu()  # Redraw the menu to reflect changes
                    if blackPlayerbuttonRect.collidepoint(event.pos):  # Player 2 button
                        playerTwo = not playerTwo
                        drawMenu()  # Redraw the menu to reflect changes
                    if difficultyButtonRect.collidepoint(event.pos):  # Player 1 button
                        if (difficultyChoice < 3):
                            difficultyChoice +=1
                        else:
                            difficultyChoice=0 
                        drawMenu()  # Redraw the menu to reflect changes
            

    loadMenu()

    screen = p.display.set_mode((totalWidth, totalHeight))
    clock = p.time.Clock()
    screen.fill(p.Color("black"))
    gs = ChessEngine.gameState()

    moveLogFont = p.font.SysFont("Helvetica", 24, False, False)

    validMoves = gs.getValidMoves()
    moveMade = False
    animate = False


    loadImgs()


    sqSelected = ()
    playerClicks = []
    gameOver = False

    AIThinking = False
    moveFinderProcess = None
    moveUndone = False


    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos()
                    # Adjust for the label padding (subtract labelPadding from the x position)
                    col = (location[0] - labelPadding) // sqSize
                    row = location[1] // sqSize
                    # If the click is outside the board (e.g., in the label area), do nothing
                    if col < 0 or col >= dimension or row < 0 or row >= dimension:
                        continue
                    # If user clicks twice OR in move log, deselect
                    if sqSelected == (row, col) or col >= 8:
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 2 and humanTurn:
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
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = True

                elif e.key == p.K_r:
                    gs = ChessEngine.gameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = True

        #AI move finder
        if not gameOver and not humanTurn and not moveUndone:
            if not AIThinking:
                AIThinking = True
                returnQueue = Queue() #passing data between threads
                random = rd.random()
                depth = maxDepth = difficultyChoice + 1
                if difficultyChoice == 0: #easy mode
                    if(random > .75):
                        moveFinderProcess = Process(target=chessAI.findRandomMove, args=(validMoves, returnQueue))
                    else:
                        moveFinderProcess = Process(target=chessAI.findBestMove, args=(gs, validMoves, depth, maxDepth, returnQueue))

                elif difficultyChoice == 1: #medium mode
                    if(random > .85):
                        moveFinderProcess = Process(target=chessAI.findRandomMove, args=(validMoves, returnQueue))
                    else:
                        moveFinderProcess = Process(target=chessAI.findBestMove, args=(gs, validMoves, depth, maxDepth, returnQueue))

                elif difficultyChoice == 2: #hard mode
                    if(random > .95):
                        moveFinderProcess = Process(target=chessAI.findRandomMove, args=(validMoves, returnQueue))
                    else:
                        moveFinderProcess = Process(target=chessAI.findBestMove, args=(gs, validMoves, depth, maxDepth, returnQueue))

                elif difficultyChoice == 3: #expert mode
                    moveFinderProcess = Process(target=chessAI.findBestMove, args=(gs, validMoves, depth, maxDepth, returnQueue))

                moveFinderProcess.start()

            if not moveFinderProcess.is_alive():
                AiMove = returnQueue.get()
                if AiMove is None:
                    AiMove = chessAI.findRandomMoveNoQueue(validMoves)
                gs.makeMove(AiMove)
                moveMade = True
                animate = True
                AIThinking = False

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False
            moveUndone = False

        drawGS(screen, gs, validMoves, sqSelected, moveLogFont)

        if gs.checkmate or gs.stalemate:
            gameOver = True
            text = "Stalemate" if gs.stalemate else "Black Wins By Checkmate" if gs.whiteToMove else "White Wins By Checkmate"
            drawEndGameText(screen, text)

        clock.tick(maxFPS)
        p.display.flip()

def drawGS(screen, gs, validMoves, sqSelected, moveLogFont):
    drawBoard(screen)
    highlightSq(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)
    drawMoveLog(screen, gs, moveLogFont)

def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("bisque4")]
    font = p.font.SysFont("Helvetica", 18, True, False)

    # Draw squares, adjusted by labelPadding to leave space for labels
    for r in range(dimension):
        for c in range(dimension):
            color = colors[((r + c) % 2)]
            boardX = c * sqSize + labelPadding  # Offset by labelPadding
            boardY = r * sqSize
            p.draw.rect(screen, color, p.Rect(boardX, boardY, sqSize, sqSize))

    # Draw rank numbers (1-8) on the left side, outside the board
    for r in range(dimension):
        rankText = font.render(str(8 - r), True, p.Color("White"))
        textX = labelPadding // 2 - rankText.get_width() // 2
        textY = r * sqSize + sqSize // 2 - rankText.get_height() // 2
        screen.blit(rankText, (textX, textY))

    # Draw file letters (a-h) below the board, outside the board
    for c in range(dimension):
        fileText = font.render(chr(ord('a') + c), True, p.Color("White"))
        textX = c * sqSize + labelPadding + sqSize // 2 - fileText.get_width() // 2
        textY = boardHeight + labelPadding // 2 - fileText.get_height() // 2
        screen.blit(fileText, (textX, textY))

def highlightSq(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            s = p.Surface((sqSize, sqSize))
            s.set_alpha(125)
            s.fill(p.Color('blue'))
            # Add labelPadding to position the highlight correctly
            screen.blit(s, (c * sqSize + labelPadding, r * sqSize))  # Account for label padding

            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.toCol * sqSize + labelPadding, move.toRow * sqSize))  # Account for label padding

def drawPieces(screen, board):
    for r in range(dimension):
        for c in range(dimension):
            piece = board[r][c]
            if piece != "--":
                pieceX = c * sqSize + labelPadding  # Adjust by labelPadding
                pieceY = r * sqSize
                screen.blit(images[piece], p.Rect(pieceX, pieceY, sqSize, sqSize))

def drawMoveLog(screen, gs, font):
    moveLogRect = p.Rect(boardWidth + labelPadding, 0, moveLogPanelWidth, moveLogPanelHeight)  # Move log starts after label area
    p.draw.rect(screen, p.Color("black"), moveLogRect)
    moveLog = gs.moveLog
    moveTexts = []

    for i in range(0, len(moveLog), 2):
        moveString = str(i // 2 + 1) + ". " + str(moveLog[i]) + "    "
        if i + 1 < len(moveLog):
            moveString += str(moveLog[i + 1]) + " "
        moveTexts.append(moveString)

    padding = 5
    textY = padding
    for i in range(len(moveTexts)):
        text = moveTexts[i]
        textObject = font.render(text, True, p.Color("White"))
        textLocation = moveLogRect.move(padding, textY)
        screen.blit(textObject, textLocation)
        textY += textObject.get_height()

def animateMove(move, screen, board, clock):
    global colors
    dR = move.toRow - move.startRow
    dC = move.toCol - move.startCol
    framePerSquare = 3
    frameCount = (abs(dR) + abs(dC)) * framePerSquare
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR * frame / frameCount, move.startCol + dC * frame / frameCount)
        
        drawBoard(screen)
        drawPieces(screen, board)
        color = colors[(move.toRow + move.toCol) % 2]
        endSquare = p.Rect(move.toCol * sqSize + labelPadding, move.toRow * sqSize, sqSize, sqSize)  # Add labelPadding here
        p.draw.rect(screen, color, endSquare)
        
        if move.pieceCaptured != '--':
            if move.enPassant:
                enPassantRow = move.toRow + 1 if move.pieceCaptured[0] == "b" else move.toRow - 1
                endSquare = p.Rect(move.toCol * sqSize + labelPadding, enPassantRow * sqSize, sqSize, sqSize)  # Add labelPadding here
            screen.blit(images[move.pieceCaptured], endSquare)

        screen.blit(images[move.pieceMoved], p.Rect(c * sqSize + labelPadding, r * sqSize, sqSize, sqSize))  # Add labelPadding here
        p.display.flip()
        clock.tick(60)
    

def drawEndGameText(screen, text):
    font = p.font.SysFont("Helvetica", 32, True, False)
    textObject = font.render(text, 0, p.Color("gray"))
    textLocation = p.Rect(0, 0, boardWidth, boardHeight).move(boardWidth/2 - textObject.get_width()/2, boardHeight/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color("black"))
    screen.blit(textObject, textLocation.move(2,2))

def drawMenuText(menu):
    text = "Welcome to my Chess Bot"
    font = p.font.SysFont("Helvetica", 24, False, False)
    textObject = font.render(text, 0, p.Color("White"))
    textLocation = p.Rect(0, 0, menuWidth, menuHeight).move(menuWidth/2 - textObject.get_width()/2, menuHeight/8 - textObject.get_height()/2)
    menu.blit(textObject, textLocation)


if __name__ == "__main__":
    main()