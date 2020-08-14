import discord, secretTextfile, asyncio, datetime
from discord.ext import commands
from csvfile_reader import csv_bootup, csv_shutdown, csv_write_into, csv_clear, csv_lookup_schedule, print_schedule
from graph_producer import produce_graph


def check_online(cli : commands.Bot) -> None:
    ''' Determines what members that the bot sees are online at the current hour and stores that info + their
        status into a datastructure (a list of dicts which has a key of string and a value of list of ints)'''
    now = datetime.datetime.now()
    print(f"Checking who is online on {now.month}/{now.day}/{now.year} at {now.hour}:{now.minute}")

    online_people = ""

    for member in client.get_all_members():
        member_id = (str(member).split("#"))[1]
        # Fetching all other data excluding schedule
        member_data = [str(member), str(member.nick), member_id,str(member.status)]
        old_schedule = csv_lookup_schedule(member_id, now.day)

        if not (now.day in old_schedule[-1].keys()):
            # Consider making a new dict if today is different
            if len(old_schedule) == 10:
                # Pop the first element to make room for a new one
                # If we have 10 days worth of data already
                old_schedule.pop(0)
            old_schedule.append({now.day : [0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0]})

        if str(member.status) != "offline":
            # If the member is not offline, update the current hour
            old_schedule[-1][now.day][now.hour-1] = old_schedule[-1][now.day][now.hour-1] | 1
            online_people += str(member) + ", "
        member_data.append(str(old_schedule))
        csv_write_into(member_data)

        #DEBUG PRINT
        #print_schedule()

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
    extensions = ["cogs.fun_commands", "cogs.admin_commands", "cogs.public_commands"]
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


    client.run(secretTextfile.__TOKEN__)
    # DO NOT ADD CODE AFTER THIS B/C client.run NEVER RETURNS