# discord chess bot
discord bot enabling chess enthusiasts who add this bot to their servers to play blindfold chess in discord chat!

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
