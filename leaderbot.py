from discord.ext import commands
import discord
import pickle
import csv

def save_object(obj):
    try:
        with open("playerdata.pickle", "wb") as f:
            pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)
    except Exception as ex:
        print("Error during pickling object (Possibly unsupported):", ex)


def load_object(filename):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except Exception as ex:
        print("Error during unpickling object (Possibly unsupported):", ex)


class Player:
    def __init__(self, name, kost, kills, deaths, wins, losses, points):
        self.name = name
        self.kost = kost
        self.kills = kills
        self.deaths = deaths
        self.wins = wins
        self.losses = losses
        self.points = points

BOT_TOKEN = "MTI2NjI4NDAxNjExNDQ3MDk2Ng.GVS3M0.soc2PKfD2TvF9wq9V4S2EgJDYZo1ew4MGeyUgc"

LEADERBOARD_CHANNEL = 1266283285516910705
COMMANDS_CHANNEL = 1266283316844429426
RESULTS_CHANNEL = 1266283405050380302

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
# client = discord.Client(intents=discord.Intents.all())

@bot.event
async def on_ready():
    print('Bot online')
    global leaderboard_c
    global commands_c
    global results_c
    leaderboard_c = bot.get_channel(LEADERBOARD_CHANNEL)
    commands_c = bot.get_channel(COMMANDS_CHANNEL)
    results_c = bot.get_channel(RESULTS_CHANNEL)

    await commands_c.send("Bot connected")


@bot.command
async def hello(ctx):
    await ctx.send("ARRRRGH")


@bot.event
async def on_message(message):
    author = message.author
    in_channel = message.channel
    attachments = message.attachments
    if author != bot.user and in_channel == results_c and len(attachments) != 0:
        for game in attachments:
            file_path = f'./{game.filename}'
            await game.save(file_path)
            results = parse_results(file_path)
            print(results)

@bot.command
async def refresh(ctx, lim):
    await commands_c.send('refreshing with last {} matches...'.format(lim))

def parse_results(file_path):
    playerlist = []
    
    with open(file_path, mode='r') as csvfile:
        reader = csv.reader(csvfile)
        
        for i in range(4):
            next(reader)

        r = 4
        for row in reader:
            if r == 4:
                team1_score = row[9]
                team2_score = row[10]
                team1_win = team1_score > team2_score
            
            if team1_win and r >= 7 and r <= 11:
                player = Player(row[3], row[10], row[16], row[22], 1, 0, row[30])
                playerlist.append(player)
            elif team1_win and r > 11:
                player = Player(row[3], row[10], row[16], row[22], 0, 1, row[30])
                playerlist.append(player)
            elif not team1_win and r >= 7 and r <= 11:
                player = Player(row[3], row[10], row[16], row[22], 0, 1, row[30])
                playerlist.append(player)
            elif not team1_win and r > 11:
                player = Player(row[3], row[10], row[16], row[22], 1, 0, row[30])
                playerlist.append(player)
            r += 1
        
        return playerlist

bot.run(BOT_TOKEN)