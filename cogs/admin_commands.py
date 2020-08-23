from pathlib import Path
import sys, asyncio
sys.path.insert(1, str(Path.cwd()))

from discord.ext import commands
import secretTextfile


async def is_admin(context):
    for role in context.message.author.roles:
        #print(str(role), secretTextfile.__ADMIN_ROLE__ , type(role))
        if (role.name == secretTextfile.__ADMIN_ROLE__ ):
            return True
    return False

class admin_commands(commands.Cog):
    def __init__(self, client):
        self.client = client


    @commands.command(aliases = ["m","M","members"])
    @commands.check(is_admin)
    async def Members(self, context):
        """ Fetches all online members and prints them out """
        # React to the user with a thumbs up
        emoji = "\N{THUMBS UP SIGN}"
        await context.message.add_reaction(emoji)

        # Do the fetching of members, making sure these members are in the same guild as the user
        currentGuild = context.message.author.guild
        channel_members = ""    
        for member in context.message.channel.members:
            if str(member.status) != "offline" and member.guild == currentGuild and (not member.bot):
                channel_members += member.name + ", "
        channel_members = channel_members.rstrip(", ")
    
        if (channel_members.find(",")):
            status_message = await context.send(f"{channel_members} are online in this server right now.")
        elif (channel_members == ""):
            status_message = await context.send("Nobody is online in this server right now.")
        else:
            status_message = await context.send(f"{channel_members} is online in this server right now.")

        # Delete the status_message 1min, 30 seconds after sending it to prevent clogging up space
        await asyncio.sleep(90)
        await status_message.delete()

        emoji = "\N{GEAR}"
        await context.message.add_reaction(emoji)
    
    @Members.error
    async def Members_error(self, context, error):
        if isinstance(error, commands.CommandError):
            emoji = "\N{THUMBS DOWN SIGN}"
            await context.message.add_reaction(emoji)


    @commands.command(aliases = ["die","Die","Shutdown"])
    @commands.check(is_admin)
    async def shutdown(self, context):
        """ Logs out the bot """
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