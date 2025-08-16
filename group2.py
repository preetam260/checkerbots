import random
from copy import deepcopy
import time

# Group1 function with strategic enhancements, using the full 20 seconds efficiently
def group2(self, board):
    transposition_table = {}

    # Helper function for move ordering with a focus on spreading pieces, central control, and protecting the king row
    def order_moves(possible_moves):
        capture_moves = []
        king_moves = []
        center_moves = []
        spread_moves = []
        regular_moves = []

        for move in possible_moves:
            for choice in move[2]:
                piece_x, piece_y = move[0], move[1]
                dest_x, dest_y = choice

                # Check if the move is a capturing move
                if abs(dest_x - piece_x) > 1:
                    capture_moves.append((move, choice))
                # Check if the move will result in a kinging (last row)
                elif (self.color == 'GREY' and dest_y == 0) or (self.color == 'PURPLE' and dest_y == 7):
                    king_moves.append((move, choice))
                # Prioritize moves towards the center
                elif dest_x in [2, 3, 4, 5] and dest_y in [2, 3, 4, 5]:
                    center_moves.append((move, choice))
                else:
                    # Spread out the pieces (avoid clumping)
                    distance_from_others = distance_to_other_pieces(board, dest_x, dest_y)
                    spread_moves.append((move, choice, distance_from_others))

        # Prioritize capture moves > kinging moves > center moves > spread moves > regular moves
        spread_moves = sorted(spread_moves, key=lambda x: -x[2])  # Prioritize moves that spread out the pieces
        spread_moves = [(move, choice) for (move, choice, dist) in spread_moves]  # Remove the distance from the list

        return capture_moves + king_moves + center_moves + spread_moves + regular_moves

    # Calculate the distance to other pieces (helps avoid clustering)
    def distance_to_other_pieces(board, dest_x, dest_y):
        total_distance = 0
        piece_count = 0

        for i in range(8):
            for j in range(8):
                if (i, j) != (dest_x, dest_y):
                    square_piece = board.getSquare(i, j).squarePiece
                    if square_piece is not None and square_piece.color == self.color:
                        distance = abs(i - dest_x) + abs(j - dest_y)
                        total_distance += distance
                        piece_count += 1

        return total_distance / piece_count if piece_count > 0 else 0  # Average distance from other pieces

    # Quiescence search to extend the search beyond captures and avoid the horizon effect
    def quiescence_search(board, alpha, beta, maximizing_player, depth_limit=3):
        if depth_limit == 0:
            return self.evaluate(board)

        stand_pat = self.evaluate(board)

        # Alpha-beta pruning in quiescence search
        if stand_pat >= beta:
            return beta
        if alpha < stand_pat:
            alpha = stand_pat

        # Get possible capture moves
        possible_moves = self.getPossibleMoves(board)
        capture_moves = [move for move in possible_moves if abs(move[2][0][0] - move[0]) > 1]  # Capturing moves only

        # Extend the search for capturing moves
        for move in capture_moves:
            for choice in move[2]:
                simulated_board = deepcopy(board)
                self.moveOnBoard(simulated_board, move[:2], choice)

                if maximizing_player:
                    eval = quiescence_search(simulated_board, alpha, beta, False, depth_limit - 1)
                    if eval >= beta:
                        return beta
                    alpha = max(alpha, eval)
                else:
                    eval = quiescence_search(simulated_board, alpha, beta, True, depth_limit - 1)
                    if eval <= alpha:
                        return alpha
                    beta = min(beta, eval)

        return alpha if maximizing_player else beta

    # Enhanced heuristic evaluation function focusing on central control, spreading pieces, long-term mobility, and formation
    def evaluate(board):
        score = 0
        capture_bonus = 10  # Bonus for potential captures
        king_bonus = 50  # Bonus for kings
        piece_bonus = 5  # Regular piece bonus
        mobility_weight = 3  # Weight for mobility (number of moves)
        center_bonus = 5  # Weight for central control
        king_safety_bonus = 15  # Bonus for keeping kings safe
        spread_bonus = 10  # Bonus for spreading pieces across the board
        opponent_mobility_penalty = 2  # Penalty to opponent's mobility
        king_row_protection_bonus = 25  # Protecting key squares on king row

        my_pieces = 0
        opponent_pieces = 0
        my_kings = 0
        opponent_kings = 0
        my_mobility = 0
        opponent_mobility = 0
        my_capture_moves = 0
        opponent_capture_moves = 0
        piece_cluster_penalty = 0
        king_row_defenders = 0

        # Helper function to check if a piece is protected
        def has_protection(x, y, board):
            for i in range(max(0, x-1), min(8, x+2)):
                for j in range(max(0, y-1), min(8, y+2)):
                    if i == x and j == y:
                        continue
                    square_piece = board.getSquare(i, j).squarePiece
                    if square_piece is not None and square_piece.color == self.color:
                        return True  # The piece is protected
            return False

        # Evaluate the board by iterating through all squares
        for i in range(8):
            for j in range(8):
                square_piece = board.getSquare(i, j).squarePiece
                if square_piece is not None:
                    if square_piece.color == self.color:
                        my_pieces += 1
                        if square_piece.king:
                            my_kings += 1
                            score += king_bonus

                            # Check king safety (prefer to keep kings away from the edges)
                            if j in [0, 7]:  # Kings on the edge
                                score -= king_safety_bonus

                        else:
                            score += piece_bonus

                        # Add bonus for central control
                        if i in [2, 3, 4, 5] and j in [2, 3, 4, 5]:
                            score += center_bonus

                        # Penalize for clustering pieces
                        cluster_penalty = 1 / distance_to_other_pieces(board, i, j)
                        piece_cluster_penalty += cluster_penalty

                        # Penalize for unprotected pieces
                        if not has_protection(i, j, board):
                            score -= 10  # Penalty for unprotected pieces

                        # Bonus for protecting key king row squares
                        if (self.color == 'GREY' and j == 7) or (self.color == 'PURPLE' and j == 0):
                            king_row_defenders += 1
                            if king_row_defenders >= 2:  # Ensure back row is properly defended
                                score += king_row_protection_bonus

                    else:
                        opponent_pieces += 1
                        if square_piece.king:
                            opponent_kings += 1
                            score -= king_bonus
                        else:
                            score -= piece_bonus

        # Mobility (number of moves available for each side)
        my_mobility = len(self.getPossibleMoves(board))

        # Temporarily switch turn to the opponent to get their moves
        original_turn = self.game.turn
        self.game.turn = 'PURPLE' if self.color == 'GREY' else 'GREY'
        opponent_mobility = len(self.getPossibleMoves(board))
        self.game.turn = original_turn  # Restore the bot's turn

        # Add mobility score (more mobility is better)
        score += mobility_weight * my_mobility
        score -= opponent_mobility_penalty * opponent_mobility  # Penalize opponent mobility

        # Capture Threats (potential capture moves in the next turn)
        for move in self.getPossibleMoves(board):
            if abs(move[2][0][0] - move[0]) > 1:  # If the move is a capture
                my_capture_moves += 1

        # Switch to opponent's turn temporarily to calculate their capture moves
        self.game.turn = 'PURPLE' if self.color == 'GREY' else 'GREY'
        for move in self.getPossibleMoves(board):
            if abs(move[2][0][0] - move[0]) > 1:
                opponent_capture_moves += 1
        self.game.turn = original_turn  # Restore the bot's turn

        # Add capture bonus
        score += capture_bonus * (my_capture_moves - opponent_capture_moves)

        # Add final score based on piece count and king count
        score += (my_pieces - opponent_pieces) * 10  # Bonus for having more pieces
        score += (my_kings - opponent_kings) * 20  # Kings are highly valuable

        # Add spread bonus and piece clustering penalty
        score += spread_bonus - piece_cluster_penalty

        return score

    # Minimax with Alpha-Beta Pruning and Transposition Table
    def minimax(board, depth, alpha, beta, maximizing_player):
        board_hash = str(board)  # Create a hashable representation of the board
        if board_hash in transposition_table:
            return transposition_table[board_hash]  # Return cached evaluation

        if depth == 0 or self.endGameCheck(board):
            eval = quiescence_search(board, alpha, beta, maximizing_player)  # Apply quiescence search instead of just evaluation
            transposition_table[board_hash] = eval  # Store evaluation in transposition table
            return eval

        possible_moves = self.getPossibleMoves(board)  # Get all possible moves
        ordered_moves = order_moves(possible_moves)  # Order moves to improve pruning

        if maximizing_player:
            max_eval = float('-inf')
            best_move = None
            best_choice = None
            for move, choice in ordered_moves:
                simulated_board = deepcopy(board)
                self.moveOnBoard(simulated_board, move[:2], choice)

                # Recursively call minimax
                eval = minimax(simulated_board, depth - 1, alpha, beta, False)

                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                    best_choice = choice

                alpha = max(alpha, eval)
                if beta <= alpha:
                    break  # Beta cutoff

            # If at depth 0 (initial call), return the best move and choice
            if depth == max_depth:
                return best_move, best_choice
            else:
                transposition_table[board_hash] = max_eval  # Store in transposition table
                return max_eval

        else:  # Minimizing player
            min_eval = float('inf')
            for move, choice in ordered_moves:
                simulated_board = deepcopy(board)
                self.moveOnBoard(simulated_board, move[:2], choice)

                # Recursively call minimax
                eval = minimax(simulated_board, depth - 1, alpha, beta, True)

                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break  # Alpha cutoff

            transposition_table[board_hash] = min_eval  # Store in transposition table
            return min_eval

    # Define the depth limit for minimax and adjust based on time remaining
    max_depth = 3  # You can tweak this to adjust performance vs. search depth

    # Measure time to ensure the function stays within 20 seconds
    start_time = time.time()
    time_limit = 20

    best_move, best_choice = minimax(board, max_depth, float('-inf'), float('inf'), True)

    # Check if the time limit has been reached, adjust depth dynamically if needed
    if time.time() - start_time < time_limit and best_move is None:
        max_depth += 1  # Increase depth for more exhaustive search if time permits
        best_move, best_choice = minimax(board, max_depth, float('-inf'), float('inf'), True)

    # If no moves were found, end the turn
    if best_move is None or best_choice is None:
        self.game.end_turn()
    else:
        return best_move, best_choice
    