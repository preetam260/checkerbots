from copy import deepcopy

def group1(self, board):
    """
    Uses the Minimax algorithm with Alpha-Beta pruning to determine the best move.
    """

    def minimax(board, depth, alpha, beta, maximizing_player):
        if depth == 0 or self.endGameCheck(board):
            return self._current_eval(board), None, None

        if maximizing_player:
            max_eval = float('-inf')
            best_move = None
            for row, col, possible_moves in self.generatemove_at_a_time(board):  
                current_pos = (row, col)  # Combine row and col into current_pos
                for final_pos in possible_moves:
                    new_board = deepcopy(board)
                    self.moveOnBoard(new_board, current_pos, final_pos)
                    eval = minimax(new_board, depth - 1, alpha, beta, False)[0]
                    max_eval = max(max_eval, eval)
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
                    if max_eval == eval:
                        best_move = (current_pos, final_pos)
                if beta <= alpha:
                    break
            return max_eval, best_move[0], best_move[1]
        else:
            min_eval = float('inf')
            best_move = None
            for current_pos, possible_moves in self.generatemove_at_a_time(board):
                for final_pos in possible_moves:
                    new_board = deepcopy(board)
                    self.moveOnBoard(new_board, current_pos, final_pos)
                    eval = minimax(new_board, depth - 1, alpha, beta, True)[0]
                    min_eval = min(min_eval, eval)
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
                    if min_eval == eval:
                        best_move = (current_pos, final_pos)
                if beta <= alpha:
                    break
            return min_eval, best_move[0], best_move[1]

    # Get the best move using Minimax with Alpha-Beta pruning
    _, current_pos, final_pos = minimax(board, self.depth, float('-inf'), float('inf'), True)

    # If no valid moves are found, end the turn
    if current_pos is None or final_pos is None:
        self.game.end_turn()
        return

    return current_pos, final_pos