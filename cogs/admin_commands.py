from discord.ext import commands

async def is_admin(context):
    return "740297516305743922" in [str(role.id) for role in context.message.author.roles]

class admin_commands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases = ["m","M","members"])
    @commands.check(is_admin)
    async def Members(self, context):
        channel_members = ""    
        for member in context.message.channel.members:
            channel_members += member.name + ", "
            await context.send(f"{member.name}'s status is {member.status}")
            await context.send(f"{member.name}'s color is {member.color}")
            await context.send(f"{member.name}'s role is {member.roles}")
        channel_members = channel_members.rstrip(", ")
        await context.send(f"{channel_members} are in the channel")
    
    
    @Members.error
    async def Members_error(self, context, error):
        if isinstance(error, commands.CommandError):
            await context.send("You do not have permission to use that command.")


    @commands.command(aliases = ["die","Die","Shutdown"])
    @commands.check(is_admin)
    async def shutdown(self, context):
        ''' Logs out the bot, but there are problems associated with it ... WIP '''
        await self.client.logout()


    @shutdown.error
    async def shutdown_error(self, context, error):
        if isinstance(error, commands.CommandError):
            await context.send("You do not have permission to use that command.")

def setup(client):
    client.add_cog(admin_commands(client))