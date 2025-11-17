import requests
import os
from dotenv import load_dotenv

from database import create_connection, get_players, get_last_match, update_last_match, select_player_by_name, select_player_by_id, update_leaderboard, add_player_to_leaderboard, add_player_to_players, remove_player_from_leaderboard, remove_player_from_players, reorder_leaderboard, get_players_count

load_dotenv()
api_key = os.getenv('API_KEY')

conn = create_connection('discordBOT.db')
players = get_players(conn)

# Useful variables

tiers = ('UNRANKED', 'IRON', 'BRONZE', 'SILVER', 'GOLD', 'PLATINUM', 'EMERALD', 'DIAMOND', 'MASTER', 'GRANDMASTER', 'CHALLENGER')
ranks = ('UNRANKED', 'I', 'II', 'III', 'IV')
messages = []

# Functions

# Get last_match id
def get_new_match(puuid):
  api_url = (
    'https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/' +
    puuid +
    '/ids?start=0&count=1&api_key=' +
    api_key
  )
  resp = requests.get(api_url)
  return resp.json()[0]

# Get match info
def get_match_info(match_id):
  api_url = (
    'https://europe.api.riotgames.com/lol/match/v5/matches/' +
    match_id +
    '?api_key=' +
    api_key
  )
  resp = requests.get(api_url)
  match_info = resp.json()
  return match_info

# Get rank info for ranked solo/duo and flex queues.
def get_rank_info(player_puuid):
  api_url = 'https://eun1.api.riotgames.com/lol/league/v4/entries/by-puuid/' + player_puuid + '?api_key=' + api_key
  resp = requests.get(api_url)
  return resp.json()


# Functions for some of the game modes
def game_modes_info(match_info, player_puuid):
  player_index = match_info['metadata']['participants'].index(player_puuid)
  remake = match_info['info']['participants'][player_index]['gameEndedInEarlySurrender']
  victory = match_info['info']['participants'][player_index]['win']
  player_kills = match_info['info']['participants'][player_index]['kills']
  player_assists = match_info['info']['participants'][player_index]['assists']
  player_deaths = match_info['info']['participants'][player_index]['deaths']
  champion = match_info['info']['participants'][player_index]['championName']
  return (remake, victory, player_kills, player_assists, player_deaths, champion)
  
def PLACEMENT_GAMES_SOLO_DUO(match_info, player_puuid, player_name):
  remake, victory, player_kills, player_assists, player_deaths, champion = game_modes_info(match_info, player_puuid)
  if remake is True:
    message = f"{player_name} remade this match. ( RANKED SOLO/DUO PLACEMENT GAMES )"
  elif victory == True:
    message = f"{player_name} won a match with {champion} scoring {player_kills} kills, {player_deaths} deaths and {player_assists} assists. ( RANKED SOLO/DUO PLACEMENT GAMES )"
  elif victory == False:
    message = f"{player_name} lost a match with {champion} scoring {player_kills} kills, {player_deaths} deaths and {player_assists} assists. ( RANKED SOLO/DUO PLACEMENT GAMES )"
  order_leaderboard((player_name, 'UNRANKED', 'UNRANKED', 0, victory))
  return message

def PLACEMENT_GAMES_FLEX(match_info, player_puuid, player_name):
  remake, victory, player_kills, player_assists, player_deaths, champion = game_modes_info(match_info, player_puuid)
  if remake is True:
    message = f"{player_name} remade this match. ( ARAM )"
  elif victory == True:
    message = f"{player_name} won a match with {champion} scoring {player_kills} kills, {player_deaths} deaths and {player_assists} assists. ( RANKED FLEX PLACEMENT GAMES )"
  elif victory == False:
    message = f"{player_name} lost a match with {champion} scoring {player_kills} kills, {player_deaths} deaths and {player_assists} assists. ( RANKED FLEX PLACEMENT GAMES )"
  return message

