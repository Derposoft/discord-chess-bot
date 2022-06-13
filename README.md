# discord chess bot
a discord bot enabling chess enthusiasts who add this bot to their servers to play blindfold chess in discord chat! designed to be a lightweight bot, possibly for embedded applications (i personally host this on my raspberry pi at home!), while still being sophisticated enough to bring excitement to your discord server. this is really just a simple discord API usage layered over the python stockfish library.

**2/14/2022 UPDATE:**
lads and lasses, the time has come. you can now play blindfolded chess versus each other instead of versus the bot. commandlist below is update to reflect the updates. since the database schema didn't change in this update, all of your old games with the bot will remain even if you update your version of the bot.

pls raise issue if there are bugs, i didn't have a lot of time to test it this time around.

## how do i start up this thing?
follow these steps:

0. install python 3 (version 3.6+) and pip (21.0+) (for Linux this is most likely installed. For other platforms [look online](https://www.python.org/downloads/).)
1. install the requirements for this project `pip install -r requirements.txt`
2. create an application with associated bot using the [discord developer portal](https://discord.com/developers/applications).
3. Add Privaledged Gateway Intents (Presence Intent, Server Members Intent, and Message Content Intent)
4. Add your application/bot to your server. This can be done through the OAuth URL generator or alternatively through the server with application ID.
5. Create a `config.json` based on the `config.example.json`
6. Copy your bot's secret token and put it in `config.json`, with the key being "discord" and the value being the secret token. i.e.:
```json
"keys": {
    "discord": "SECRET_KEY_HERE" 
}
```
7. Download/Install Stockfish on your local machine. for debian-based linux machines, this looks something like running `sudo apt-get install stockfish`.
8. Copy the stockfish filepath to your `config.json`
```json
"api": {
    //...
    "stockfish": "path_to_stockfish_executable"
},
```

the bot is now ready to use pog

### Running the Scripts
#### LINUX
From the root of the repository run `python -m api & python -m bot &`
#### Windows (Batch/CMD)
From the root of the repository run `start python -m api & start python -m bot`
#### NOTE
These will start background processes. To kill these processes it may only be possible to kill/end them via Task Manager or `ps` + signal command for Linux/Mac.

## Automated Testing
I added a second requirements list for dev testing. `requirements-dev` which can be installed via `pip install -r requirements-dev.txt`. Then go ahead and run via pytest.

1. `pip install -r requirements-dev.txt`
2. `python -m pytest --log-cli-level=0 --config="test-config.json" ./api` with `test-config.json` being the same as `config.example.json` but with test/breakable values (don't use the production database)
3. `python -m pytest --log-cli-level=0 --config="test-config.json" ./bot` same as above with `test-config.json` (it uses the same file too)

## ok but how do i use the bot once it's up and running?
the commands are simple ([parameter] = optional):

**-help**   list the commands

**-new white|black [elo/@mention]**  start a new game either as white or black with either the given stockfish elo or the opponent that you @mentioned in the server. if no elo/mention is given, a default of elo=1500 will be used.

**-move move [@mention]**    make a move. moves must be in full algebraic notation (e.g. e4 e5 Nf3 -> e2e4 e7e5 g1f3). if @mention is included, the move will be made in the game between you and the mentioned player. otherwise, your current game versus stockfish is used.

**-ff [@mention]** surrender against the bot (or against your opponent if @mention is used).

**-cheat [@mention]**  cheat at blindfold chess by viewing the board. the bot will also return the best move in the current position, and the stockfish evaluation. you can choose which active game to cheat in by adding an @mention.


## possible upcoming features
- [x] ability to play against other people in the server via @mentions
- [ ] use of easier notation (e.g. 'Nf3' instead of 'g1f3')
- [ ] ???

## also, here are some screenshots of the bot in action once you've set it up right

1. you can ask it for help and you'll get some help

![help](https://github.com/Derposoft/discord-chess-bot/blob/main/images/1-help.png?raw=true)

2. you can create a new game and play with it, but you can only play 1 game at a time right now

![new game](https://github.com/Derposoft/discord-chess-bot/blob/main/images/2-new_game.png)

3. if you can no longer visualize the board, it'll help you cheat - but it's pretty snarky and loves trash talking, so it'll insult you too. sorry

![cheat](https://github.com/Derposoft/discord-chess-bot/blob/main/images/3-cheat.png)

4. if you give up, you can surrender. it really loves trash talking you by design

![help](https://github.com/Derposoft/discord-chess-bot/blob/main/images/4-ff.png)

5. it'll let you know if you try to make an illegal move too

![illegal move](https://github.com/Derposoft/discord-chess-bot/blob/main/images/5-illegal_move.png)

