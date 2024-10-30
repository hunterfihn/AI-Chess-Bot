import chess
import chess.polyglot
import random

# Enhanced values to reflect nuanced strategic worth of each piece type
pieceValues = {
    chess.PAWN: 1,
    chess.KNIGHT: 3.2,
    chess.BISHOP: 3.3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0
}

# Piece-square tables (simplified)
pieceSquareTable = {
    chess.PAWN: [0, 0, 0, 0, 0, 0, 0, 0,   # Rank 8
                  5, 5, 5, 5, 5, 5, 5, 5,  # Rank 7
                  2, 2, 3, 3, 3, 3, 0, 0,  # Rank 6
                  0, 0, 1, 1, 1, 1, 0, 0,  # Rank 5
                  0, 0, 0, 0, 0, 0, 0, 0,  # Rank 4
                  0, 0, 0, 0, 0, 0, 0, 0,  # Rank 3
                  0, 0, 0, 0, 0, 0, 0, 0,  # Rank 2
                  0, 0, 0, 0, 0, 0, 0, 0], # Rank 1
    chess.KNIGHT: [-5, -4, -3, -2, -2, -3, -4, -5,
                    -4, -2, 0, 1, 1, 0, -2, -4,
                    -3, 1, 2, 3, 3, 2, 1, -3,
                    -2, 1, 2, 3, 3, 2, 1, -2,
                    -2, 0, 1, 2, 2, 1, 0, -2,
                    -3, -2, 0, 1, 1, 0, -2, -3,
                    -4, -5, -4, -3, -3, -4, -5, -4,
                    -5, -4, -3, -2, -2, -3, -4, -5],
    chess.BISHOP: [-2, -1, -1, -1, -1, -1, -1, -2,
                    -1, 0, 0, 1, 1, 0, 0, -1,
                    -1, 0, 1, 1, 1, 1, 0, -1,
                    -1, 1, 1, 1, 1, 1, 1, -1,
                    -1, 1, 1, 1, 1, 1, 1, -1,
                    -1, 0, 1, 1, 1, 0, 0, -1,
                    -1, 0, 0, 1, 1, 0, 0, -1,
                    -2, -1, -1, -1, -1, -1, -1, -2],
    chess.ROOK: [0, 0, 0, 0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0, 0, 0, 0,
                  5, 10, 10, 10, 10, 10, 10, 5,
                  0, 0, 0, 0, 0, 0, 0, 0],
    chess.QUEEN: [-20, -10, -10, -5, -5, -10, -10, -20,
                   -10, 0, 5, 5, 5, 5, 0, -10,
                   -10, 5, 5, 5, 5, 5, 5, -10,
                   -5, 5, 5, 5, 5, 5, 5, -5,
                   0, 5, 5, 5, 5, 5, 5, 0,
                   -10, 0, 5, 5, 5, 5, 0, -10,
                   -20, -10, -10, -5, -5, -10, -10, -20,
                   0, 0, 0, 0, 0, 0, 0, 0],
}

# Central and extended central squares
centerSquares = [chess.D4, chess.E4, chess.D5, chess.E5]
extendedCenter = centerSquares + [chess.C3, chess.C6, chess.F3, chess.F6]

def getOpeningMove(board):
    """Get a random opening move from a polyglot opening book."""
    try:
        with chess.polyglot.open_reader("gm2001.bin") as reader:
            # Collect all possible moves for the current position
            moves = [entry.move for entry in reader.find_all(board)]
            if moves:
                # Randomly select one of the possible moves
                return random.choice(moves)
    except IndexError:
        return None

def getDynamicDepth(board):
    """Adjust search depth based on board complexity and game stage."""
    numPieces = len(board.piece_map())
    numLegalMoves = len(list(board.legal_moves))
    if numPieces > 20 and numLegalMoves > 25:
        return 4  # Early game
    elif numPieces > 10:
        return 5  # Mid-game
    elif numPieces > 4:
        return 6  # Endgame
    else:
        return 7  # Simple endgame situations

def evalBoard(board):
    """Evaluate the board considering material, center control, and positional factors."""
    if board.is_checkmate():
        return -9999 if board.turn == chess.WHITE else 9999
    elif board.is_stalemate() or board.is_insufficient_material():
        return 0

    score = 0
    for pieceType in pieceValues:
        # Count material
        score += len(board.pieces(pieceType, chess.WHITE)) * pieceValues[pieceType]
        score -= len(board.pieces(pieceType, chess.BLACK)) * pieceValues[pieceType]

        # Add piece-square table value, now also handling the KING
        for square in board.pieces(pieceType, chess.WHITE):
            try:
                index = chess.square_rank(square) * 8 + chess.square_file(square)
                score += pieceSquareTable[pieceType][index]
            except KeyError:
                print(f"KeyError for WHITE {pieceType} at square {square} (index {index})")
                raise
        for square in board.pieces(pieceType, chess.BLACK):
            try:
                index = chess.square_rank(square) * 8 + chess.square_file(square)
                score -= pieceSquareTable[pieceType][index]
            except KeyError:
                print(f"KeyError for BLACK {pieceType} at square {square} (index {index})")
                raise

    # Center control
    score += evaluateCenterControl(board)
    
    # Piece activity
    score += evaluatePieceActivity(board)
    
    # King safety
    score += evaluateKingSafety(board)
    
    # Evaluate pawn structure
    score += evaluatePawnStructure(board)

    return score




