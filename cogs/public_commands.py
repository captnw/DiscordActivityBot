import discord
from discord.ext import commands
from pathlib import Path

import sys, datetime
sys.path.insert(1, str(Path.cwd()))
#print(str(Path.cwd()))

from csvfile_reader import csv_lookup_schedule
from graph_producer import produce_graph

class public_commands(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.command(aliases = ["Myschedule","MySchedule", "ms", "MS"])
    async def myschedule(self, context):
        user_id = (str(context.message.author).split("#"))[1]
        now = datetime.datetime.now()
        lista = csv_lookup_schedule(user_id, now.day)
        #print(lista)
        produce_graph(lista, user_id)
        
        await context.send(file=discord.File(f'./graph_folder/{user_id}.png'))

def setup(client):
    client.add_cog(public_commands(client))