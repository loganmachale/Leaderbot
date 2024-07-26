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
    def __init__(self, name, kills, deaths, wins, losses):
        self.name = name
        self.kills = kills
        self.deaths = deaths
        self.wins = wins
        self.losses = losses

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
            
@bot.command
async def refresh(ctx, lim):
    await commands_c.send('refreshing with last {} matches...'.format(lim))

def parse_results(attachments):
    playerlist = []
    
    with open(attachments, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            playerlist.append(row)

bot.run(BOT_TOKEN)