def evaluateCenterControl(board):
    """Score based on control of central squares."""
    score = 0
    for square in centerSquares:
        piece = board.piece_at(square)
        if piece:
            score += 0.5 if piece.color == chess.WHITE else -0.5
    for square in extendedCenter:
        piece = board.piece_at(square)
        if piece:
            score += 0.25 if piece.color == chess.WHITE else -0.25
    return score

def evaluatePieceActivity(board):
    """Score based on piece activity and mobility."""
    score = 0
    for square, piece in board.piece_map().items():
        if piece.color == chess.WHITE:
            score += len(board.attacks(square)) * 0.1  # More attacks = better activity
        else:
            score -= len(board.attacks(square)) * 0.1  # Opponent's activity negatively impacts score
    return score

def evaluateKingSafety(board):
    """Score based on king safety and pawn structure around the king."""
    score = 0
    king_square = board.king(chess.WHITE)
    if board.is_attacked_by(chess.BLACK, king_square):
        score -= 5.0  # Penalty for being attacked
    # Consider pawn structure around the king
    king_pawn_structure = [chess.F2, chess.G2, chess.H2]
    for square in king_pawn_structure:
        if board.piece_at(square) and board.piece_at(square).piece_type == chess.PAWN:
            score += 0.5  # Bonus for having pawns protecting the king
    return score

def evaluatePawnStructure(board):
    """Score based on the structure of pawns."""
    score = 0
    pawns_white = board.pieces(chess.PAWN, chess.WHITE)
    pawns_black = board.pieces(chess.PAWN, chess.BLACK)
    
    # Evaluate isolated pawns
    for square in pawns_white:
        if not any(board.piece_at(square + offset) for offset in [-1, 1]):
            score -= 1  # Penalize isolated pawns
    for square in pawns_black:
        if not any(board.piece_at(square + offset) for offset in [-1, 1]):
            score += 1  # Penalize isolated pawns

    # Evaluate doubled pawns
    white_pawn_files = [0] * 8
    black_pawn_files = [0] * 8
    for square in pawns_white:
        white_pawn_files[chess.square_file(square)] += 1
    for square in pawns_black:
        black_pawn_files[chess.square_file(square)] += 1

    score -= sum((count - 1) for count in white_pawn_files if count > 1)  # Penalize doubled pawns
    score += sum((count - 1) for count in black_pawn_files if count > 1)  # Penalize doubled pawns

    return score

def evalMove(board, move):
    """Evaluate individual moves for tactical opportunities."""
    score = 0
    targetPiece = board.piece_at(move.to_square)

    # High priority for capturing valuable pieces, especially the queen
    if targetPiece:
        if targetPiece.piece_type == chess.QUEEN:
            score += pieceValues[targetPiece.piece_type] * 20  # Significantly reward capturing the queen
        else:
            score += pieceValues[targetPiece.piece_type] * 10  # Reward for capturing other pieces

    # Check if the move is defending the queen
    if board.piece_at(move.from_square).piece_type == chess.QUEEN:
        if board.is_attacked_by(not board.turn, move.to_square):
            score -= 10  # Penalize moves that leave the queen in danger

    # Prioritize central control
    if move.to_square in centerSquares:
        score += 2.0
    elif move.to_square in extendedCenter:
        score += 1

    # Penalize retreating moves
    from_square = move.from_square
    if board.piece_at(from_square).piece_type != chess.KING and board.fullmove_number < 10:
        if chess.square_rank(move.to_square) < chess.square_rank(from_square):
            score -= 0.5

    # Extra points for checks
    if board.gives_check(move):
        score += 1.5

    # Penalize leaving the queen unprotected
    if targetPiece and targetPiece.piece_type == chess.QUEEN and not board.is_attacked_by(board.turn, move.to_square):
        score -= 5.0

    return score

def negamax(board, depth, alpha, beta):
    """Negamax algorithm with alpha-beta pruning."""
    if depth == 0 or board.is_game_over():
        return evalBoard(board)

    maxEval = -float('inf')
    moves = sorted(board.legal_moves, key=lambda move: evalMove(board, move), reverse=True)
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
    """Find the best move based on the opening book and negamax strategy."""
    opening = getOpeningMove(board)
    if opening:
        return opening

    depth = getDynamicDepth(board)
    bestMove = None
    bestVal = -float('inf')

    # Check for immediate checkmate
    for move in board.legal_moves:
        board.push(move)
        if board.is_checkmate():
            board.pop()
            return move
        board.pop()

    # Evaluate all legal moves
    sortedMoves = sorted(board.legal_moves, key=lambda move: evalMove(board, move), reverse=True)
    for move in sortedMoves:
        board.push(move)
        moveVal = -negamax(board, depth - 1, -float('inf'), float('inf'))
        board.pop()

        if moveVal > bestVal:
            bestVal = moveVal
            bestMove = move

    return bestMove
