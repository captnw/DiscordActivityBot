import discord, asyncio, pytz
from discord.ext import commands
from pathlib import Path

import sys, datetime
sys.path.insert(1, str(Path.cwd()))

from csvfile_reader import csv_lookup_schedule, online_freq
from graph_producer import produce_graph, produce_graph_bar


class public_commands(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    
    @commands.command(aliases = ["Myactivity","MyActivity", "ma", "MA"])
    async def myactivity(self, context):
        ''' Print out your current discord online activity. (see the data for the last 10 days) '''
        user_name = str(context.message.author).split("#")[0]
        user_id = context.message.author.id
        pacific = pytz.timezone("US/Pacific") # The timezone being used to record the hour
        now = datetime.datetime.now(pacific)
        lista = csv_lookup_schedule(user_id, now.day)
        produce_graph(lista, user_id, user_name)
        
        image_message = await context.send(file=discord.File(f"./graph_folder/UserAct_{user_id}.png"))

        # Delete the image 1min, 30 seconds after sending it to prevent clogging up space
        await asyncio.sleep(90)
        await image_message.delete()
        
        emoji = "\N{GEAR}"
        await context.message.add_reaction(emoji)


    @commands.command(aliases = ["Serveractivity", "serverActivity", "ServerActivity", "sa", "SA"])
    async def serveractivity(self, context):
        ''' Print a bar graph displaying how many people on average (in the span of a week) are online at various hours. '''
        guild_hash = str(hash(context.message.author.guild))
        guild_name = str(context.message.guild.name)
        days_data_recorded = online_freq[guild_hash]["_DAYS"]
        produce_graph_bar(online_freq[guild_hash]["_FREQ"], guild_name, guild_hash, days_data_recorded) # Get the respective freq graph for the server
        image_message = await context.send(file=discord.File(f"./graph_folder/GuildAct_{guild_hash}.png"))

        # Delete the image 1min, 30 seconds after sending it to prevent clogging up space
        await asyncio.sleep(90)
        await image_message.delete()

        emoji = "\N{GEAR}"
        await context.message.add_reaction(emoji)


def setup(client):
    client.add_cog(public_commands(client))