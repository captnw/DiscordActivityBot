from pathlib import Path
import sys
sys.path.insert(1, str(Path.cwd()))

from discord.ext import commands
import secretTextfile


async def is_admin(context):
    for role in context.message.author.roles:
        if (role.name == secretTextfile.__ADMIN_ROLE__ ):
            return True
    return False


class admin_commands(commands.Cog):
    def __init__(self, client):
        self.client = client


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