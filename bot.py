import discord
from discord.ext import commands
from csvfile_reader import *
import time


def begin_phrase(msg, listA: list) -> bool:
    ''' Helper function to check for alias, returns bool '''
    returnVal = False
    for alias in listA:
        returnVal = returnVal or msg.content.startswith(alias)
    return returnVal


if __name__ == "__main__":

    client = commands.Bot(command_prefix = '!')
    
    @client.event
    async def on_ready():
        print("Logged in as")
        print(client.user.name)
        print(client.user.id)
        print('------')
        csv_bootup()


    @client.event
    async def on_disconnect():
        print("Bot is actually disconnected.")
        csv_shutdown()


    @client.event
    async def on_message_delete(message):
        ''' Bot prints message people tried to delete '''
        await message.channel.send(f"{message.author.name} tried to hide this message: {message.content}")


    @client.event
    async def on_member_update(before, after):
        print("A member's status has changed or something Idk")
        # Now it's name, nickname, id, status, schedule
        csv_write_into([str(after), after.nick, (str(after).split("#"))[1],after.status])
        print("Before: {}".format(big_struct))
        print("After: {}".format(big_struct))


    @client.command(aliases = ["Hello","Hi","hi"])
    async def hello(context):
        await context.send(f"Hello {context.message.author.mention}")
    

    @client.command(aliases = ["8ball","8b","eightball"])
    async def Eightball(context):
        await context.send("Gamer")


    @client.command(aliases = ["m","M","members"])
    async def Members(context):
        channel_members = ""    
        for member in context.message.channel.members:
            channel_members += member.name + ", "
            await context.send(f"{member.name}'s status is {member.status}")
            await context.send(f"{member.name}'s color is {member.color}")
            await context.send(f"{member.name}'s role is {member.roles}")
        await context.send(f"{channel_members} are in the channel")


    @client.command(aliases = ["die","Die","Shutdown"])
    async def shutdown(context):
        ''' Logs out the bot, but there are problems associated with it ... WIP '''
        await client.logout()


    #@client.command()
    #async def startCsv(context):
    #    csv_bootup()

    
    #@client.command()
    #async def stopCsv(context):
    #    csv_shutdown()
    

    client.run("NzM4MTM1NTE0ODUwNTI1MzM3.XyHgRA.4nQ2q7_IqeKMKm_STOlhyJLV9pU")
    # DO NOT ADD CODE AFTER THIS B/C client.run NEVER RETURNS