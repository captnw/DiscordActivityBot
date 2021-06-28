from ast import literal_eval as astEVAL
from asyncio import sleep as asyncioSLEEP
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from collections import defaultdict 
from datetime import datetime as DateTime
from discord import Status as discordSTATUS, Activity as discordACTIVITY, ActivityType as discordACTIVITYTYPE, Intents as discordINTENTS
from discord.ext.commands import Bot as BotBase
from glob import glob
import library.secretTextfile as secretTextfile, library.sqlite_handler as sqlite_handler, library.graph_producer as graph_producer
import library.id_obfuscater as id_obfuscater
from os import system as osSYSTEM, name as osNAME, path as osPATH
from pytz import timezone as pytzTIMEZONE, UTC as pytzUTC

# Run the "StartBot.bat" (for windows) or "StartBot.sh" (for mac/linux) to run the bot
# the first StartBot .bat/.sh file should install the required python packages, and initialize and enter the pyenv virtual environment
# the second StartBot .bat/.sh file would run the bot and keep it on if it turns off
# you can abort any of these commands via control + c.

# Settings and global variables
BOT_ACTIVITY = discordACTIVITY(name="for =help", type=discordACTIVITYTYPE.watching)
CHECK_INTERVAL_SECONDS = 120 # Interval between when check_update_online is called, recommended minimum: 30 seconds
COGS = [path.split("\\")[-1][:-3] for path in glob("./cogs/*.py")] # Fetch cog files
CURRENT_TZ = pytzTIMEZONE(secretTextfile.PREFERRED_TIMEZONE) # Timezone for the command prompt
DEBUG_MODE = False # disables the countdown clock and users who were online GUI
ERROR_LOG_FILE = "error.txt" # name of error file
VERSION = "1.5.0" # Bot version
USERNAMES_DISPLAYED_IN_SERVER_LIMIT = 50 # how many users that were online can be displayed under the server name in the GUI at once (prevents clutter) 

sigint_triggered = False # has the sigint been triggered?
online_message = "" # stores who is online at the time when check_update_online is called

# Some of the template bot code borrowed from Carberra Tutorials (thank you!)
class Bot(BotBase):
    def __init__(self):
        self.ready = False
        self.scheduler = AsyncIOScheduler()
        intents = discordINTENTS.default()
        intents.members = True # this allows the bot to see other members
        intents.presences = True # this allows the bot to see other member's presences
        intents.reactions = True # allows the bot to react to comments
        intents.messages = True # allow the bot to send server and direct messages
        super().__init__(command_prefix='=', intents=intents)

    def setup(self):
        # LOAD COGS
        for cog in COGS:
            self.load_extension(f"cogs.{cog}")
            print(f"{cog} cog loaded")
        print("\nCog setup complete")
        # clean the images associated with any commands
        graph_producer.clear_graph_folder()
        print("\nClean graph folder check complete")

    def run(self, version):
        self.VERSION = version
        prompt_header("Setting up cogs...\n")
        self.setup()
        self.TOKEN = secretTextfile.BOT_TOKEN

        print("\nRunning bot...")
        super().run(self.TOKEN, reconnect=True)

    async def on_connect(self):
        print("\nBot connected.")

    async def on_disconnect(self):
        prompt_header("Bot disconnected.\n")

        if activityBot.scheduler.running:
            activityBot.scheduler.remove_all_jobs()
            activityBot.scheduler.shutdown()

    async def on_ready(self):
        if not self.ready:
            self.ready = True
            if not DEBUG_MODE:
                self.scheduler.add_job(check_prompt, IntervalTrigger(seconds=CHECK_INTERVAL_SECONDS), 
                    replace_existing=True, id="CountdownClock", max_instances = 2, next_run_time = DateTime.now(CURRENT_TZ))
            self.scheduler.add_job(lambda: check_update_online(self), IntervalTrigger(seconds=CHECK_INTERVAL_SECONDS), 
                replace_existing=True, id="CheckUpdate", next_run_time = DateTime.now(CURRENT_TZ)) # check every 2 minutes
            
            self.scheduler.start()

            prompt_header("Bot logged in as:\n")
            print("Username: {}".format(self.user.name))
            print("User id: {}".format(self.user.id))
            print('------\n')
            print("Bot ready." if not DEBUG_MODE else "Bot ready. Running in debug mode.")
        else:
            prompt_header(f"Bot reconnected.")

        await self.change_presence(status=discordSTATUS.online, activity=BOT_ACTIVITY)


def prompt_header(*args) -> None:
    ''' Clears the terminal, print the header, and prints any additional strings EXACTLY as they are passed in'''
    osSYSTEM('cls' if osNAME=='nt' else 'clear') # Clears the terminal
    print(f"\\\\ ActivityBot v.{VERSION} //")
    for string in args: 
        print(string, end="")
    

