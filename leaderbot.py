from discord.ext import commands
import discord
import pickle
import csv
import os
import numpy as np
import scipy.stats as sps
from table2ascii import table2ascii as t2a, PresetStyle
import json

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


def initialize():
    '''
    creates all necessary starter files from which record can pile on.
    WARNING: will erase all current player records, leave commented out!
    '''
    global MATCH_HIST
    global KNOWN_PLAYERS
    global PLAYER_LEADERBOARD
    global PLAYER_DATA
    global BANNED_PLAYERS

    MATCH_HIST = []
    KNOWN_PLAYERS = []
    PLAYER_DATA = []
    PLAYER_LEADERBOARD = []
    BANNED_PLAYERS = []

    save_object(KNOWN_PLAYERS, 'known_players.pickle')
    save_object(PLAYER_DATA, 'player_data.pickle')
    save_object(MATCH_HIST, 'match_hist.pickle')
    save_object(PLAYER_LEADERBOARD, 'player_leaderboard.pickle')
    save_object(BANNED_PLAYERS, 'banned_players.pickle')


initialize()


class Player:
    def __init__(self, name: str, kost: float, kills: int, deaths: int, wins: int,
                 losses: int, points: int, elo: int, p_id: str):
        self.name = name
        self.kost = kost
        self.kills = kills
        self.deaths = deaths
        self.wins = wins
        self.losses = losses
        self.points = points
        self.elo = elo
        self.p_id = p_id

### initialize() ### only uncomment when sure

BOT_TOKEN = "MTI2NjI4NDAxNjExNDQ3MDk2Ng.GVS3M0.soc2PKfD2TvF9wq9V4S2EgJDYZo1ew4MGeyUgc"

LEADERBOARD_CHANNEL = 1266283285516910705
COMMANDS_CHANNEL = 1266283316844429426
JSON_RESULTS_CHANNEL = 1266283405050380302

BANNED_PLAYERS = load_object('banned_players.pickle')
PLAYER_DATA = load_object('player_data.pickle')
KNOWN_PLAYERS = load_object('known_players.pickle')
PLAYER_LEADERBOARD = load_object('player_leaderboard.pickle')
LB1_MSG_ID = load_object('lb1_msg_id.pickle')
LB2_MSG_ID = load_object('lb2_msg_id.pickle')
LB3_MSG_ID = load_object('lb3_msg_id.pickle')
LB4_MSG_ID = load_object('lb4_msg_id.pickle')
LB5_MSG_ID = load_object('lb5_msg_id.pickle')

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
# client = discord.Client(intents=discord.Intents.all())

@bot.event
async def on_ready():
    print('Bot online')
    global leaderboard_c
    global commands_c
    global json_results_c

    leaderboard_c = bot.get_channel(LEADERBOARD_CHANNEL)
    commands_c = bot.get_channel(COMMANDS_CHANNEL)
    json_results_c = bot.get_channel(JSON_RESULTS_CHANNEL)

    await commands_c.send("Bot connected")


@bot.command()
async def hello(ctx):
    await ctx.send("ARRRRGH")


# on message to results channel will extract match data and auto-update leaderboard
@bot.event
async def on_message(message):
    global MATCH_HIST
    global PLAYER_DATA
    
    await bot.process_commands(message)
    author = message.author
    in_channel = message.channel
    attachments = message.attachments
    if author != bot.user and in_channel == json_results_c and len(attachments) != 0:
        for game in attachments:
            file_path = f'./{game.filename}'
            await game.save(file_path)  
            results = parse_json_results(file_path)
            
            MATCH_HIST = load_object('match_hist.pickle')
            MATCH_HIST.append(results)
            save_object(MATCH_HIST, 'match_hist.pickle')
            del MATCH_HIST

            await validate_match(results)
            update_player_data(results)
            await update_leaderboard(PLAYER_DATA)
            os.remove(file_path)


