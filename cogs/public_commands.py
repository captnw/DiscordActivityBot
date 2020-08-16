import discord, asyncio
from discord.ext import commands
from pathlib import Path

import sys, datetime
sys.path.insert(1, str(Path.cwd()))

from csvfile_reader import csv_lookup_schedule
from graph_producer import produce_graph


class public_commands(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    
    @commands.command(aliases = ["Myschedule","MySchedule", "ms", "MS"])
    async def myschedule(self, context):
        ''' Print out your current discord online schedule. See which times the bot '''
        user_name, user_id = (str(context.message.author).split("#"))
        now = datetime.datetime.now()
        lista = csv_lookup_schedule(user_id, now.day)
        produce_graph(lista, user_id, user_name)
        
        image_message = await context.send(file=discord.File(f'./graph_folder/{user_id}.png'))

        # Delete the image 3 minutes after sending it to prevent clogging up space
        await asyncio.sleep(180)
        await image_message.delete()
        
        emoji = "\N{GEAR}"
        await context.message.add_reaction(emoji)


def setup(client):
    client.add_cog(public_commands(client))