from pathlib import Path
import sys, datetime
sys.path.insert(1, str(Path.cwd()))

from discord.ext import commands
import secretTextfile


async def is_admin(context):
    for role in context.message.author.roles:
        print(str(role), secretTextfile.__ADMIN_ROLE__ , type(role))
        if (role.name == secretTextfile.__ADMIN_ROLE__ ):
            return True
    return False

class admin_commands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases = ["m","M","members"])
    @commands.check(is_admin)
    async def Members(self, context):
        emoji = "\N{THUMBS UP SIGN}"
        await context.message.add_reaction(emoji)
        channel_members = ""    
        #for member in context.message.channel.members:
        #    channel_members += member.name + ", "
        #    await context.send(f"{member.name}'s status is {member.status}")
        #    await context.send(f"{member.name}'s color is {member.color}")
        #    await context.send(f"{member.name}'s role is {member.roles}")
        channel_members = channel_members.rstrip(", ")
        await context.send(f"{channel_members} are in the channel")
    
    
    @Members.error
    async def Members_error(self, context, error):
        if isinstance(error, commands.CommandError):
            emoji = "\N{THUMBS DOWN SIGN}"
            await context.message.add_reaction(emoji)


    @commands.command(aliases = ["die","Die","Shutdown"])
    @commands.check(is_admin)
    async def shutdown(self, context):
        ''' Logs out the bot '''
        emoji = "\N{THUMBS UP SIGN}"
        await context.message.add_reaction(emoji)
        await self.client.logout()


    @shutdown.error
    async def shutdown_error(self, context, error):
        if isinstance(error, commands.CommandError):
            emoji = "\N{THUMBS DOWN SIGN}"
            await context.message.add_reaction(emoji)

def setup(client):
    client.add_cog(admin_commands(client))