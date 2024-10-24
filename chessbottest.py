import pygame
import os
import chess

# Initialize Pygame
pygame.init()
gameEnded = False

# Set board dimensions with space for labels (outside the board)
width, height = 640, 640  # Increased size to accommodate labels
rows, columns = 8, 8
sqSize = (width - 80) // columns  # Make squares slightly smaller to fit labels

# Colors for light/dark squares, highlights for selection, check, and checkmate
lightSq = (240, 217, 181)
darkSq = (181, 136, 99)
highlightYellow = (255, 255, 102)  # Light yellow for selected piece
checkBlue = (102, 178, 255)         # Blue for check
checkmateRed = (255, 51, 51)        # Red for checkmate
stalemateGrey = (128, 128, 128)     #Grey for stalemate
drawGrey = (128, 128, 128)          #Grey for draw
legalMoveGreen = (227, 179, 48)      # Green for legal move highlights

# Set up display
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Chess")

# Load pieces
pieces = {}

def loadPieceImgs():
    pieceNames = ['bR', 'bN', 'bB', 'bQ', 'bK', 'bP', 
                  'wR', 'wN', 'wB', 'wQ', 'wK', 'wP']
    for piece in pieceNames:
        pieces[piece] = pygame.transform.scale(
            pygame.image.load(os.path.join('images', piece + '.png')),
            (sqSize, sqSize)
        )

# Font for coordinates
font = pygame.font.SysFont('Arial', 24)

