# returns user info
def user_info(ctx):
    return 'uid=' + str(ctx.author.id) #+ '&name=' + ctx.author.name

# parse @mentions
def mention_parser(ctx):
    return 0

# UNDER CONSTRUCTION (this one is hard as it requires board context)
def sfmove_to_algebraic(sfmove):
    return 0
    