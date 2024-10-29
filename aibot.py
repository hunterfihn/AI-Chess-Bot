import chess

# Value of pieces for evaluation
pieceValues = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0
}

def getDynamicDepth(board):
    """Dynamically adjust depth based on board state."""
    numPieces = len(board.piece_map())
    numLegalMoves = len(list(board.legal_moves))

    if numPieces > 20 and numLegalMoves > 25:
        return 3
    elif numPieces > 10:
        return 4
    else:
        return 6

def mateInOne(board):
    """Check if the AI can deliver checkmate in one move."""
    for move in board.legal_moves:
        board.push(move)
        if board.is_checkmate():
            board.pop()
            return True
        board.pop()
    return False

def evalboard(board):
    """Evaluate the board's position, considering various factors."""
    if board.is_checkmate():
        return -9999 if board.turn == chess.WHITE else 9999
    elif board.is_stalemate() or board.is_insufficient_material():
        return 0

    score = 0
    for pieceType in pieceValues:
        score += len(board.pieces(pieceType, chess.WHITE)) * pieceValues[pieceType]
        score -= len(board.pieces(pieceType, chess.BLACK)) * pieceValues[pieceType]

    # Additional scoring for center control
    center_squares = [chess.E4, chess.E5, chess.D4, chess.D5]
    for square in center_squares:
        if board.piece_at(square) is not None:
            if board.piece_at(square).color == chess.WHITE:
                score += 0.5
            else:
                score -= 0.5

    return score

def negamax(board, depth, alpha, beta):
    """Negamax with alpha-beta pruning."""
    if depth == 0 or board.is_game_over():
        return evalboard(board)

    maxEval = -float('inf')
    moves = sorted(board.legal_moves, key=lambda move: evalMove(board, move), reverse=True)  # Sort moves by evaluation
    for move in moves:
        board.push(move)
        
        eval = -negamax(board, depth - 1, -beta, -alpha)
        board.pop()

        maxEval = max(maxEval, eval)
        alpha = max(alpha, eval)
        if alpha >= beta:
            break

    return maxEval

def getAiMove(board):
    """Determine the best move for the AI."""
    depth = getDynamicDepth(board)

    # Check for immediate checkmate
    for move in board.legal_moves:
        board.push(move)
        if board.is_checkmate():
            board.pop()
            return move  # This move delivers checkmate
        board.pop()

    if mateInOne(board):
        # If there's a potential checkmate in 1 move, look for moves that block it
        for move in board.legal_moves:
            board.push(move)
            if not mateInOne(board):  # Make a move that prevents checkmate
                board.pop()
                return move
            board.pop()
    
    bestMove = None
    bestVal = -float('inf')

    # Sort moves based on evaluation to optimize search
    sortedMoves = sorted(board.legal_moves, key=lambda move: evalMove(board, move), reverse=True)
    for move in sortedMoves:
        board.push(move)
        moveVal = -negamax(board, depth - 1, -float('inf'), float('inf'))
        board.pop()

        if moveVal > bestVal:
            bestVal = moveVal
            bestMove = move

    return bestMove

def evalMove(board, move):
    """Evaluate individual moves for prioritization."""
    score = 0
    targPiece = board.piece_at(move.to_square)

    # Score for capturing pieces
    if targPiece:
        score += pieceValues[targPiece.piece_type] * 10  # Weight captures heavily

    # Score for central control
    centerSquares = [chess.D4, chess.E4, chess.D5, chess.E5]
    if move.to_square in centerSquares:
        score += 0.5

    # Score for giving check
    if board.gives_check(move):
        score += 1

    return score
