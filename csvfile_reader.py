import os.path
from os import path
import csv

filename = "private_data.csv"
fields = ["name", "status"]

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
            for row in reader:
                if row["name"] == "name" or row["status"] == "status": 
                    # Do not copy the header into big_struct (avoid duplication)
                    continue
                big_struct.append({"name": row["name"], "status": row["status"]})
   

def csv_shutdown() -> None:
    ''' Gets all of the info in big_struct and then override/append it into private_data.csv '''
    # Note that opening the file in "w+" mode will wipe the .csv file clean
    with open(filename, "w+", newline='') as csv_file_wr:
        # Sort the list of dictionaries by name ...
        global big_struct
        big_struct = sorted(big_struct, key = lambda dicta : dicta["name"])

        # Then write the new stuff in the .csv file
        writer = csv.DictWriter(csv_file_wr, fieldnames= fields)
        writer.writeheader()
        for dicta in big_struct:
            #print(dicta) # DEBUG PRINT
            writer.writerow(dicta)


def csv_write_into(lista : list) -> None:
    ''' Modifies / adds a new entry to big_struct '''
    name, status = lista[0],lista[1]
    nameExist = False

    for dicta in big_struct:
        if dicta["name"] == name:
            # Name already exists, so just modify the status and other information
            dicta["status"] = status
            nameExist = True

    if not nameExist:
        # Name doesn't exist, so we have to add it to our big_struct
        big_struct.append({"name": name, "status": status})


def csv_clear() -> bool:
    ''' The big boy function that removes/clears the data in the .csv 
        Global variable "clear_safety" must be set to False before
        this function can clear the .csv. Returns whether the .csv
        has been successfully cleared or not. '''
    if clear_safety == False:
        f = open(filename, 'r+')
        f.truncate(0) # need '0' when using r+
        f.seek(0,0) # return back to start of file
    return not clear_safety


# Commands should probably go along this order (as seen below)
#if __name__ == "__main__":
    #csv_bootup()
    #csv_write_into(['phat','online'])
    #csv_write_into(['captnw', 'dnd'])
    #csv_write_into(['phat', 'stupid'])
    #csv_write_into(["james's dog", "name is forgotten"])
    #csv_shutdown()


