from discord.ext import commands
import discord

# L_MAIN
# L_BACKUP

class Player:
    def __init__(self, name, kd, wl)
        self.name = name
        self.kd = kd
        self.wl = wl

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
    content = message.content
    in_channel = message.channel
    if author != bot.user:
        if in_channel == results_c:
            await results_c.send('working')
            await results_c.send(content)
        else:
            await in_channel.send('wrong channel')


@bot.command
async def refresh(ctx, lim):
    await commands_c.send('refreshing with last {} matches...'.format(lim))
    await get_results(ctx, lim)


def get_results(ctx, lim):
    messages = results_c.history(limit=lim)
    return commands_c.send(messages)


bot.run(BOT_TOKEN)