def parse_json_results(file_path):
    with open(file_path) as match_json:
        match_data = json.load(match_json)

    player_data = match_data['per_player']
    fteam_win = bool(match_data['friendly_win'])

    f_w = 0
    e_w = 0

    if fteam_win:
        f_w = 1
        e_w = 0
    else:
        f_w = 0
        e_w = 1

    player_list = []

    for p_id in player_data:
        p_dic = player_data[p_id]

        if p_dic['team'] == 'friendly':
            try:
                player = Player(p_dic['name'], float(p_dic['kost'].replace('%', ''))/100, int(p_dic['kills']), int(p_dic['deaths']), f_w, e_w,
                                int(p_dic['score']), 0, p_id)
                player_list.append(player)
            except:
                pass
        else:
            try:
                player = Player(p_dic['name'], float(p_dic['kost'].replace('%', ''))/100, int(p_dic['kills']), int(p_dic['deaths']), e_w, f_w,
                                int(p_dic['score']), 0, p_id)
                player_list.append(player)
            except:
                pass
    return player_list


def parse_csv_results(file_path):
    playerlist = []
    
    with open(file_path, mode='r') as csvfile:
        reader = csv.reader(csvfile)
        
        for i in range(4):
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
        p_win = m_player.wins == 1
        
        if m_player.p_id in KNOWN_PLAYERS:
            p_ind = KNOWN_PLAYERS.index(m_player.p_id)
            p = PLAYER_DATA[p_ind]
            p_games = p.wins + p.losses
            p.kost = (p.kost * p_games + m_player.kost) / (p_games + 1)
            p.kills += m_player.kills
            p.deaths += m_player.deaths
            p.wins += m_player.wins
            p.losses += m_player.losses
            p.points += m_player.points
            p.elo += elo_func(m_player.kost, m_player.kills, m_player.deaths, p_win)
        else:
            m_player.elo += elo_func(m_player.kost, m_player.kills, m_player.deaths, p_win)
            PLAYER_DATA.append(m_player)
            KNOWN_PLAYERS.append(m_player.p_id)
    
    # saves updated player data and known player list
    save_object(PLAYER_DATA, 'player_data.pickle')
    save_object(KNOWN_PLAYERS, 'known_players.pickle')


async def update_leaderboard(player_data):
    global PLAYER_LEADERBOARD
    
    b1_msg = await leaderboard_c.fetch_message(LB1_MSG_ID)
    b2_msg = await leaderboard_c.fetch_message(LB2_MSG_ID)
    b3_msg = await leaderboard_c.fetch_message(LB3_MSG_ID)
    b4_msg = await leaderboard_c.fetch_message(LB4_MSG_ID)
    b5_msg = await leaderboard_c.fetch_message(LB5_MSG_ID)
    
    PLAYER_LEADERBOARD = sorted(player_data, key=lambda x: x.elo, reverse=True)
    save_object(PLAYER_LEADERBOARD, 'player_leaderboard.pickle')
    head = '```diff\n+ Aura X Scrim Leaderboard +\n```'
 
    r = 1
    p_list = []
    for p in PLAYER_LEADERBOARD:
        if p.deaths != 0:
            p_list.append([r, p.name, p.elo, p.wins, p.losses, p.kills,
                        p.deaths, '{:.2f}'.format(p.kills / p.deaths),
                        '{:.2f}'.format(p.kost)])
        else:
            p_list.append([r, p.name, p.elo, p.wins, p.losses, p.kills,
                        p.deaths, '{:.2f}'.format(p.kills),
                        '{:.2f}'.format(p.kost)])
        r += 1
        if r > 90:
            break

    output1 = t2a(
        header=['Rank', 'Name', 'Elo', 'Wins', 'Losses', 'Kills', 'Deaths', 'K/D', 'KOST'],
        body=p_list[:18]
    )

    output2 = t2a(
        header=['Rank', 'Name', 'Elo', 'Wins', 'Losses', 'Kills', 'Deaths', 'K/D', 'KOST'],
        body=p_list[18:36]
    )

    output3 = t2a(
        header=['Rank', 'Name', 'Elo', 'Wins', 'Losses', 'Kills', 'Deaths', 'K/D', 'KOST'],
        body=p_list[36:54]
    )

    output4 = t2a(
        header=['Rank', 'Name', 'Elo', 'Wins', 'Losses', 'Kills', 'Deaths', 'K/D', 'KOST'],
        body=p_list[54:72]
    )

    output5 = t2a(
        header=['Rank', 'Name', 'Elo', 'Wins', 'Losses', 'Kills', 'Deaths', 'K/D', 'KOST'],
        body=p_list[72:90]
    )

    await b1_msg.edit(content=head + '```{}```'.format(output1))
    await b2_msg.edit(content='```{}```'.format(output2))
    await b3_msg.edit(content='```{}```'.format(output3))
    await b4_msg.edit(content='```{}```'.format(output4))
    await b5_msg.edit(content='```{}```'.format(output5))
    

