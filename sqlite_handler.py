import sqlite3
from apscheduler.triggers.cron import CronTrigger

sql_filename = "data"
sql_filenameFULL = sql_filename+".sqlite"
data_fields = [("NAME","TEXT DEFAULT none"), ("NICKNAME","TEXT DEFAULT none"), 
    ("ID","INT PRIMARY KEY DEFAULT -1"), ("GUILD_ID","INT DEFAULT -1"), 
    ("STATUS","TEXT DEFAULT none"), ("SCHEDULE","TEXT DEFAULT none")]

big_struct = [] # This will store + update all of the user info while the bot is still active
online_freq = {} # This will store the frequency/amount of people who are online at certain hours in a week.


db = sqlite3.connect(sql_filenameFULL)
cursor = db.cursor()

# Setup the table if it already doesn't exists.
cursor.execute(f"CREATE TABLE IF NOT EXISTS {sql_filename}("
    + ", ".join(tup[0]+" "+tup[1] for tup in data_fields) + ")")

# THIS FILE IS A MESS :(
# This will eventually replace the csvfile_reader.

#def commit():

#def print_hey():
#    print("HELLO!")


#def test_print(sched):
#	sched.add_job(print_hey, CronTrigger(second=0))