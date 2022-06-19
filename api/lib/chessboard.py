import chess, logging
from . import utils

logger = logging.getLogger(__name__)


def _set_board_to(stockfish, moves):
    stockfish.set_position([move for move in moves.split(" ") if move != ""])


def check_move(stockfish, moves, move):
    _set_board_to(stockfish, moves)
    return stockfish.is_move_correct(move)


def engine_move(stockfish, moves, elo):
    stockfish.set_elo_rating(elo)
    _set_board_to(stockfish, moves)
    best = stockfish.get_best_move()
    return best


def cheat_board(stockfish, moves):
    logger.debug(f"moves {moves}")
    _set_board_to(stockfish, moves)
    board = stockfish.get_board_visual()
    eval = stockfish.get_evaluation()
    best = stockfish.get_best_move()
    return "```" + board + "```", str(eval), best


def get_board(stockfish, moves):
    _set_board_to(stockfish, moves)
    return stockfish.get_board_visual()


def get_board_backquoted(stockfish, moves):
    return f"```{get_board(stockfish, moves)}```"


def draw_claim_victory(draw_text, moves, stockfish):
    return utils.respond(
        draw_text
        + f"final board:\n{get_board_backquoted(stockfish, moves)}"
        + f"\nmoves: {moves}",
        202,
    )


def solo_claim_victory(moves, mover, stockfish):
    return utils.respond(
        f"{utils.mention_db_player(mover)}, you win POG game over, well played ((no kap))."
        + f"final board:\n{get_board_backquoted(stockfish, moves)}"
        + f"\nmoves: {moves}",
        202,
    )


def ai_claim_victory(moves, mover, last_move, stockfish):
    start = ""
    if last_move != None:
        start = f"{utils.relay_move_db(mover, last_move)}\n"

    return utils.respond(
        start
        + f"{utils.mention_db_player(mover)} get rekt noob i win again KEKW "
        + f"final board state:\n{get_board_backquoted(stockfish, moves)}"
        + f"\nmoves: {moves}",
        202,
    )


def pvp_claim_victory(moves, winner, loser, stockfish):
    return utils.respond(
        f"{utils.mention_db_player(loser)} lmao "
        + f"{utils.mention_db_player(winner)} stands above you again, you plebe:\n"
        + f"{get_board_backquoted(stockfish, moves)}"
        + f"\nmoves: {moves}",
        202,
    )


def get_gameover_text(stockfish, moves, is_ai, mover, opponent=None, last_move=None):
    logger.debug(f"Getting Game Over Text For: {moves} {is_ai}")
    _set_board_to(stockfish, moves)
    fen = stockfish.get_fen_position()
    board = chess.Board(fen)
    logger.debug(f"{board.outcome()}")
    # check for different game over scenarios
    if board.is_stalemate():
        return draw_claim_victory("game is draw by stalemate. sadge.", moves, stockfish)
    elif board.is_insufficient_material():
        return draw_claim_victory(
            "game is draw by not enough juicers for mate sadge.", moves, stockfish
        )
    elif board.can_claim_fifty_moves():
        return draw_claim_victory(
            "game is draw by 50 move rule OMEGALUL!", moves, stockfish
        )
    elif board.can_claim_threefold_repetition():
        return draw_claim_victory(
            "game is over by 3fold repetition :LUL: ", moves, stockfish
        )
    elif board.is_checkmate():
        if is_ai:
            return ai_claim_victory(moves, mover, last_move, stockfish)
        elif opponent == None:
            return solo_claim_victory(moves, mover, stockfish)
        else:
            return pvp_claim_victory(moves, mover, opponent, stockfish)
    elif board.outcome() != None:
        return draw_claim_victory(
            "game is over by unknown glitch (jk it's a chess rule but i haven't coded it in).",
            moves,
            stockfish,
        )

    return None
