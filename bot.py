import secretTextfile, asyncio, datetime, pytz, sqlite3
from discord.ext.commands import Bot as BotBase
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
# from csvfile_reader import csv_bootup, csv_shutdown, csv_write_into, csv_lookup_schedule, csv_all_schedule, csv_order_data
import sqlite_handler
import os
from glob import glob

# in this experimental branch, we're switching from csv to .db (using sqlite3)
# we will also be using (asyncpg) so that we can utilize PostgreSQL so that we can use heroku to host our bot

# A lot of code borrowed from Carberra Tutorials (thank you!)
COGS = [path.split("\\")[-1][:-3] for path in glob("./cogs/*.py")] # Fetch cog files
VERSION = "0.5.0" # Bot version

# OLD CSV stuff
"""
def check_online(client) -> None:
    ''' Determines what members that the bot sees are online at the current hour and stores that info + their
        status into a datastructure (a list of dicts which has a key of string and a value of list of ints)'''
    pacific = pytz.timezone("US/Pacific") # The timezone being used to record the hour
    now = datetime.datetime.now(pacific)
    print(f"Checking who is online on {now.month}/{now.day:02}/{now.year} at {now.hour:02}:{now.minute:02}:{now.second:02} PST.")

    online_people = ""

    for member in sorted(client.get_all_members(), key = lambda x : str(x).split("#")[0].lower()):
        if not (member.bot):
            # Fetching all other data excluding schedule
            # If added new labels, MUST ADD NEW KEY AND VALUE BELOW FOR AFOREMENTIONED LABELS
            unordered_data = {"_NAME":str(member), "_NICKNAME":str(member.nick), "_ID":member.id, "_GUILD":str(hash(member.guild)), "_STATUS":str(member.status)}
            old_schedule = csv_lookup_schedule(member.id, now.day)
            if not (now.day in old_schedule[-1].keys()):
                # Consider making a new dict if today is different
                if len(old_schedule) == 10:
                    # Pop the first element to make room for a new one
                    # If we have 10 days worth of data already
                    old_schedule.pop(0)
                old_schedule.append({now.day : [0 for _ in range(24)]})

            if str(member.status) != "offline":
                # If the member is not offline, update the current hour
                old_schedule[-1][now.day][now.hour-1] = old_schedule[-1][now.day][now.hour-1] | 1
                online_people += member.name + ", "

            unordered_data["_SCHEDULE"] = str(old_schedule)
            member_data = csv_order_data(unordered_data)
            csv_write_into(member_data)

    csv_all_schedule() # update the online frequency list

    if online_people != "":
        online_people = online_people.rstrip(", ")
        if (online_people.find(",")):
            print("{} are online right now.\n".format(online_people))
        else:
            print("{} is online right now.\n".format(online_people))
    else:
        print("Nobody is online right now.\n")
"""

def header(*args) -> None:
    ''' Clears the terminal, print the header, and prints any additional strings passed in'''
    os.system('cls' if os.name=='nt' else 'clear') # Clears the terminal
    print(f"\\\\_ScheduleBot v.{VERSION}_//")
    for string in args: print(string)


def check_update_online(client) -> None:
    ''' Check what discord users that the bot sees (in any server) are online at the current hour and stores that info + their
    status into a datastructure (a list of dicts which has a key of string and a value of list of ints)'''
    now = datetime.datetime.now(pytz.UTC) # UTC time
    header(f"Checking who is online on {now.month}/{now.day:02}/{now.year} at {now.hour:02}:{now.minute:02}:{now.second:02} UTC.")
    online_people = ""

    all_member_data = [] # store all member data for a one time write open cycle (open sql, write in sql, close sql)
    for member in sorted(client.get_all_members(), key = lambda x : str(x).split("#")[0].lower()):
        if (not (member.bot)):
            if str(member.status) != "offline":
                online_people += member.name + ", "
            dict_data = {"NAME":str(member), "NICKNAME":str(member.nick), "ID":member.id, 
                        "GUILD_ID":str(hash(member.guild)), "STATUS":str(member.status)
                        ,"SCHEDULE":str([[]])}
            all_member_data.append(tuple(sqlite_handler.order_dict(dict_data)))

    sqlite_handler.insert_update(all_member_data)
    
    
    
    print("Insertion completed!")

    if online_people != "":
        online_people = online_people.rstrip(", ")
        if (online_people.find(",")):
            print("{} are online right now.\n".format(online_people))
        else:
            print("{} is online right now.\n".format(online_people))
    else:
        print("Nobody is online right now.\n")


class Bot(BotBase):
    def __init__(self):
        self.ready = False
        self.scheduler = AsyncIOScheduler()

        #sqlite_handler.test_print(self.scheduler)
        super().__init__(command_prefix='!')

    def setup(self):
        # LOAD COGS
        for cog in COGS:
            self.load_extension(f"cogs.{cog}")
            print(f"{cog} cog loaded")
        print("\nCog setup complete")

    def run(self, version):
        self.VERSION = version
        header("Setting up cogs...")
        self.setup()
        self.TOKEN = secretTextfile.__TOKEN__

        print("\nLoading .sqlite stuff")
        #csv_bootup()

        print("\nRunning bot...")
        super().run(self.TOKEN, reconnect=True)

    async def on_connect(self):
        print("\nBot connected.")

    async def on_disconnect(self):
        header("Bot disconnected.")
        print("Closing .sqlite file...")
        #csv_shutdown()

    async def on_ready(self):
        now = datetime.datetime.now(pytz.UTC) # UTC time
        if not self.ready:
            self.ready = True
            self.scheduler.add_job(lambda: check_update_online(self), IntervalTrigger(seconds=10))
            self.scheduler.start()
            header("Bot logged in as:")
            print("Username: {}".format(self.user.name))
            print("User id: {}".format(self.user.id))
            print('------\n')
            print(f"Bot ready on {now.month}/{now.day:02}/{now.year} at {now.hour:02}:{now.minute:02}:{now.second:02} UTC.")
        else:
            header(f"Bot reconnected on {now.month}/{now.day:02}/{now.year} at {now.hour:02}:{now.minute:02}:{now.second:02} UTC.")


bot = Bot()

if __name__ == "__main__":
    try:
        bot.run(VERSION)
    except Exception as e:
        print("\n___________ERROR_CAUGHT_______________")
        print("Error description is shown below...\n{}".format(e))
        print("Closing .sqlite file...")
        #csv_shutdown()
