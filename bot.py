import discord, secretTextfile, asyncio, datetime
from discord.ext import commands
from csvfile_reader import *


def check_online(cli : commands.Bot) -> None:
    now = datetime.datetime.now()
    print(f"Checking who is online on {now.month}/{now.day}/{now.year} at {now.hour}:{now.minute}")

    online_people = ""

    # currently schedule is 1D and doesn't reflect the day ... 
    # work on it tomorrow

    for member in client.get_all_members():
        member_id = (str(member).split("#"))[1]
        member_data = [str(member), str(member.nick), member_id,str(member.status)]
        old_schedule = csv_lookup_schedule(member_id)
        if str(member.status) != "offline":
            old_schedule[now.hour] = old_schedule[now.hour] or True
            online_people += str(member) + ", "
        member_data.append(str(old_schedule))
        csv_write_into(member_data)

    if online_people != "":
        online_people = online_people.rstrip(", ")
        print("{} are online right now.".format(online_people))
    else:
        print("Nobody is online right now.")


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

        while True:
            check_online(client)
            await asyncio.sleep(900)

    @client.event
    async def on_disconnect():
        print("Bot is now offline.")
        csv_shutdown()


    @client.event
    async def on_message_delete(message):
        ''' Bot announces that somebody has deleted something. '''
        await message.channel.send(f"{message.author.name} has hidden a message. ")


    #@client.event
    #async def on_member_update(before, after):
    #    print("A member's status has changed.")
    #    # Now it's name, nickname, id, status, schedule
    #    csv_write_into([str(after), after.nick, (str(after).split("#"))[1],after.status])
    #    print("Before: {}".format(big_struct))
    #    print("After: {}".format(big_struct))


    #@client.command()
    #async def startCsv(context):
    #    csv_bootup()

    
    #@client.command()
    #async def stopCsv(context):
    #    csv_shutdown()
    

    client.run(secretTextfile.__TOKEN__)
    # DO NOT ADD CODE AFTER THIS B/C client.run NEVER RETURNS