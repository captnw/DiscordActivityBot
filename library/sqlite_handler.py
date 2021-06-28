from ast import literal_eval as astEVAL
from sqlite3 import connect as sqlite3CONNECT
# This file handles the storing and moving of schedule data between the data.sqlite file and the bot

sql_filename = "data"
sql_filenameFULL = sql_filename+".sqlite"

data_fields = [("HASHED_ID","TEXT PRIMARY KEY DEFAULT None"), ("GUILD_HASH_LIST","TEXT DEFAULT None"), 
    ("STATUS","TEXT DEFAULT None"), ("TIMEZONE", "TEXT DEFAULT UTC"), ("SCHEDULE","TEXT DEFAULT None")]
HASHED_ID_INDEX = 0
GUILD_HASH_LIST_INDEX = 1

online_freq = {} # This will store the frequency/amount of people who are online in any server at certain hours in a week.
                 # Key: guild hash str, Value: a dict with keyval pair DAYS str:int and keyval pair FREQ str:[int (size 24)]
## This code segment below runs when imported  ##

db = sqlite3CONNECT(sql_filenameFULL)
cursor = db.cursor()
# Setup the table if it already doesn't exists.
cursor.execute(f"CREATE TABLE IF NOT EXISTS {sql_filename}("
    + ", ".join(tup[0]+" "+tup[1] for tup in data_fields) + ")")
print("\nCreate sql file check done.")

# Close cursor and db
db.commit()
cursor.close()
db.close()
db, cursor = None, None

## Code segment ends ##

def average_freq_graph() -> None:
    ''' Average out the freq graph ata according to the amount of days recorded so far '''
    for guild_hash in online_freq:
        num_days = int(online_freq[guild_hash]["DAYS"])
        if (num_days >= 2):
            online_freq[guild_hash]["FREQ"] = [round(num/num_days) for num in online_freq[guild_hash]["FREQ"]]


def fetch_guild_hashes(member_id: str, current_guild_id: int) -> list:
    ''' Return the guild_hashes for the guilds that the user belongs to '''
    db = sqlite3CONNECT(sql_filenameFULL)
    cursor = db.cursor()
    cursor.execute(f"SELECT GUILD_HASH_LIST FROM {sql_filename} WHERE HASHED_ID=?",(member_id,))
    guild_hashlist = cursor.fetchone()
    cursor.close()
    db.close()
    if guild_hashlist and guild_hashlist != "None":
        guild_hashlist = astEVAL(guild_hashlist[0])
        if (current_guild_id not in guild_hashlist):
            guild_hashlist.append(current_guild_id)
        return guild_hashlist
    else: 
        return list((current_guild_id,))


def fetch_schedule(member_id: str, current_day: int, guild_hash_list: list = []) -> list:
    ''' Return someone's 24 hour activity (for n days, up to 10 days) which is denoted by a list of boolean values (true/false means
        active for the hour at the index+1th hour). Otherwise returns a list of size 24 all set to false'''
    db = sqlite3CONNECT(sql_filenameFULL)
    cursor = db.cursor()
    cursor.execute(f"SELECT SCHEDULE FROM {sql_filename} WHERE HASHED_ID=?",(member_id,))
    sched = cursor.fetchone()
    cursor.close()
    db.close()

    if sched and sched != "None": 
        sched = astEVAL(sched[0])

    ## This portion of the function updates the freq graph if graph_hash_list is nonempty ##
    # Since we already have access to a member's schedule, traverse through schedule 
    # and add the hours online to server freq graph
    for guild_hash in guild_hash_list:
        # A user may be in multiple servers.

        if not guild_hash in online_freq:
            # Create the freq graph for the server if it didn't already exist
            online_freq[guild_hash] = {"DAYS":1, "FREQ":[0 for _ in range(24)]}

        if sched and sched != "None": 
            # Update days as it get larger, but constrain it to 7 days.
            online_freq[guild_hash]["DAYS"] = min(max(online_freq[guild_hash]["DAYS"], len(sched)), 7) 

            for numdicto, dicto in enumerate(sched, start=1):
                if numdicto <= 7:
                    # only count data up to the previous 7th day
                    online_hours = list(dicto.values())[0]
                    for hr, isOnline in enumerate(online_hours):
                        if isOnline != 0:
                            online_freq[guild_hash]["FREQ"][hr] += 1
                else: break
    ## End freq graph portion ##

    # Return values
    if sched and sched != "None": 
        return sched
    else: 
        return [{current_day:[0 for _ in range(24)]}]


def fetch_timezone(member_id: str) -> str:
    ''' Return someone's timezone (default UTC) '''
    db = sqlite3CONNECT(sql_filenameFULL)
    cursor = db.cursor()
    cursor.execute(f"SELECT TIMEZONE FROM {sql_filename} WHERE HASHED_ID=?",(member_id,))
    return_tzone = cursor.fetchone()
    cursor.close()
    db.close()
    if return_tzone: return return_tzone[0]
    else: return "UTC"
    

def insert_update(lista: list) -> None:
    ''' Updates the .sqlite file with multiple new entries/old changed entries '''
    if not lista:
        # Empty, raise error.
        raise ValueError("Function sqlite_handler.insert_update(lista: list) should have a nonempty list as an argument")
    db = sqlite3CONNECT(sql_filenameFULL)
    cursor = db.cursor()
    cursor.execute(f"DELETE FROM {sql_filename}") # clear table, removing people that had left servers
    questions = (", ".join(["?" for _ in data_fields])).rstrip(", ") # generate the ?, ?, ?, ?
    fields = (", ".join([field[0] for field in data_fields])).rstrip(", ") # generate the fields
    cursor.executemany(f"INSERT OR REPLACE INTO {sql_filename} ({fields}) VALUES ({questions})", lista) # "upserting" = insert OR update, look it up.
    cursor.close()
    db.commit()
    db.close()


def order_dict(unordered_dict: dict) -> list:
    ''' Return a list of values (in the same order as the columns) given a dict of values '''
    return [unordered_dict[field[0]] if field[0] in unordered_dict.keys() else 
        (field[1].rsplit(" ",1)[-1] if field[1].split(" ",1)[0] != "INT" else int(field[1].rsplit(" ",1)[-1]))
        for field in data_fields]


def replace_timezone(member_id: str, tzone: str):
    ''' Updates the .sqlite file with a new, valid timezone for a particular user '''
    db = sqlite3CONNECT(sql_filenameFULL)
    cursor = db.cursor()
    print(member_id)
    cursor.execute(f"UPDATE {sql_filename} SET TIMEZONE = ? WHERE HASHED_ID = ?",(tzone,member_id))
    cursor.close()
    db.commit()
    db.close()


def reset_freq_graph():
    ''' Reset all values in each server freq graph to 0 '''
    for guild_hash in online_freq:
        online_freq[guild_hash]["FREQ"] = [0 for _ in range(24)]