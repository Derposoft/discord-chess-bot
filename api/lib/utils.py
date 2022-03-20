from flask import make_response

# Takes two dictionaries and 2 lookups. Assigns the value if it exists otherwise assigns it to default
def safe_dict_copy_default(recv, recvpath, send, sendpath, default):
    safe_dict_copy(recv, recvpath, send, sendpath, lambda: default)

# Takes two dictionaries and 2 lookups. Assigns the value if it exists otherwise calls supplier. Will not assign index to "None"
def safe_dict_copy(recv, recvpath, send, sendpath, supplier=lambda: None):
    if recvpath is None or len(recvpath) == 0:
        raise ValueError("Indexes for receiving dictionary are empty or None") 
    elif sendpath is None or len(sendpath) == 0:
        raise ValueError("Indexes for sending dictionary are empty or None") 

    recvDict = recv
    recvNode = recv
    sendDict = send
    sendNode = send
    
    #TODO Maybe we should be type checking each node to be a dictionary or at least be
    #   indexable

    # Find Node in recv
    for i in range(len(recvpath)):
        index = recvpath[i]
        
        if index in recvNode:
            recvDict = recvNode
            recvNode = recvDict[index]
        elif i < len(recvpath) - 1:
            recvDict = recvNode
            recvDict[index] = {}
            recvNode = recvDict[index]
        else:
            recvDict = recvNode
    
    # Find Node in Send
    for index in sendpath:
        if index in sendNode:
            sendDict = sendNode
            sendNode = sendDict[index]
        else:
            sendNode = None
            break
    
    if sendNode is None:
        sendNode = supplier()
        if sendNode is None:
            return

    recvDict[recvpath[-1]] = sendNode


# Takes a dictionary and a list of indexes. Will return the value in the dictionary
# representing the first-most index in indexes. Otherwise return None if none of the
# indexes are in the dictionary
def get_first_valid_index(dict, indexes):
    for index in indexes:
        if index in dict:
            return dict[index]
    
    return None

def parse_args(request):
    return request.args

def mention_db_player(player):
    if player.discord_user_id != None:
        return mention_player(player.discord_user_id)
    else:
        return mention_player(player.discord_guild_id)

def mention_player(player_uid):
    return f'<@!{player_uid}>'

def relay_move(mover, move):
    return _relay_move(mover, move, mention_player)

def relay_move_db(mover, move):
    return _relay_move(mover, move, mention_db_player)

def _relay_move(mover, move, mention_player_lambda):
    return ('I play ' + move + mention_player_lambda(mover) + '.' if move != None else '')

def is_white_move(author_id, is_author_white, mover_id):
    return (author_id == mover_id) == is_author_white

def respond(body, status):
    return make_response((body, status))