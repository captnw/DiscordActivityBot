import discord, secretTextfile
from discord.ext import commands
from csvfile_reader import *


def begin_phrase(msg, listA: list) -> bool:
    ''' Helper function to check for alias, returns bool '''
    returnVal = False
    for alias in listA:
        returnVal = returnVal or msg.content.startswith(alias)
    return returnVal


if __name__ == "__main__":

    client = commands.Bot(command_prefix = '!')
    extensions = ["cogs.fun_commands", "cogs.admin_commands"]
    for ext in extensions:
        client.load_extension(ext)

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


    #@client.command()
    #async def startCsv(context):
    #    csv_bootup()

    
    #@client.command()
    #async def stopCsv(context):
    #    csv_shutdown()
    

    client.run(secretTextfile.__TOKEN__)
    # DO NOT ADD CODE AFTER THIS B/C client.run NEVER RETURNS