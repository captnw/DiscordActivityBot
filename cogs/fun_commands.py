from discord.ext import commands

class fun_commands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def ping(self, context):
        await context.send(f"{int(self.client.latency*1000)}ms")

    @commands.command(aliases = ["Hello","Hi","hi"])
    async def hello(self, context):
        await context.send(f"Hello {context.message.author.mention}")
    

    @commands.command(aliases = ["8ball","8b","eightball"])
    async def Eightball(self, context):
        await context.send("Gamer")

def setup(client):
    client.add_cog(fun_commands(client))