async def check_prompt():
    ''' Prints when check_update_online was last called, a clock of when it will be called again, and the list of people
        who were online in any server when check_update_online was called. '''
    now = DateTime.now(CURRENT_TZ) 
    time_left = CHECK_INTERVAL_SECONDS # in seconds, max is 3600 (1 hr), min is 0 seconds
    time_left -= 6 # shave off 6 seconds to prevent overlapping coroutines

    divider_width = 60 # characters
    HORIZONTAL_DIVIDER = "-"*divider_width+"\n"
    lastcheck_message = f"Last checked who was online on {now.hour:02}:{now.minute:02}:{now.second:02} at {now.month}/{now.day:02}/{now.year} ({secretTextfile.PREFERRED_TIMEZONE} format).\n"
    
    global online_message

    while time_left >= 0:
        # Construct the string and print it all at once to reduce screen flickering
        time_left_mins, time_left_secs = divmod(time_left, 60)
        nextcheck_message = f"Next online check will be in: ({time_left_mins:02}:{time_left_secs:02})\n"
        if online_message == "":
            prompt_header(lastcheck_message, nextcheck_message, HORIZONTAL_DIVIDER,"Data pending...\n", HORIZONTAL_DIVIDER)
        else:
            prompt_header(lastcheck_message, nextcheck_message, HORIZONTAL_DIVIDER, online_message, HORIZONTAL_DIVIDER, lastcheck_message, nextcheck_message)
        time_left -= 1
        await asyncioSLEEP(1)


def check_update_online(client) -> None:
    ''' Check what discord users that the bot sees (in any server) are online at the current hour and stores that info + their
    status into a datastructure (a list of dicts which has a key of string and a value of list of ints) '''
    
    now = DateTime.now(pytzUTC) # MUST BE UTC time
    
    global online_message
    online_message = "" # reset the message
    online_server = defaultdict(list) # key - guild, val - list of people online
    all_member_data = [] # store all member data for a one time write open cycle (open sql, write in sql, close sql)
    inserted_user_id = set() # keep track of user ids that we have inserted so far
    sqlite_handler.reset_freq_graph()

    for member in sorted(client.get_all_members(), key = lambda x : str(x).split("#")[0].lower()):
        if (not (member.bot)):
            hashed_id = id_obfuscater.encrypt(member.id)
            if (hashed_id in inserted_user_id):
                # Check if we have already inserted a record belonging to this user into all_member_data
                # This means that the user is in multiple servers

                for index in range(0, len(all_member_data)):
                    if all_member_data[index][sqlite_handler.HASHED_ID_INDEX] == hashed_id:
                        # Found it, update guild_hash_list
                        guild_hash_list = astEVAL(all_member_data[index][sqlite_handler.GUILD_HASH_LIST_INDEX])
                        if hash(member.guild) not in guild_hash_list:
                            guild_hash_list.append(hash(member.guild))
                            all_member_data[index] = tuple([item if index != sqlite_handler.GUILD_HASH_LIST_INDEX 
                                                            else str(guild_hash_list) for index, item in enumerate(all_member_data[index])])
                        # Double check if the user is online in a different server
                        if (member.name not in online_server[member.guild] and str(member.status) != "offline"):
                            online_server[member.guild].append(member.name)
                        break
            else:
                inserted_user_id.add(hashed_id)
                unordered_data = {"HASHED_ID":hashed_id, "STATUS":str(member.status), 
                                    "TIMEZONE":sqlite_handler.fetch_timezone(hashed_id)}
                old_hashlist = sqlite_handler.fetch_guild_hashes(hashed_id, hash(member.guild))
                old_schedule = sqlite_handler.fetch_schedule(hashed_id, now.day, old_hashlist)

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

    # if there isn't any data, don't update the sql file
    # nor average out the frequency graph
    if (all_member_data):
        sqlite_handler.insert_update(all_member_data)
        sqlite_handler.average_freq_graph()

    temp_online_message = ""

    if not bool(online_server):
        temp_online_message = "Nobody was online in any server.\n"
    else:
        for guild, member_list in online_server.items():
            temp_online_message += f"|| {str(guild)} server:\n"
            
            aLotOfUsersAreOnline = len(member_list) > USERNAMES_DISPLAYED_IN_SERVER_LIMIT
            if aLotOfUsersAreOnline:
                member_list = member_list[:50] # grab 50 users from the entire list, in alphabetical order
            online_people = (", ".join(member_list)).rstrip(", ")
            if online_people.find(",") != -1:
                if aLotOfUsersAreOnline:
                    temp_online_message += f"{online_people} and many others were online.\n\n"
                else:
                    temp_online_message += f"{online_people} were online.\n\n"
            elif online_people != "":
                temp_online_message += f"{online_people} was online.\n\n"
            else:
                temp_online_message += "Nobody was online in this server.\n\n"
    
    online_message = temp_online_message


if __name__ == "__main__":
    try:
        global activityBot
        activityBot = Bot()
        activityBot.run(VERSION)

    except (KeyboardInterrupt, SystemExit):
        exit(0)

    except Exception as e:
        # Write an error message
        if osPATH.exists(ERROR_LOG_FILE):
            error_log = open("error.txt","a")
        else:
            error_log = open("error.txt","w")
        now = DateTime.now(CURRENT_TZ)
        error_log.write("___________ERROR_CAUGHT_______________\n")
        error_log.write(f"Error message logged on {now.hour:02}:{now.minute:02}:{now.second:02} at {now.month}/{now.day:02}/{now.year} ({secretTextfile.PREFERRED_TIMEZONE} format)\n")
        error_log.write("{}\n".format(e))
        error_log.close()

    finally:  
        if activityBot.scheduler.running:
            activityBot.scheduler.remove_all_jobs()
            activityBot.scheduler.shutdown()

        # clean the images associated with any commands
        graph_producer.clear_graph_folder() 