def RANKED_SOLO_DUO(match_info, player_puuid, player_name, rank_info):
  tier = rank_info['tier']
  rank = rank_info['rank']
  lp = rank_info['leaguePoints']
  remake, victory, player_kills, player_assists, player_deaths, champion = game_modes_info(match_info, player_puuid)
  if remake is True:
    message = f"{player_name} remade this match. {player_name} is {tier} {rank} {lp} lps. ( RANKED SOLO/DUO )"
  elif victory == True:  
    message = f"{player_name} won a match with {champion} scoring {player_kills} kills, {player_deaths} deaths and {player_assists} assists. {player_name} is {tier} {rank} {lp} lps. ( RANKED SOLO/DUO )"
  elif victory == False:
    message = f"{player_name} lost a match with {champion} scoring {player_kills} kills, {player_deaths} deaths and {player_assists} assists. {player_name} is {tier} {rank} {lp} lps. ( RANKED SOLO/DUO )"
  order_leaderboard((player_name, tier, rank, lp, victory))
  return message

def ARAM(match_info, player_puuid, player_name):
  remake, victory, player_kills, player_assists, player_deaths, champion = game_modes_info(match_info, player_puuid)
  if remake is True:
    message = f"{player_name} remade this match. ( ARAM )"
  elif victory == True:
    message = f"{player_name} won a match with {champion} scoring {player_kills} kills, {player_deaths} deaths and {player_assists} assists. ( ARAM )"
  elif victory == False:
    message = f"{player_name} lost a match with {champion} scoring {player_kills} kills, {player_deaths} deaths and {player_assists} assists. ( ARAM )"
  return message

def RANKED_FLEX(match_info, player_puuid, player_name, rank_info):
  tier = rank_info['tier']
  rank = rank_info['rank']
  lp = rank_info['leaguePoints']
  remake, victory, player_kills, player_assists, player_deaths, champion = game_modes_info(match_info, player_puuid)
  if remake is True:
    message = f"{player_name} remade this match. {player_name} is {tier} {rank} {lp} lps. ( RANKED FLEX )"
  elif victory == True:  
    message = f"{player_name} won a match with {champion} scoring {player_kills} kills, {player_deaths} deaths and {player_assists} assists. {player_name} is {tier} {rank} {lp} lps. ( RANKED FLEX )"
  elif victory == False:
    message = f"{player_name} lost a match with {champion} scoring {player_kills} kills, {player_deaths} deaths and {player_assists} assists. {player_name} is {tier} {rank} {lp} lps. ( RANKED FLEX )"
  return message

def ARENA(match_info, player_puuid, player_name):
  player_index = match_info['metadata']['participants'].index(player_puuid)
  placement = match_info['info']['participants'][player_index]['placement']
  player_kills = match_info['info']['participants'][player_index]['kills']
  player_assists = match_info['info']['participants'][player_index]['assists']
  player_deaths = match_info['info']['participants'][player_index]['deaths']
  champion = match_info['info']['participants'][player_index]['championName']
  if placement == 1:
    message = f"{player_name} got 1st with {champion} scoring {player_kills} kills, {player_deaths} deaths and {player_assists} assists. ( ARENA )"
  elif placement == 2:
    message = f"{player_name} got 2nd with {champion} scoring {player_kills} kills, {player_deaths} deaths and {player_assists} assists. ( ARENA )"
  elif placement == 3:
    message = f"{player_name} got 3rd with {champion} scoring {player_kills} kills, {player_deaths} deaths and {player_assists} assists. ( ARENA )"
  elif placement == 4:
    message = f"{player_name} got 4th with {champion} scoring {player_kills} kills, {player_deaths} deaths and {player_assists} assists. ( ARENA )"
  else:
    message = f"{player_name} is a bot and got bot 4 with {champion}. Score {player_kills}/{player_deaths}/{player_assists}. ( ARENA )"
  return message

