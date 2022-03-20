from constants import BLACK, WHITE

def validate_new_game(is_pvp, side, author, invitee):
    if side != WHITE and side != BLACK:
        return f'you can only be {WHITE} or {BLACK} because this is chess OMEGALUL'
    elif author is None:
        return 'A unique ID for the author must be provided!'
    elif is_pvp and invitee is None:
        return 'A unique ID for the invitee/challenged must be provided!'
    
    return None