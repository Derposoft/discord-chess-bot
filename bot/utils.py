# returns user info
def user_info(ctx):
    return 'uid=' + str(ctx.author.id) #+ '&name=' + ctx.author.name

# parse @mentions
def mention_parser(user):
    return user[3:-1] # cuts out the '<@!' and '>' and the start and end

# add an extra query param in case of a pvp request
def pvpstring(player):
    pstring = ''
    if player != '':
        # is a pvp game
        pstring = f'&opponent={mention_parser(player)}'
    return pstring

# UNDER CONSTRUCTION (this one is hard as it requires board context)
def sfmove_to_algebraic(sfmove):
    return 0
    