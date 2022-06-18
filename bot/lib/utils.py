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

    # TODO Maybe we should be type checking each node to be a dictionary or at least be
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


# returns user info
def user_info(ctx):
    return str(ctx.author.id)


# parse @mentions
def mention_parser(user):
    return user[3:-1]  # cuts out the '<@!' and '>' and the start and end


# is 'elo' parameter a number?
def is_elo(elo):
    nums = "0123456789"
    return all([c in nums for c in elo])


# add an extra query param in case of a pvp request
def pvpstring(player):
    return mention_parser(player)


# UNDER CONSTRUCTION (this one is hard as it requires board context)
def sfmove_to_algebraic(sfmove):
    return 0
