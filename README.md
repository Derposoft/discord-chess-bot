# discord chess bot
a discord bot enabling chess enthusiasts who add this bot to their servers to play blindfold chess in discord chat! designed to be a lightweight bot, possibly for embedded applications (i personally host this on my raspberry pi at home!), while still being sophisticated enough to bring excitement to your discord server. this is really just a simple discord API usage layered over the python stockfish library.

## how do i start up this thing?
follow these steps:

0. install the requirements for this project (pip install -r requirements.txt; requires python 3.6+)
1. create a bot using the discord developer portal, because i don't have this hosted anywhere
2. add your bot to your server (hint: you'll need your application ID for this)
3. find your bot's secret token and put it in bot/keys.json, with the key being "discord" and the value being the secret token. i.e.:
{
    "discord": "[secret token]"
}
4. install stockfish on your local machine. for debian-based linux machines, this looks something like running "sudo apt-get install stockfish".
5. run 'bot/bot.py'
6. run 'api/api.py'

the bot is now ready to use pog

## ok but how do i use the bot once it's up and running?
the commands are simple:

**-help**   list the commands

**-new [white|black] [elo]**  start a new game either as white or black with the given stockfish elo opponent. if no elo is given. elo=1500 will be used.

**-move [move]**    make a move. moves must be in full algebraic notation (e.g. e4 e5 Nf3 -> e2e4 e7e5 g1f3).

**-ff** surrender against the bot.

**-cheat**  cheat at blindfold chess by viewing the board. the bot will also return the best move in the current position, and the stockfish evaluation.


## possible upcoming features
1. ability to play against other people in the server via @mentions
2. use of easier notation (e.g. 'Nf3' instead of 'g1f3')
3. ???

## also, here are some screenshots of the bot in action once you've set it up right

1. you can ask it for help and you'll get some help
[help](https://github.com/Derposoft/discord-chess-bot/blob/main/images/1-help.png)

2. you can create a new game and play with it, but you can only play 1 game at a time right now
[new game](https://github.com/Derposoft/discord-chess-bot/blob/main/images/2-new_game.png)

3. if you can no longer visualize the board, it'll help you cheat - but it's pretty snarky and loves trash talking, so it'll insult you too. sorry
[cheat](https://github.com/Derposoft/discord-chess-bot/blob/main/images/3-cheat.png)

4. if you give up, you can surrender. it really loves trash talking you by design
[help](https://github.com/Derposoft/discord-chess-bot/blob/main/images/4-ff.png)

5. it'll let you know if you try to make an illegal move too
[illegal move](https://github.com/Derposoft/discord-chess-bot/blob/main/images/5-illegal_move.png)

