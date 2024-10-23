import pygame
import chess
import os

pygame.init()

#set board dimensions
width, height = 600, 600
rows, columns = 8, 8
sqSize = width//columns

#colors for light/dark squares
lightSq = (240, 217, 181)
darkSq = (181, 136, 99)

#set up display
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Chess")

#load pieces
pieces = {}

def loadPieceImgs():
    pieceNames = ['bR', 'bN', 'bB', 'bQ', 'bK', 'bP', 
                  'wR', 'wN', 'wB', 'wQ', 'wK', 'wP' ]
    for piece in pieceNames:
        pieces[piece] = pygame.transform.scale(
            pygame.image.load(os.path.join('images', piece + '.png')),
            (sqSize, sqSize)
        )

#draw board
def drawBoard(win):
    for row in range(rows):
        for col in range(columns):
            color = lightSq if (row + col) % 2 == 0 else darkSq
            pygame.draw.rect(win, color, (col * sqSize, row * sqSize, sqSize, sqSize))

#init board setup
def getInitState():
    return [
        ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
        ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
        [None] * 8,
        [None] * 8,
        [None] * 8,
        [None] * 8,
        ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
        ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
    ]

#draw pieces
def drawPieces(win, board, selectedPos):
    for row in range(rows):
        for col in range(columns):
            piece = board[row][col]
            if piece and (row, col) != selectedPos:
                win.blit(pieces[piece], (col * sqSize, row * sqSize))

def getBoardPos(mousePos):
    x, y = mousePos
    return y // sqSize, x // sqSize

def clampMousePos(mouseX, mouseY):
    clampedX = max(0, min(mouseX, width-sqSize//2))
    clampedY = max(0, min(mouseY, height-sqSize//2))
    return clampedX, clampedY

#main game loop
def main():
    clock = pygame.time.Clock()
    board = getInitState()
    loadPieceImgs()

    selectedPiece = None
    selectedPos = None
    dragging = False

    run = True
    while run:
        clock.tick(60)
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    row, col = getBoardPos(pygame.mouse.get_pos())
                    if board[row][col]:
                        selectedPiece = board[row][col]
                        selectedPos = (row, col)
                        dragging = True
                
                if event.type == pygame.MOUSEBUTTONUP and dragging:
                    row, col = getBoardPos(pygame.mouse.get_pos())

                    if selectedPiece and selectedPos:
                        board[selectedPos[0]][selectedPos[1]] = None
                        board[row][col] = selectedPiece
                        selectedPiece = None
                        dragging = False


        drawBoard(window)
        drawPieces(window, board, selectedPos)

        if selectedPiece and dragging:
            mouseX, mouseY = pygame.mouse.get_pos()
            clampedX, clampedY = clampMousePos(mouseX, mouseY)
            window.blit(pieces[selectedPiece], (clampedX - sqSize // 2, clampedY - sqSize // 2))
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()