from discord.ext import commands

class admin_commands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases = ["m","M","members"])
    async def Members(self, context):
        channel_members = ""    
        for member in context.message.channel.members:
            channel_members += member.name + ", "
            await context.send(f"{member.name}'s status is {member.status}")
            await context.send(f"{member.name}'s color is {member.color}")
            await context.send(f"{member.name}'s role is {member.roles}")
        await context.send(f"{channel_members} are in the channel")

    @commands.command(aliases = ["die","Die","Shutdown"])
    async def shutdown(self, context):
        ''' Logs out the bot, but there are problems associated with it ... WIP '''
        await self.client.logout()

def setup(client):
    client.add_cog(admin_commands(client))