@bot.command()
async def reset_lb(ctx):
    global LB1_MSG_ID
    global LB2_MSG_ID
    global LB3_MSG_ID
    global LB4_MSG_ID
    global LB5_MSG_ID
    
    b1_msg = await leaderboard_c.fetch_message(LB1_MSG_ID)
    b2_msg = await leaderboard_c.fetch_message(LB2_MSG_ID)
    b3_msg = await leaderboard_c.fetch_message(LB3_MSG_ID)
    b4_msg = await leaderboard_c.fetch_message(LB4_MSG_ID)
    b5_msg = await leaderboard_c.fetch_message(LB5_MSG_ID)

    await leaderboard_c.delete_messages([b1_msg, b2_msg, b3_msg,
                                         b4_msg, b5_msg])
    
    b1_msg = await leaderboard_c.send('```\n```')
    b2_msg = await leaderboard_c.send('```\n```')
    b3_msg = await leaderboard_c.send('```\n```')
    b4_msg = await leaderboard_c.send('```\n```')
    b5_msg = await leaderboard_c.send('```\n```')

    LB1_MSG_ID = b1_msg.id
    LB2_MSG_ID = b2_msg.id
    LB3_MSG_ID = b3_msg.id
    LB4_MSG_ID = b4_msg.id
    LB5_MSG_ID = b5_msg.id

    save_object(LB1_MSG_ID, 'lb1_msg_id.pickle')
    save_object(LB2_MSG_ID, 'lb2_msg_id.pickle')
    save_object(LB3_MSG_ID, 'lb3_msg_id.pickle')
    save_object(LB4_MSG_ID, 'lb4_msg_id.pickle')
    save_object(LB5_MSG_ID, 'lb5_msg_id.pickle')


@bot.command()
async def refresh_lb(ctx):
    global PLAYER_DATA
    PLAYER_DATA = load_object('player_data.pickle')
    
    await update_leaderboard(PLAYER_DATA)

def elo_func(kost, kills, deaths, win):
    kost_mu = 0.55
    kost_sigma = 0.2
    dist = sps.norm(loc=kost_mu, scale=kost_sigma)
    p = dist.cdf(kost + ((kost - 0.55) ** 2) / 7 + (kost - 0.55) / 9)

    if win:
        if int(kost) == 1:
            kost_factor = 2
        else:    
            kost_factor = (np.sqrt(2) - 2 + 2 * (1 - np.sqrt(2)) * p) ** 2
        
        return round(150 * kost_factor + kills * 10 - deaths * 10)
    else:
        if int(kost) == 1:
            kost_factor = 0.4
        else:    
            kost_factor = -6 / 5 * p + 1.6
        
        return round(-100 * kost_factor + kills * 10 - deaths * 10)


async def validate_match(match_data):
    for player in match_data:
        if player.kills >= 26:
            await json_results_c.send('verify this match data with a screenshot')


def get_rank(player, player_lb):
    r = 1
    for p in player_lb:
        if p.name == player:
            return r
        r += 1


def get_stats(player, player_data):
    for p in player_data:
        if p.name == player:
            return p


