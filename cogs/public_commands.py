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
    
    
    @commands.command(aliases = ["Myschedule","MySchedule", "ms", "MS"])
    async def myschedule(self, context):
        ''' Print out your current discord online schedule. (see the data for the last 10 days) '''
        user_name, user_id = (str(context.message.author).split("#"))
        pacific = pytz.timezone("US/Pacific") # The timezone being used to record the hour
        now = datetime.datetime.now(pacific)
        lista = csv_lookup_schedule(user_id, now.day)
        produce_graph(lista, user_id, user_name)
        
        image_message = await context.send(file=discord.File(f"./graph_folder/{user_id}.png"))

        # Delete the image 1min, 30 seconds after sending it to prevent clogging up space
        await asyncio.sleep(90)
        await image_message.delete()
        
        emoji = "\N{GEAR}"
        await context.message.add_reaction(emoji)


    @commands.command(aliases = ["Activehours", "activeHours", "ActiveHours", "ah", "AH"])
    async def activehours(self, context):
        ''' Print a bar graph displaying how often people are online at certain hours. (Work in progress ; does nothing so far) '''
        produce_graph_bar(online_freq[str(hash(context.message.author.guild))]) # Get the respective freq graph for the server
        image_message = await context.send(file=discord.File("./graph_folder/OnlineFrequency.png"))

        # Delete the image 1min, 30 seconds after sending it to prevent clogging up space
        await asyncio.sleep(90)
        await image_message.delete()

        emoji = "\N{GEAR}"
        await context.message.add_reaction(emoji)


def setup(client):
    client.add_cog(public_commands(client))