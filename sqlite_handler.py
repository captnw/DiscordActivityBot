from ast import literal_eval as astEVAL
from sqlite3 import connect as sqlite3CONNECT

# This file handles the storing and moving of schedule data between the data.sqlite file and the bot

sql_filename = "data"
sql_filenameFULL = sql_filename+".sqlite"
data_fields = [("NAME","TEXT DEFAULT None"), ("NICKNAME","TEXT DEFAULT None"), 
    ("ID","INT PRIMARY KEY DEFAULT -1"), ("GUILD_HASH","INT DEFAULT -1"), 
    ("STATUS","TEXT DEFAULT None"), ("SCHEDULE","TEXT DEFAULT None")]

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


def insert_update(lista: list) -> None:
    ''' Updates the .sqlite file '''
    if not lista:
        # Empty, raise error.
        raise ValueError("Function sqlite_handler.insert_update(lista: list) should have a nonempty list as an argument")
    db = sqlite3CONNECT(sql_filenameFULL)
    cursor = db.cursor()
    questions = (", ".join(["?" for _ in data_fields])).rstrip(", ") # generate the ?, ?, ?, ?
    cursor.executemany(f"INSERT OR REPLACE INTO {sql_filename} VALUES ({questions})", lista) # "upserting" = insert OR update, look it up.
    cursor.close()
    db.commit()
    db.close()


def fetch_schedule(member_id: int, guild_hash: str, current_day: int) -> list:
    ''' Return someone's 24 hour activity (for n days, up to 10 days) which is denoted by a list of boolean values (true/false means
        active for the hour at the index+1th hour). Otherwise returns a list of size 24 all set to false'''
    db = sqlite3CONNECT(sql_filenameFULL)
    cursor = db.cursor()
    cursor.execute(f"SELECT SCHEDULE FROM {sql_filename} WHERE ID=?",(member_id,))
    sched = cursor.fetchone()[0]
    cursor.close()
    db.close()

    if not guild_hash in online_freq:
        # Create the freq graph for the server if it didn't already exist
        online_freq[guild_hash] = {"DAYS":1, "FREQ":[0 for _ in range(24)]}

    if sched and sched != "none": 
        sched = astEVAL(sched)

        # Since we already have access to a member's schedule, traverse through schedule 
        # and add the hours online to server freq graph
        

        return sched
    else: 
        return [{current_day:[0 for _ in range(24)]}]


def order_dict(unordered_dict: dict) -> list:
    ''' Return a list of values (in the same order as the columns) given a dict of values '''
    return [unordered_dict[field[0]] if field[0] in unordered_dict.keys() else (-1 if field[1].split(' ',1)[0] == "INT" else "none") for field in data_fields]