@bot.command()
async def undo(ctx):
    global KNOWN_PLAYERS
    global PLAYER_DATA
    
    KNOWN_PLAYERS = load_object('known_players_backup.pickle')
    PLAYER_DATA = load_object('player_data_backup.pickle')
    save_object(KNOWN_PLAYERS, 'known_players.pickle')
    save_object(PLAYER_DATA, 'player_data.pickle')

    await update_leaderboard(PLAYER_DATA)


@bot.command()
async def stats(ctx, player=''):
    global PLAYER_DATA
    
    if len(player) > 0 and ctx.channel == commands_c:
        p = get_stats(player, PLAYER_DATA)
        if p.deaths != 0:
            await ctx.send('Player: {}, Elo: {}, Wins: {}, Losses: {}, Kills: {}, Deaths: {}, K/D: {:.2f}, KOST: {:.2f}, Points: {}'.format(
                p.name, p.elo, p.wins, p.losses, p.kills, p.deaths, p.kills / p.deaths, p.kost, p.points
            ))
        else:
            await ctx.send('Player: {}, Elo: {}, Wins: {}, Losses: {}, Kills: {}, Deaths: {}, K/D: {:.2f}, KOST: {:.2f}, Points: {}'.format(
                p.name, p.elo, p.wins, p.losses, p.kills, p.deaths, p.kills, p.kost, p.points
            ))
    elif len(player) > 0 and ctx.channel != commands_c:
        await ctx.send('wrong channel')
    else:
        await ctx.send('Enter player username')


@bot.command()
async def rank(ctx, player=''):
    global PLAYER_LEADERBOARD
    
    if len(player) > 0 and ctx.channel == commands_c:
        await ctx.send('#' + str(get_rank(player, PLAYER_LEADERBOARD)))
    elif len(player) > 0 and ctx.channel != commands_c:
        await ctx.send('wrong channel')
    else:
        await ctx.send('Enter player username')


key = 'phoenix'
@bot.command()
async def wipe_player_data(ctx, password):
    global PLAYER_DATA
    global KNOWN_PLAYERS
    global PLAYER_LEADERBOARD
    
    if password == key:
        PLAYER_DATA = []
        KNOWN_PLAYERS = []
        PLAYER_LEADERBOARD = []

        save_object(PLAYER_DATA, 'player_data.pickle')
        save_object(KNOWN_PLAYERS, 'known_players.pickle')
        save_object(PLAYER_LEADERBOARD, 'player_leaderboard.pickle')


@bot.command()
async def ban(ctx, user):
    global MATCH_HIST
    global PLAYER_DATA

    MATCH_HIST = load_object('match_hist.pickle')
    cheat_matches = []

    for match in MATCH_HIST:
        for player in match:
            if user == player.name:
                cheat_matches.append(match)
                cheater = player
                break
                
    for game in cheat_matches:
        for m_player in game:
            p_win = m_player.wins == 1
            p_ind = KNOWN_PLAYERS.index(m_player.p_id)
            p = PLAYER_DATA[p_ind]
            p_games = p.wins + p.losses
            # p.kost = (p.kost * p_games - m_player.kost) / (p_games + 1)
            p.kills -= m_player.kills
            p.deaths -= m_player.deaths
            p.wins -= m_player.wins
            p.losses -= m_player.losses
            p.points -= m_player.points
            p.elo -= elo_func(m_player.kost, m_player.kills, m_player.deaths, p_win)
    save_object(PLAYER_DATA, 'player_data.pickle')
    
    MATCH_HIST.remove(match)
    KNOWN_PLAYERS.remove(cheater.p_id)
    BANNED_PLAYERS.append(cheater)
    for pr in PLAYER_DATA:
        if pr.name == user:
            PLAYER_DATA.remove(pr)

    save_object(MATCH_HIST, 'match_hist.pickle')
    save_object(PLAYER_DATA, 'player_data.pickle')
    save_object(KNOWN_PLAYERS, 'known_players.pickle')
    save_object(BANNED_PLAYERS, 'banned_players.pickle')

    del MATCH_HIST
    await update_leaderboard(PLAYER_DATA)


bot.run(BOT_TOKEN)