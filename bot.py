from ast import literal_eval as astEVAL
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from collections import defaultdict 
from datetime import datetime as DateTime
from discord.ext.commands import Bot as BotBase
from glob import glob
from graph_producer import clear_graph_folder
from os import system as osSYSTEM, name as osNAME
from pytz import UTC
import secretTextfile, sqlite_handler

# in this experimental branch, we're switching from csv to .db (using sqlite3)

# Some of the template bot code borrowed from Carberra Tutorials (thank you!)
COGS = [path.split("\\")[-1][:-3] for path in glob("./cogs/*.py")] # Fetch cog files
VERSION = "0.5.0" # Bot version


def prompt_header(*args) -> None:
    ''' Clears the terminal, print the header, and prints any additional strings passed in'''
    osSYSTEM('cls' if osNAME=='nt' else 'clear') # Clears the terminal
    print(f"\\\\_ScheduleBot v.{VERSION}_//")
    for string in args: print(string)


def check_update_online(client) -> None:
    ''' Check what discord users that the bot sees (in any server) are online at the current hour and stores that info + their
    status into a datastructure (a list of dicts which has a key of string and a value of list of ints)'''
    now = DateTime.now(UTC) # UTC time
    prompt_header(f"Checking who is online on {now.month}/{now.day:02}/{now.year} at {now.hour:02}:{now.minute:02}:{now.second:02} UTC.")
    
    online_server = defaultdict(list) # key - guild, val - list of people online
    all_member_data = [] # store all member data for a one time write open cycle (open sql, write in sql, close sql)
    inserted_user_id = set() # keep track of user ids that we have inserted so far
    sqlite_handler.reset_freq_graph()
    for member in sorted(client.get_all_members(), key = lambda x : str(x).split("#")[0].lower()):
        if (not (member.bot)):
            
            if (member.id in inserted_user_id):
                # Check if we have already inserted a record belonging to this user into all_member_data
                # This means that the user is in multiple servers

                for index in range(0, len(all_member_data)):
                    if all_member_data[index][1] == member.id:
                        # Found it, update guild_hash_list
                        guild_hash_list = astEVAL(all_member_data[index][2])
                        if hash(member.guild) not in guild_hash_list:
                            guild_hash_list.append(hash(member.guild))
                            all_member_data[index] = tuple([item if index != 2 else str(guild_hash_list) for index, item in enumerate(all_member_data[index])])
                        # Double check if the user is online in a different server
                        if (member.name not in online_server[member.guild]):
                            online_server[member.guild].append(member.name)
                        break
            else:
                inserted_user_id.add(member.id)
                unordered_data = {"NAME":str(member), "ID":member.id, 
                                "STATUS":str(member.status), "TIMEZONE":sqlite_handler.fetch_timezone(member.id)}
                old_hashlist = sqlite_handler.fetch_guild_hashes(member.id, hash(member.guild))
                old_schedule = sqlite_handler.fetch_schedule(member.id, now.day, old_hashlist)

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
                unordered_data["GUILD_HASH_LIST"] = str(old_hashlist)
                all_member_data.append(tuple(sqlite_handler.order_dict(unordered_data)))

    sqlite_handler.insert_update(all_member_data)
    sqlite_handler.average_freq_graph()

    if not bool(online_server):
        print("Nobody is online right now.\n")
    else:
        for guild, member_list in online_server.items():
            print(f"|| {str(guild)} server:")
            online_people = (", ".join(member_list)).rstrip(", ")
            if (online_people.find(",") != -1):
                print("{} are online right now.\n".format(online_people))
            else:
                print("{} is online right now.\n".format(online_people))


class Bot(BotBase):
    def __init__(self):
        self.ready = False
        self.scheduler = AsyncIOScheduler()
        super().__init__(command_prefix='=')

    def setup(self):
        # LOAD COGS
        for cog in COGS:
            self.load_extension(f"cogs.{cog}")
            print(f"{cog} cog loaded")
        print("\nCog setup complete")
        # Clean graph folder
        clear_graph_folder()
        print("\nClean graph folder check complete")

    def run(self, version):
        self.VERSION = version
        prompt_header("Setting up cogs...")
        self.setup()
        self.TOKEN = secretTextfile.__TOKEN__

        print("\nRunning bot...")
        super().run(self.TOKEN, reconnect=True)

    async def on_connect(self):
        print("\nBot connected.")

    async def on_disconnect(self):
        prompt_header("Bot disconnected.")
        clear_graph_folder()

    async def on_ready(self):
        if not self.ready:
            self.ready = True
            self.scheduler.add_job(lambda: check_update_online(self), IntervalTrigger(minutes=2))
            self.scheduler.start()
            prompt_header("Bot logged in as:")
            print("Username: {}".format(self.user.name))
            print("User id: {}".format(self.user.id))
            print('------\n')
            print(f"Bot ready.")
        else:
            prompt_header(f"Bot reconnected.")
        check_update_online(self) # call this function so that it always runs once after it is ready

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
        clear_graph_folder()