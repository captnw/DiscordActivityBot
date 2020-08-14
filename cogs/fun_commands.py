from discord.ext import commands
import asyncio

class fun_commands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def ping(self, context):
        #print({role : role.id for role in context.message.author.roles})
        await context.send(f"{int(self.client.latency*1000)}ms")

    @commands.command(aliases = ["Hello","Hi","hi"])
    async def hello(self, context):
        await context.send(f"Hello {context.message.author.mention}")
    

    @commands.command(aliases = ["8ball","8b","eightball"])
    async def Eightball(self, context):
        await context.send("Gamer")

    #@commands.command(aliases = ["spam"])
    #async def Spam(self, context):
    #    while True:
    #        await asyncio.sleep(2)
    #        await context.send("You just got friccin bean'd moron!")

def setup(client):
    client.add_cog(fun_commands(client))