# Draw board with highlights and labels
def drawBoard(win, selectedPos=None, legalMoves=None, kingPos=None, kingPos2=None, checkState=None):
    # Draw the chessboard squares
    for row in range(rows):
        for col in range(columns):
            color = lightSq if (row + col) % 2 == 0 else darkSq
            
            # Check for highlighting based on king positions and check state
            if kingPos and (row, col) == kingPos:
                if checkState == 'checkmate':
                    color = checkmateRed
                elif checkState == 'check':
                    color = checkBlue
                elif checkState in ['stalemate', 'material draw', 'repetition draw', 'fifty-moves draw']:
                    color = drawGrey  # Change to drawGrey for draw states

            if kingPos2 and (row, col) == kingPos2:
                if checkState in ['stalemate', 'material draw', 'repetition draw', 'fifty-moves draw']:
                    color = drawGrey  # Change to drawGrey for draw states

            pygame.draw.rect(win, color, (col * sqSize + 40, row * sqSize + 40, sqSize, sqSize))
            if legalMoves and (row, col) in legalMoves:
                pygame.draw.rect(win, legalMoveGreen, (col * sqSize + 40, row * sqSize + 40, sqSize, sqSize), 5)

    # Draw coordinates (letters a-h and numbers 1-8) only on the bottom and left sides
    for i in range(columns):
        letter = font.render(chr(97 + i), True, (255, 255, 255))  # 'a' starts at ASCII 97
        
        # Adjust the y-position for bottom coordinates (closer to the board)
        win.blit(letter, (i * sqSize + sqSize // 2 + 40, height - 40))  # Bottom

        number = font.render(str(8 - i), True, (255, 255, 255))
        # Adjust the y-position for left coordinates (slightly up for centering)
        win.blit(number, (10, i * sqSize + sqSize // 2 + 30))  # Left

# Initialize board setup using python-chess
def getInitState():
    return chess.Board()  # Create a new chess board

# Convert chess piece representation to image key
def pieceToKey(piece):
    if piece.color == chess.WHITE:
        return f'w{piece.symbol().upper()}'
    else:
        return f'b{piece.symbol().upper()}'

# Draw pieces
def drawPieces(win, board, selectedPiece, selectedPos):
    for row in range(rows):
        for col in range(columns):
            piece = board.piece_at(chess.square(col, 7 - row))
            if piece and (selectedPos is None or (row, col) != selectedPos):
                piece_key = pieceToKey(piece)
                win.blit(pieces[piece_key], (col * sqSize + 40, row * sqSize + 40))

def getBoardPos(mousePos):
    x, y = mousePos
    return (y - 40) // sqSize, (x - 40) // sqSize

# Get the king's position and check/checkmate state
def getKingInfo(board):
    whiteKingSquare = board.king(chess.WHITE)
    blackKingSquare = board.king(chess.BLACK)

    currentKingPos = None
    currentKingPos2 = None
    check_state = None

    if board.is_stalemate():
        currentKingPos = (7 - chess.square_rank(whiteKingSquare), chess.square_file(whiteKingSquare))
        currentKingPos2 = (7 - chess.square_rank(blackKingSquare), chess.square_file(blackKingSquare))
        check_state = 'stalemate'
    
    elif board.is_insufficient_material():
        currentKingPos = (7 - chess.square_rank(whiteKingSquare), chess.square_file(whiteKingSquare))
        currentKingPos2 = (7 - chess.square_rank(blackKingSquare), chess.square_file(blackKingSquare))
        check_state = 'material draw'

    elif board.is_fivefold_repetition():
        currentKingPos = (7 - chess.square_rank(whiteKingSquare), chess.square_file(whiteKingSquare))
        currentKingPos2 = (7 - chess.square_rank(blackKingSquare), chess.square_file(blackKingSquare))
        check_state = 'repetition draw'
    
    elif board.is_fifty_moves():
        currentKingPos = (7 - chess.square_rank(whiteKingSquare), chess.square_file(whiteKingSquare))
        currentKingPos2 = (7 - chess.square_rank(blackKingSquare), chess.square_file(blackKingSquare))
        check_state = 'fifty-moves draw'

    elif board.is_checkmate():
        if board.turn == chess.WHITE:
            currentKingPos = (7 - chess.square_rank(whiteKingSquare), chess.square_file(whiteKingSquare))
        else:
            currentKingPos = (7 - chess.square_rank(blackKingSquare), chess.square_file(blackKingSquare))
        check_state = 'checkmate'

    elif board.is_check():
        if board.turn == chess.WHITE:
            currentKingPos = (7 - chess.square_rank(whiteKingSquare), chess.square_file(whiteKingSquare))
        else:
            currentKingPos = (7 - chess.square_rank(blackKingSquare), chess.square_file(blackKingSquare))
        check_state = 'check'

    return currentKingPos, currentKingPos2, check_state

# Get legal moves for a selected piece
def getLegalMoves(board, pieceSquare):
    legalMoves = []
    for move in board.legal_moves:
        if move.from_square == pieceSquare:
            targetRow, targetCol = 7 - chess.square_rank(move.to_square), chess.square_file(move.to_square)
            legalMoves.append((targetRow, targetCol))
    return legalMoves


def handlePromotionGUI():
    # Set up the promotion window dimensions and layout
    promotionWindowWidth = 320
    promotionWindowHeight = 80
    promotionWindow = pygame.Surface((promotionWindowWidth, promotionWindowHeight))
    
    # Piece types in order: Queen, Rook, Bishop, Knight
    promotionPieces = ['wQ', 'wR', 'wB', 'wN']
    promotionPieceTypes = [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]
    
    # Draw the promotion options on the window
    for i, pieceKey in enumerate(promotionPieces):
        pieceImage = pieces[pieceKey]
        pieceRect = pygame.Rect(i * 80, 0, 80, 80)
        promotionWindow.blit(pieceImage, pieceRect)
    
    # Display the promotion window in the center of the main window
    window.blit(promotionWindow, (width // 2 - promotionWindowWidth // 2, height // 2 - promotionWindowHeight // 2))
    pygame.display.update()

    # Wait for the user to click on a promotion piece
    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouseX, mouseY = event.pos
                # Calculate which piece was clicked based on the mouse position
                relativeX = mouseX - (width // 2 - promotionWindowWidth // 2)
                relativeY = mouseY - (height // 2 - promotionWindowHeight // 2)
                
                if 0 <= relativeY < promotionWindowHeight and 0 <= relativeX < promotionWindowWidth:
                    selectedIndex = relativeX // 80  # 80px per piece
                    return promotionPieceTypes[selectedIndex]  # Return the selected promotion piece

def drawText(win, text, position, color=(255, 0, 0), font_size=24):
    font = pygame.font.SysFont('Arial', font_size)
    text_surface = font.render(text, True, color)
    win.blit(text_surface, position)

# Main game loop
def main():
    global gameEnded
    clock = pygame.time.Clock()
    board = getInitState()  # Initialize the chess board
    loadPieceImgs()

    selectedPiece = None
    selectedPos = None
    dragging = False
    legalMovesVisible = False
    legalMoves = []

    run = True
    while run:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                row, col = getBoardPos(pygame.mouse.get_pos())
                if 0 <= row < 8 and 0 <= col < 8:
                    piece = board.piece_at(chess.square(col, 7 - row))  # Get the piece from the board
                    if piece and piece.color == board.turn:  # Allow selecting piece if it’s the current player's turn
                        selectedPiece = piece
                        selectedPos = (row, col)
                        legalMoves = getLegalMoves(board, chess.square(col, 7 - row))  # Get legal moves for the selected piece
                        dragging = True

            if event.type == pygame.MOUSEBUTTONUP and dragging:
                row, col = getBoardPos(pygame.mouse.get_pos())
                destSquare = chess.square(col, 7 - row)

                if selectedPiece:
                    fromSquare = chess.square(selectedPos[1], 7 - selectedPos[0])

                    # Check for pawn promotion before pushing the move
                    if selectedPiece.piece_type == chess.PAWN and (row == 0 or row == 7):
                        # Handle pawn promotion
                        promote_to = handlePromotionGUI()  # Get the promotion piece from user input
                        move = chess.Move(fromSquare, destSquare, promotion=promote_to)  # Create the promotion move
                    else:
                        move = chess.Move(fromSquare, destSquare)  # Regular move for non-pawn or non-promotion

                    # Now check if the move is legal and push it to the board
                    if move in board.legal_moves:
                        board.push(move)  # Push the move, either regular or promotion

                # Reset state
                selectedPiece = None
                selectedPos = None
                legalMoves = []  # Clear legal moves after a move
                dragging = False


        # Get king position and check state after every move
        kingPos, kingpos2, checkState = getKingInfo(board)

        window.fill((0, 0, 0))  # Change to your background color

        drawBoard(window, selectedPos, legalMoves, kingPos, kingpos2, checkState)
        drawPieces(window, board, selectedPiece, selectedPos)

        

        if checkState == 'check':
            message = "Check!"
            drawText(window, message, position=(width // 2 - 50, 10))
        
        if checkState in ['stalemate', 'material draw', 'repetition draw', 'fifty-moves draw', 'checkmate']:
            message = checkState.replace('_', ' ').capitalize() + '!' 
            drawText(window, message, position=(width // 2 - 50, 10))
            gameEnded = True 

             # Wait for the user to close the window after game over
            while gameEnded:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False
                        gameEnded = False
                        break
                pygame.display.update()

        if selectedPiece and dragging:
            mouseX, mouseY = pygame.mouse.get_pos()
    
            # Constrain the position within the board
            if 60 <= mouseX <= width - 60 and 60 <= mouseY <= height - 60:
                window.blit(pieces[pieceToKey(selectedPiece)], (mouseX - sqSize // 2, mouseY - sqSize // 2))

        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()
