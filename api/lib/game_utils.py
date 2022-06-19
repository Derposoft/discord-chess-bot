import logging

# local imports
from . import chessboard, utils, query
from .constants import STOCKFISH_INVITEE_ID, BLACK, WHITE

logger = logging.getLogger(__name__)


def move_ai_game(author, game, move_intent, stockfish):
    moves = query.get_moves_string(game)

    if not chessboard.check_move(stockfish, moves, move_intent):
        return utils.respond(
            f"u can't play that lol {utils.mention_db_player(author)}", 400
        )

    if not query.add_move_to_game(game, move_intent):
        return utils.respond(f"Couldn't make that move in the DB Senpai!", 500)

    moves = game.moves
    logger.debug(f"Calculating from moves for AI Move {moves} for game: {game.id}")

    # did player win?
    gameover_text = chessboard.get_gameover_text(stockfish, moves, False, author)
    logger.debug(f"PLAYER MOVE GAMEOVER?: {gameover_text}")
    if gameover_text is not None:
        logger.debug("PLAYER WIN!")
        complete_game(game)
        return gameover_text

    # AI Player Takes Turn
    best_move = chessboard.engine_move(stockfish, moves, game.stockfish_elo)
    query.add_move_to_game(game, best_move)
    moves = query.get_moves_string(game)

    # Did AI Player Win?
    gameover_text = chessboard.get_gameover_text(
        stockfish, moves, True, author, last_move=best_move
    )
    logger.debug(f"CPU MOVE GAMEOVER?: {gameover_text}")
    if gameover_text is not None:
        logger.debug("CPU WIN!")
        complete_game(game)
        return gameover_text

    return utils.respond(utils.relay_move_db(author, best_move), 202)


def move_pvp_game(mover, opponent, game, move_intent, stockfish):
    if not check_users_turn(game, mover):
        return utils.respond(
            f"it not ur turn lol?? {utils.mention_db_player(mover)}", 400
        )

    moves = query.get_moves_string(game)

    # load the game in stockfish and verify that the move is legal
    if not chessboard.check_move(stockfish, moves, move_intent):
        return utils.respond(
            f"u can't play that lol {utils.mention_db_player(mover)}", 400
        )

    if not query.add_move_to_game(game, move_intent):
        return utils.respond(
            f"Something Went Wrong in Making that Move (Are u hecking bro?)", 500
        )

    moves = game.moves

    # did player win?
    gameover_text = chessboard.get_gameover_text(
        stockfish, moves, False, mover, opponent=opponent
    )
    logger.debug(f"PLAYER MOVE GAMEOVER?: {gameover_text}")

    if gameover_text is not None:
        # end game
        logger.debug("PLAYER WIN!")
        complete_game(game)
        return gameover_text

    return utils.respond(
        f"ur move has been made good job pogO {utils.mention_db_player(mover)}", 202
    )


def get_game(mover, opponent, is_ai):
    mover_p = query.get_participant(mover)
    if mover_p is None:
        return construct_get_game_error(
            utils.respond(
                f"bruh is this your first time {utils.mention_player(mover)}?", 400
            )
        )

    opponent_p = None
    if opponent is not None:
        opponent_p = query.get_participant(opponent)
        if opponent_p is None:
            return construct_get_game_error(
                utils.respond(
                    f"Cool you wanna play with {utils.mention_player(opponent)}... but idk who they are.",
                    400,
                )
            )

    is_pvp = False
    game = None
    if opponent_p is None and not is_ai:
        game = query.get_recent_game(mover_p)
        if game != None and game.invitee_id != STOCKFISH_INVITEE_ID:
            is_pvp = True
            opponent_p = query.get_participant_from_id(game.invitee_id)
    elif opponent_p is None:
        is_pvp = False
        game = query.get_solo_game(mover_p)
    else:
        is_pvp = True
        game = query.get_pvp_game(mover_p, opponent_p)

    logger.debug(
        f"Returning Game: {game} and Mover: {mover_p} and opponent {opponent_p}"
    )
    return construct_get_game_response(mover_p, opponent_p, is_pvp, game)


def _construct_get_game_response_map(err, mover_p, opponent_p, is_pvp, game):
    return {
        "error": err,
        "mover_p": mover_p,
        "opponent_p": opponent_p,
        "is_pvp": is_pvp,
        "game": game,
    }


def construct_get_game_error(err):
    return _construct_get_game_response_map(err, None, None, None, None)


def construct_get_game_response(mover_p, opponent_p, is_pvp, game):
    return _construct_get_game_response_map(None, mover_p, opponent_p, is_pvp, game)


def get_error_from_response(game_response):
    if game_response["error"] != None:
        return game_response["error"]
    elif game_response["game"] == None:
        return utils.respond(
            "bruh don't know what game you speak of"
            + utils.mention_db_player(game_response["mover_p"]),
            400,
        )


def is_valid_from_response(game_response):
    return game_response["error"] == None and game_response["game"] != None


def get_game_from_response(game_response):
    return game_response["game"]


def get_mover_from_response(game_response):
    return game_response["mover_p"]


def get_opponent_from_response(game_response):
    return game_response["opponent_p"]


def get_is_pvp_from_response(game_response):
    return game_response["is_pvp"]


def complete_game(game):
    logger.debug(f"Game Has Been Completed and Thus Archived! ID:{game.id}")
    if not query.archive_game(game):
        logger.error(f"Issue occurred when Archiving Game!")


def check_users_turn(game, mover):
    mover_is_author = game.author_id == mover.id
    author_is_white = game.author_is_white
    its_whites_turn = game.white_to_move

    return (author_is_white == its_whites_turn) == mover_is_author


def validate_new_game(is_pvp, side, author, invitee):
    if side != WHITE and side != BLACK:
        return f"you can only be {WHITE} or {BLACK} because this is chess OMEGALUL"
    elif author is None:
        return "A unique ID for the author must be provided!"
    elif is_pvp and invitee is None:
        return "A unique ID for the invitee/challenged must be provided!"

    return None
