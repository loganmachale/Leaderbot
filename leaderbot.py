from discord.ext import commands
import discord
import pickle
import csv
import os
import numpy as np
import scipy.stats as sps


def save_object(obj, fname):
    try:
        with open(fname, "wb") as f:
            pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)
    except Exception as ex:
        print("Error during pickling object (Possibly unsupported):", ex)


def load_object(filename):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except Exception as ex:
        print("Error during unpickling object (Possibly unsupported):", ex)


# def first_run():
#     '''
#     creates all necessary starter files from which record can pile on.
#     WARNING: will erase all current player records, leave commented out!
#     '''
#     KNOWN_PLAYERS = []
#     PLAYER_DATA = []

#     save_object(KNOWN_PLAYERS, 'known_players.pickle')
#     save_object(PLAYER_DATA, 'player_data.pickle')


class Player:
    def __init__(self, name, kost, kills, deaths, wins, losses, points, elo):
        self.name = name
        self.kost = kost
        self.kills = kills
        self.deaths = deaths
        self.wins = wins
        self.losses = losses
        self.points = points
        self.elo = elo

BOT_TOKEN = "MTI2NjI4NDAxNjExNDQ3MDk2Ng.GVS3M0.soc2PKfD2TvF9wq9V4S2EgJDYZo1ew4MGeyUgc"

LEADERBOARD_CHANNEL = 1266283285516910705
COMMANDS_CHANNEL = 1266283316844429426
RESULTS_CHANNEL = 1266283405050380302

global PLAYER_DATA
global KNOWN_PLAYERS

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


# on message to results channel will extract match data and auto-update leaderboard
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
            update_player_data(results)
            os.remove(file_path)


def parse_results(file_path):
    playerlist = []
    
    with open(file_path, mode='r') as csvfile:
        reader = csv.reader(csvfile)
        
        for i in range(5):
            next(reader)

        r = 4
        for row in reader:
            if r == 4:
                team1_score = int(row[9])
                team2_score = int(row[10])
                team1_win = team1_score > team2_score

            if team1_win and r >= 8 and r <= 12:
                player = Player(row[3], float(row[10]), int(row[16]), int(row[22]), 1, 0, int(row[30]), 0)
                playerlist.append(player)
            elif team1_win and r > 12:
                player = Player(row[3], float(row[10]), int(row[16]), int(row[22]), 0, 1, int(row[30]), 0)
                playerlist.append(player)
            elif not team1_win and r >= 8 and r <= 12:
                player = Player(row[3], float(row[10]), int(row[16]), int(row[22]), 0, 1, int(row[30]), 0)
                playerlist.append(player)
            elif not team1_win and r > 12:
                player = Player(row[3], float(row[10]), int(row[16]), int(row[22]), 1, 0, int(row[30]), 0)
                playerlist.append(player)
            r += 1

            if r > 17:
                break
        return playerlist


def update_player_data(match_data):
    global PLAYER_DATA
    global KNOWN_PLAYERS
    PLAYER_DATA = load_object('player_data.pickle')
    KNOWN_PLAYERS = load_object('known_players.pickle')
    # back up player data and known players
    save_object(PLAYER_DATA, 'player_data_backup.pickle')
    save_object(KNOWN_PLAYERS, 'known_players_backup.pickle')

    for m_player in match_data:
        if m_player.name in KNOWN_PLAYERS:
            p_ind = KNOWN_PLAYERS.index(m_player.name)
            player = PLAYER_DATA[p_ind]
            p_games = player.wins + player.losses
            player.kost = (player.kost * p_games + m_player.kost) / (p_games + 1)
            player.kills += m_player.kills
            player.deaths += m_player.deaths
            player.wins += m_player.wins
            player.losses += m_player.losses
            player.points += m_player.points
        else:
            PLAYER_DATA.append(m_player)
            KNOWN_PLAYERS.append(m_player.name)
    
    # saves updated player data and known player list
    save_object(PLAYER_DATA, 'player_data.pickle')
    save_object(KNOWN_PLAYERS, 'known_players.pickle')


# def update_leaderboard(player_data):


def elo_func(kost, kills, deaths, wins, losses):
    kost_mu = 0.55
    kost_sigma = 0.15
    dist = sps.norm(loc=kost_mu, scale=kost_sigma)
    p = dist.cdf(kost)

    kost_factor = (np.sqrt(2) - 2 + 2 * (1 - np.sqrt(2)) * p) ** 2

    return (wins * 150 - losses * 100 ) * kost_factor + kills * 10 - deaths * 10

# def get_rank(player):


# @bot.command
# async def revert():


# @bot.command
# async def stats(ctx, player):
#     if ctx.channel == commands_c and player in KNOWN_PLAYERS:
#         ctx.send(STATS)
#     elif ctx.channel == commands_c and player not in KNOWN_PLAYERS:
#         ctx.send('player not found')
#     elif ctx.channel != commands_c and player in KNOWN_PLAYERS:
#         ctx.send('wrong channel')
#     elif ctx.channel != commands_c and player not in KNOWN_PLAYERS:
#         ctx.send('player not found and wrong channel!')    


# @bot.command
# async def rank(ctx, player):
#     if ctx.channel == commands_c and player in KNOWN_PLAYERS:
#         ctx.send(RANK)
#     elif ctx.channel == commands_c and player not in KNOWN_PLAYERS:
#         ctx.send('player not found')
#     elif ctx.channel != commands_c and player in KNOWN_PLAYERS:
#         ctx.send('wrong channel')
#     elif ctx.channel != commands_c and player not in KNOWN_PLAYERS:
#         ctx.send('player not found and wrong channel!')  

bot.run(BOT_TOKEN)