def NORMAL_DRAFT_PICK(match_info, player_puuid, player_name):
  remake, victory, player_kills, player_assists, player_deaths, champion = game_modes_info(match_info, player_puuid)
  if remake is True:
    message = f"{player_name} remade this match. ( NORMAL DRAFT PICK )".format(player_name)
  elif victory == True:
    message = f"{player_name} won a match with {champion} scoring {player_kills} kills, {player_deaths} deaths and {player_assists} assists. ( NORMAL DRAFT PICK )"
  elif victory == False:
    message = f"{player_name} lost a match with {champion} scoring {player_kills} kills, {player_deaths} deaths and {player_assists} assists. ( NORMAL DRAFT PICK )"
  return message

def NORMAL_QUICKPLAY(match_info, player_puuid, player_name):
  remake, victory, player_kills, player_assists, player_deaths, champion = game_modes_info(match_info, player_puuid)
  if remake is True:
    message = f"{player_name} remade this match. ( NORMAL QUICKPLAY )".format(player_name)
  elif victory == True:
    message = f"{player_name} won a match with {champion} scoring {player_kills} kills, {player_deaths} deaths and {player_assists} assists. ( NORMAL QUICKPLAY )"
  elif victory == False:
    message = f"{player_name} lost a match with {champion} scoring {player_kills} kills, {player_deaths} deaths and {player_assists} assists. ( NORMAL QUICKPLAY )"
  return message

# Main function

def handle_ranked_solo(match_info, player_puuid, player):
    rank = get_rank_info(player_puuid)
    unranked = True
    for rank_info in rank:
        if rank_info['queueType'] == 'RANKED_SOLO_5x5':
            unranked = False
            return RANKED_SOLO_DUO(match_info, player_puuid, player, rank_info)
    if unranked:
        return PLACEMENT_GAMES_SOLO_DUO(match_info, player_puuid, player)

def handle_ranked_flex(match_info, player_puuid, player):
    rank = get_rank_info(player_puuid)
    unranked = True
    for rank_info in rank:
        if rank_info['queueType'] == 'RANKED_FLEX_SR':
            unranked = False
            return RANKED_FLEX(match_info, player_puuid, player, rank_info)
    if unranked:
        return PLACEMENT_GAMES_FLEX(match_info, player_puuid, player)

# Dictionary mapping match types to functions
match_handlers = {
    420: handle_ranked_solo,
    450: ARAM,
    1700: ARENA,
    440: handle_ranked_flex,
    400: NORMAL_DRAFT_PICK,
    490: NORMAL_QUICKPLAY
}

def program():
  unranked = True
  messages.clear()
  for player in players:
    username, tag = player[0].split('#')
    print(username, tag)
    api_url = "https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/"+ username + "/" + tag + "?api_key=" + api_key
    resp = requests.get(api_url)
    player_puuid = resp.json()['puuid']
    new_match = get_new_match(player_puuid)
    last_match = get_last_match(conn, player[0])
    if new_match != last_match:
      update_last_match(conn, (new_match, player[0]))
      match_info = get_match_info(new_match)
      match_type = match_info['info']['queueId']
      
      handler = match_handlers.get(match_type)
      if handler:
          if callable(handler):
              message = handler(match_info, player_puuid, player[0])
          else:
              message = handler(match_info, player_puuid, player[0])
      else:
          message = f"{player[0]}'s last game is not ARENA, ARAM, RANKED SOLO/DUO, RANKED FLEX, NORMAL BLIND PICK or NORMAL QUICKPLAY."
      
      messages.append(message)
    
# Order leaderboard after every ranked solo/duo match.

def swap_players_positions(info, other_player_info, position):
  update_leaderboard(conn, (info[0], info[1], info[2], info[3], other_player_info[0]))
  update_leaderboard(conn, (other_player_info[1], other_player_info[2], other_player_info[3], other_player_info[4], position))

