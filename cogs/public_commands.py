#from discord.ext import commands
#from pathlib import Path
#print(str(Path.cwd()))
#import "..//graph_producer."


#class public_commands(commands.Cog):
#    def __init__(self, client):
#        self.client = client

#    @commands.command()
#    async def ping(self, context):
#        print({role : role.id for role in context.message.author.roles})
#        await context.send(f"{int(self.client.latency*1000)}ms")


#def setup(client):
#    client.add_cog(public_commands(client))