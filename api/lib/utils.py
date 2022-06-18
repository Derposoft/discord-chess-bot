from flask import make_response
from copy import deepcopy

# Takes two dictionaries and 2 lookups. Assigns the value if it exists otherwise calls supplier. Will not assign index to "None"
def safe_dict_copy(recv, recvpath, send, sendpath, default=None):
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
        sendNode = deepcopy(default)
        if sendNode is None:
            return

    recvDict[recvpath[-1]] = sendNode

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

def respond(body, status):
    return make_response((body, status))