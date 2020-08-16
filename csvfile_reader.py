import csv, ast
import os.path
from os import path

filename = "private_data.csv"
fields = ["_NAME", "_NICKNAME", "_ID", "_STATUS", "_SCHEDULE"]

clear_safety = True # You're going to have to manually set this to false before calling the clear() function
big_struct = [] # This will store + update all of the user info while the bot is still active


# Note to anyone reading this
# Instead of updating the .csv constantly, we would just read from .csv 
# and maintain a list of dictionaries which would be updated
# then when the bot shut down ... just update the .csv


def csv_bootup() -> None:
    ''' Parses the current .csv and stores info into big_struct. This should only be called once at the beginning.
        If the file doesn't exist, this will not create a new file. '''
    if path.exists(filename):
        with open(filename, "r") as csv_file_rd:
            reader = csv.DictReader(csv_file_rd, fieldnames= fields)
            known_ids = set()
            for row in reader:
                #print(f"{row.values()}")
                user_id = row["_ID"]
                if "_NAME" in row.values() or user_id in known_ids:
                    # Do not copy the header into big_struct or any duplicate data belonging to the same id
                    continue
                big_struct.append({field : (row[field] if field in row.keys() else "_NODATA") for field in fields})
                known_ids.add(user_id)
   

def csv_shutdown() -> None:
    ''' Gets all of the info in big_struct and then override/append it into private_data.csv '''
    # Note that opening the file in "w+" mode will wipe the .csv file clean
    with open(filename, "w+", newline='') as csv_file_wr:
        # Sort the list of dictionaries by name ...
        global big_struct
        big_struct = sorted(big_struct, key = lambda dicta : dicta["_NAME"].split("#")[0].lower())

        # Then write the new stuff in the .csv file
        writer = csv.DictWriter(csv_file_wr, fieldnames= fields)
        writer.writeheader()
        known_ids = set()

        for dicta in big_struct:
            user_id = dicta["_ID"]
            if user_id in known_ids: 
                # Ignore duplicate IDs
                continue
            writer.writerow(dicta)
            known_ids.add(user_id)


def csv_write_into(lista : list) -> None:
    ''' Modifies / adds a new entry to big_struct '''
    givenInfo = [lista[fieldnum] if fieldnum < len(lista) else "_NODATA" for fieldnum in range(len(fields))]
    nameExist = False

    for dicta in big_struct:
        if dicta["_ID"] == givenInfo[2]:
            # ID already exists, so just modify the status and other information
            for fieldnum in range(0,len(fields)):
                if fieldnum == 2: continue # _ID, just continue
                fieldname = fields[fieldnum]
                dicta[fieldname] = givenInfo[fieldnum] if fieldnum < len(givenInfo) else "_NODATA"
            nameExist = True

    if not nameExist:
        # Name doesn't exist, so we have to add it to our big_struct
        big_struct.append({fields[fieldnum] : (lista[fieldnum] if fieldnum < len(lista) else "_NODATA") for fieldnum in range(len(fields))})


def csv_clear() -> bool:
    ''' The big boy function that removes/clears the data in the .csv 
        Global variable "clear_safety" must be set to False before
        this function can clear the .csv. Returns whether the .csv
        has been successfully cleared or not. '''
    if clear_safety == False:
        print("CLEAR SAFETY IS OFF, CLEARING CVS FILE ...")
        f = open(filename, 'r+')
        f.truncate(0) # need '0' when using r+
        f.seek(0,0) # return back to start of file
        f.close()
        print("CVS FILE HAS BEEN CLEARED.")
    return not clear_safety


def csv_lookup_schedule(id, current_day) -> list:
    ''' Return someone's 24 hour activity which is denoted by a list of boolean values (true/false means
        active for the hour at the index+1th hour). Otherwise returns a list of size 24 all set to false'''
    for dicta in big_struct:
        if dicta["_ID"] == id:
            large_struct = ast.literal_eval(dicta["_SCHEDULE"])
            #print("Name: {}, Data: {}".format(dicta["_NAME"],large_struct))
            return large_struct
    return [{current_day : [0 for num in range(24)]}]