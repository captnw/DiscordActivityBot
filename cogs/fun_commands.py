from discord.ext import commands
import random

class fun_commands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def ping(self, context):
        """ See your own ping. """
        await context.send(f"{int(self.client.latency*1000)}ms")


    @commands.command(aliases = ["Hello","Hi","hi"])
    async def hello(self, context):
        """ Say hi to the bot. """
        await context.send(f"Hello {context.message.author.mention}")
    
    
    @commands.command(aliases = ["8ball","8b","eightball"])
    async def Eightball(self, context):
        """ Ask a yes/no question and recieve a (helpful?) answer. """
        responses = [
            "As I see it, yes.", "Ask again later.", "Better not tell you now.", "Cannot predict now.",
            "Concentrate and ask again.", "Don’t count on it.", "It is certain.", "It is decidedly so.",
            "Most likely.", "My reply is no.", "My sources say no.", "Outlook not so good.",
            "Outlook good.", "Reply hazy, try again.", "Signs point to yes.", "Very doubtful.", "Without a doubt.",
            "Yes.", "Yes – definitely.", "You may rely on it."
        ]
        await context.send(responses[random.randint(0, len(responses)-1)])


def setup(client):
    client.add_cog(fun_commands(client))