def order_leaderboard(info):
  player_info = select_player_by_name(conn, info[0])
  total_players = get_players_count(conn)
  if total_players > 1:
    while True:
      stop_flag = False
      current_position = player_info[0]
      should_move_up = info[4] == False and current_position < total_players
      should_move_down = info[4] == True and current_position > 1
      
      if should_move_up:
        other_player_info = select_player_by_id(conn, (current_position + 1))
        
        if other_player_info:
          tier_comparison = tiers.index(info[1]) - tiers.index(other_player_info[2])
          rank_comparison = ranks.index(info[2]) - ranks.index(other_player_info[3])
          lp_comparison = info[3] - other_player_info[4]

          if tier_comparison < 0 or (tier_comparison == 0 and rank_comparison > 0) or (tier_comparison == 0 and rank_comparison == 0 and lp_comparison < 0):
            swap_players_positions(info, other_player_info, current_position)
            player_info = select_player_by_name(conn, info[0])
            stop_flag = True

      elif should_move_down:
        other_player_info = select_player_by_id(conn, (current_position - 1))
        
        if other_player_info:
          tier_comparison = tiers.index(info[1]) - tiers.index(other_player_info[2])
          rank_comparison = ranks.index(info[2]) - ranks.index(other_player_info[3])
          lp_comparison = info[3] - other_player_info[4]

          if tier_comparison > 0 or (tier_comparison == 0 and rank_comparison < 0) or (tier_comparison == 0 and rank_comparison == 0 and lp_comparison > 0):
            swap_players_positions(info, other_player_info, current_position)
            player_info = select_player_by_name(conn, info[0])
            stop_flag = True
            
      else:
        update_leaderboard(conn, (info[0], info[1], info[2], info[3], current_position))
      if not stop_flag:
        update_leaderboard(conn, (info[0], info[1], info[2], info[3], current_position))
        break
   
# Functions for bot commands
        
async def update_rank(player):
  name, tag = player.split('#')
  api_url = "https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/"+ name + "/" + tag + "?api_key=" + api_key
  resp = requests.get(api_url)
  player_puuid = resp.json()['puuid']
  rank = get_rank_info(player_puuid)
  if len(rank) > 0:
    for x in range(len(rank)):
      if rank[x]['queueType'] == 'RANKED_SOLO_5x5':
        rank = rank[x]
        order_leaderboard((player, rank['tier'], rank['rank'], rank['leaguePoints'], True))    
        break  
  
async def add_player(player):
  try:
    name, tag = player.split('#')
    api_url = "https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/"+ name + "/" + tag + "?api_key=" + api_key
    resp = requests.get(api_url)
    player_puuid = resp.json()['puuid']
  except:
    return 'Invalid name'
  player_exists = select_player_by_name(conn, player)
  if player_exists is not None:
    return f'{player} is already in the leaderboard!'
  else:
    rank = get_rank_info(player_puuid)
    if len(rank) > 0:
      for x in range(len(rank)):
        if rank[x]['queueType'] == 'RANKED_SOLO_5x5':
          rank = rank[x]
          add_player_to_players(conn, (player, ''))
          add_player_to_leaderboard(conn, (player, rank['tier'], rank['rank'], rank['leaguePoints']))
          order_leaderboard((player, rank['tier'], rank['rank'], rank['leaguePoints'], True))
          return f'{player} was added to the leaderboard'
    add_player_to_players(conn, (player, ''))
    add_player_to_leaderboard(conn, (player, 'UNRANKED', 'UNRANKED', 0))
    return f'{player} was added to the leaderboard'
  
async def remove_player(player):
  players = get_players(conn)
  for p in players:
    if p[0] == player:
      remove_player_from_players(conn, player)
      remove_player_from_leaderboard(conn, player)
      reorder_leaderboard(conn, 'leaderboard')
      return f'{player} removed from the leaderboard!'
  return f'{player} is not in the leaderboard!'