import sqlite3

sql_filename = "data"
sql_filenameFULL = sql_filename+".sqlite"
data_fields = [("NAME","TEXT DEFAULT none"), ("NICKNAME","TEXT DEFAULT none"), 
    ("ID","INT PRIMARY KEY DEFAULT -1"), ("GUILD_ID","INT DEFAULT -1"), 
    ("STATUS","TEXT DEFAULT none"), ("SCHEDULE","TEXT DEFAULT none")]
#big_struct = [] # This will store + update all of the user info while the bot is still active
#online_freq = {} # This will store the frequency/amount of people who are online at certain hours in a week.

db = sqlite3.connect(sql_filenameFULL)
cursor = db.cursor()

# Setup the table if it already doesn't exists.
cursor.execute(f"CREATE TABLE IF NOT EXISTS {sql_filename}("
    + ", ".join(tup[0]+" "+tup[1] for tup in data_fields) + ")")
print("Create sql file check done.")

# Close cursor and db
db.commit()
cursor.close()
db.close()
db, cursor = None, None

# This will eventually replace the csvfile_reader.

def insert_update(lista: list) -> None:
    if not lista:
        # Empty, raise error.
        raise ValueError("Function sqlite_handler.insert_update(lista: list) should have a nonempty list as an argument")
    db = sqlite3.connect(sql_filenameFULL)
    cursor = db.cursor()
    questions = (", ".join(["?" for _ in data_fields])).rstrip(", ") # generate the ?, ?, ?, ?
    cursor.executemany(f"INSERT OR REPLACE INTO {sql_filename} VALUES ({questions})", lista) # "upserting" = insert OR update, look it up.
    db.commit()
    db.close()


def order_dict(unordered_dict: dict) -> list:
    ''' Return a list of values (in the same order as the columns) given a dict of values '''
    return [unordered_dict[field[0]] if field[0] in unordered_dict.keys() else (-1 if field[1].split(' ',1)[0] == "INT" else "none") for field in data_fields]