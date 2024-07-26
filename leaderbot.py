from discord.ext import commands
import discord

# L_MAIN
# L_BACKUP

BOT_TOKEN = "MTI2NjI4NDAxNjExNDQ3MDk2Ng.GVS3M0.soc2PKfD2TvF9wq9V4S2EgJDYZo1ew4MGeyUgc"

LEADERBOARD_CHANNEL = 1266283285516910705
COMMANDS_CHANNEL = 1266283316844429426
RESULTS_CHANNEL = 1266283405050380302

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print('hello world')
    global leaderboard_c
    global commands_c
    global results_c
    leaderboard_c = bot.get_channel(LEADERBOARD_CHANNEL)
    commands_c = bot.get_channel(COMMANDS_CHANNEL)
    results_c = bot.get_channel(RESULTS_CHANNEL)

    await commands_c.send("hello world")


@bot.command()
async def hello(ctx):
    await ctx.send("ARRRRGH")


# @client.event
# async def on_message(message):


@bot.command()
def refresh(ctx, lim):
    commands_c.send('refreshing with last {} matches...'.format(lim))
    get_results(ctx, lim)
    

def get_results(ctx, lim):
    messages = ctx.channel.history(limit=lim)
    commands_c.send(messages)

bot.run(BOT_TOKEN)