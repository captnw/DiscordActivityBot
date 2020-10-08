import secretTextfile, asyncio, datetime, pytz, sqlite3
#from discord.ext import commands
from discord.ext.commands import Bot as BotBase
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from csvfile_reader import csv_bootup, csv_shutdown, csv_write_into, csv_lookup_schedule, csv_all_schedule, csv_order_data
import sqlite_handler

from glob import glob
# in this experimental branch, we're switching from csv to .db (using sqlite3)
# we will also be using (asyncpg) so that we can utilize PostgreSQL so that we can use heroku to host our bot

# A lot of code borrowed from Carberra Tutorials (thank you!)
COGS = [path.split("\\")[-1][:-3] for path in glob("./cogs/*.py")] # Fetch cog files
VERSION = "0.5.0" # Bot version

# OLD CSV stuff
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
                old_schedule.append({now.day : [0 for num in range(24)]})

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

        print("Cog setup complete")

    def run(self, version):
        self.VERSION = version
        print("Running ScheduleBot ver "+version)
        print("Setting up cogs...")
        self.setup()
        self.TOKEN = secretTextfile.__TOKEN__

        print("Loading .csv stuff")
        csv_bootup()

        print("Running bot...")
        super().run(self.TOKEN, reconnect=True)

    async def on_connect(self):
        print("Bot connected.")

    async def on_disconnect(self):
        print("Bot disconnected.")
        print("Closing .csv file...")
        csv_shutdown()

    async def on_ready(self):
        if not self.ready:
            self.ready = True
            self.scheduler.add_job(lambda: check_online(self), IntervalTrigger(seconds=30))
            self.scheduler.start()

        else:
            print("Bot reconnected")


bot = Bot()

if __name__ == "__main__":
    try:
        bot.run(VERSION)
    except Exception as e:
        print("Error caught! Error description is shown below...\n{}".format(e))
        print("Closing .csv file...")
        csv_shutdown()
