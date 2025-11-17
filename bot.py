import os
from datetime import datetime

import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio

from database import conn, select_leaderboard, get_players, reset_leaderboard_table
from discordBot import update_rank, program, messages, add_player, remove_player

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
AUTHORIZED_USER_ID = os.getenv('DISCORD_ADMIN_ID')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)
client = discord.Client(intents=intents)

async def show_leaderboard():
  leaderboard = select_leaderboard(conn)
  if not leaderboard:
    return 'Leaderboard is empty!'
  final_leaderboard = ''
  for x in leaderboard:
    player = '{}. {} {} {} {}.\n'.format(x[0], x[1], x[2], x[3], x[4])
    final_leaderboard += player
  return final_leaderboard
  
async def reset_leaderboard():
  players = get_players(conn)
  for player in players:
    reset_leaderboard_table(conn, player[0])
    await update_rank(player[0])
    
async def check_player():
  channel = bot.get_channel(1111633524659867658)
  program()
  print(messages)
  for message in messages.copy():
    await channel.send(message)
    messages.remove(message)
        
@bot.event
async def on_ready():
  while True:
    now = datetime.now()
    print(f'We have logged in as {bot.user.name}. {now.strftime("%H:%M:%S")}')
    await check_player()
    await asyncio.sleep(600)
    
@bot.command()
async def leaderboard(ctx):
  await ctx.send(await show_leaderboard())
  
@bot.command()
async def reset(ctx):
  if ctx.author.id not in AUTHORIZED_USER_ID:
    await ctx.send('Nope!')
    return
  await reset_leaderboard()
  print('Leaderboard reset successfully!')
  await ctx.send('Done!')
  
@bot.command()
async def add(ctx, arg=None):
    if arg is None:
        await ctx.send("Add a player!")
        return
    if ctx.author.id not in AUTHORIZED_USER_ID:
        await ctx.send('Nope!')
        return
    output = await add_player(arg)
    await ctx.send(output)
    
@bot.command()
async def remove(ctx, arg=None):
    if arg is None:
        await ctx.send("Add a player!")
        return
    if ctx.author.id not in AUTHORIZED_USER_ID:
        await ctx.send('Nope!')
        return
    output = await remove_player(arg)
    await ctx.send(output)

bot.run(TOKEN)