import secretTextfile, datetime, pytz
from collections import defaultdict 
from discord.ext.commands import Bot as BotBase
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import sqlite_handler
from os import system as osSYSTEM, name as osNAME
from glob import glob

# in this experimental branch, we're switching from csv to .db (using sqlite3)
# we will also be using (asyncpg) so that we can utilize PostgreSQL so that we can use heroku to host our bot

# A lot of code borrowed from Carberra Tutorials (thank you!)
COGS = [path.split("\\")[-1][:-3] for path in glob("./cogs/*.py")] # Fetch cog files
VERSION = "0.5.0" # Bot version


def header(*args) -> None:
    ''' Clears the terminal, print the header, and prints any additional strings passed in'''
    osSYSTEM('cls' if osNAME=='nt' else 'clear') # Clears the terminal
    print(f"\\\\_ScheduleBot v.{VERSION}_//")
    for string in args: print(string)


def check_update_online(client) -> None:
    ''' Check what discord users that the bot sees (in any server) are online at the current hour and stores that info + their
    status into a datastructure (a list of dicts which has a key of string and a value of list of ints)'''
    now = datetime.datetime.now(pytz.UTC) # UTC time
    header(f"Checking who is online on {now.month}/{now.day:02}/{now.year} at {now.hour:02}:{now.minute:02}:{now.second:02} UTC.")
    
    online_server = defaultdict(list) # key - guild, val - list of people online
    all_member_data = [] # store all member data for a one time write open cycle (open sql, write in sql, close sql)
    
    for member in sorted(client.get_all_members(), key = lambda x : str(x).split("#")[0].lower()):
        if (not (member.bot)):
            unordered_data = {"NAME":str(member), "NICKNAME":str(member.nick), "ID":member.id, 
                        "GUILD_HASH":str(hash(member.guild)), "STATUS":str(member.status)}
            old_schedule = sqlite_handler.fetch_schedule(member.id, str(hash(member.guild)), now.day)

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
                online_server[member.guild].append(member.name)
            unordered_data["SCHEDULE"] = str(old_schedule)
            all_member_data.append(tuple(sqlite_handler.order_dict(unordered_data)))

    sqlite_handler.insert_update(all_member_data)

    if not bool(online_server):
        print("Nobody is online right now.\n")
    else:
        for guild, member_list in online_server.items():
            print(f"|| {str(guild)} server:")
            online_people = (", ".join(member_list)).rstrip(", ")
            if (online_people.find(",")):
                print("{} are online right now.\n".format(online_people))
            else:
                print("{} is online right now.\n".format(online_people))


class Bot(BotBase):
    def __init__(self):
        self.ready = False
        self.scheduler = AsyncIOScheduler()
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

        print("\nRunning bot...")
        super().run(self.TOKEN, reconnect=True)

    async def on_connect(self):
        print("\nBot connected.")

    async def on_disconnect(self):
        header("Bot disconnected.")

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
        print("Shutting bot down...")
        for job in bot.scheduler.get_jobs():
            job.remove()
        bot.scheduler.shutdown()