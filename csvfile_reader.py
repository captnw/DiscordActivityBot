import csv, ast, glob
import os.path
from os import path
from pathlib import Path

filename = "private_data.csv"
fields = ["_NAME", "_NICKNAME", "_ID", "_GUILD", "_STATUS", "_SCHEDULE"]

clear_safety = True # You're going to have to manually set this to false before calling the clear() function
big_struct = [] # This will store + update all of the user info while the bot is still active
online_freq = {} # This will store the frequency/amount of people who are online at certain hours in a week.


# Note about the .csv file to anyone reading this
# Instead of updating the .csv constantly, we would just read from .csv 
# and maintain a list of dictionaries which would be updated
# then when the bot shut down ... just update the .csv


def generate_label_instructions(main_labels : list, csv_labels : list) -> list:
    ''' Return a list of indices or the string "Skip" that gives insight in where to look
        if the labels are misaligned/missing.

        Example:
        Main_label = ['FirstName','LastName','NO','ID','Status','FavNum', 'MARIO']
        Csv_label = ['FirstName','LastName','ID','Status','FavNum']
        This function would return [0, 1, "Skip", 2, 3, 4, "Skip"]
    '''

    instruction_list = []

    if (main_labels != csv_labels):
        ind1, ind2 = 0,0
        # Find where the difference lies
        while (ind1 < len(main_labels)):
            #print("Ind1: ", ind1, " Ind2: ", ind2)
            main_label = None
            read_label = None
            if (ind1 < len(main_labels)): 
                main_label = main_labels[ind1]
               # print("main_labels: ", main_labels[ind1])
                
            if (ind2 < len(csv_labels)): 
                read_label = csv_labels[ind2]
                #print("csv_labels: ", read_label)

            if (main_label == read_label):
                instruction_list.append(ind2)
            else:
                temp_ind = 0; # Start searching from beginning of list
                while (temp_ind < len(csv_labels)):
                    if (main_label == csv_labels[temp_ind]):
                        instruction_list.append(temp_ind) # Found the label, it's in a different index
                        break
                    temp_ind = temp_ind + 1;
                else: 
                    instruction_list.append("Skip") # The label doesn't exist
                    
                # current label is already accounted for, move to next label
                ind1 = ind1+1 if ind1 < len(main_labels) else ind1
                continue

            ind1 = ind1+1 if ind1 < len(main_labels) else ind1
            ind2 = ind2+1 if ind2 < len(csv_labels) else ind2  
    else:
        instruction_list = [num for num in range(len(csv_labels))]

    return instruction_list


def csv_bootup() -> None:
    ''' Parses the current .csv and stores info into big_struct. This should only be called once at the beginning.
        If the file doesn't exist, this will not create a new file. '''
    if path.exists(filename):
        with open(filename, "r") as csv_file_rd:
            reader = csv.reader(csv_file_rd) # Using reader instead of dictreader allows us to utilize the indices (consider each input row as a list)
            known_ids = set()
            current_instructions = None
            for row in reader:
                current_data = {}
                user_id = row[fields.index("_ID")]
                if "_NAME" in row or user_id in known_ids:
                    # Do not copy the header into big_struct or any duplicate data belonging to the same id
                    if "_NAME" in row and "_SCHEDULE" in row:
                        # This is the label row for the .csv file, determine if the labels are aligned/misaligned
                        current_instructions = generate_label_instructions(fields, row)
                    continue
                
                for ind, val in enumerate(current_instructions):
                    if val == "Skip":
                        current_data[fields[ind]] = "_NODATA" # label doesn't exist
                    else:
                        current_data[fields[ind]] = row[val] # label is aligned/misaligned (depending on val)
                
                big_struct.append(current_data)
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
            if user_id in known_ids: continue # Ignore duplicate IDs
            writer.writerow(dicta)
            known_ids.add(user_id)

    clear_graph_folder() # Clear the image folder after we've finished writing to delete unnecessary data


def csv_write_into(lista : list) -> None:
    ''' Modifies / adds a new entry to big_struct '''
    nameExist = False
    ind_of_id = fields.index("_ID") # Added so that this function would readjust itself should the fields be arranged in a different order
    user_id = lista[ind_of_id]

    for dicta in big_struct:
        if dicta["_ID"] == str(user_id):
            # ID already exists, so just modify the status and other information
            for fieldnum in range(0,len(fields)):
                if fieldnum == ind_of_id: continue # Do not alter the _ID, just continue
                fieldname = fields[fieldnum]
                dicta[fieldname] = lista[fieldnum]
            nameExist = True

    if not nameExist:
        # Name doesn't exist, so we have to add it to our big_struct
        big_struct.append({fields[fieldnum] : lista[fieldnum] for fieldnum in range(len(fields))})


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
    ''' Return someone's 24 hour activity (for n days, up to 10 days) which is denoted by a list of boolean values (true/false means
        active for the hour at the index+1th hour). Otherwise returns a list of size 24 all set to false'''
    for dicta in big_struct:
        if dicta["_ID"] == str(id):
            online_history = ast.literal_eval(dicta["_SCHEDULE"])
            return online_history
    return [{current_day : [0 for num in range(24)]}]


def csv_all_schedule() -> list:
    ''' Updates the list in online_freq that represent how many people are online (on average) at each hour for the last 7 days in a specific server '''
    # note: we're not going to consider the other 3 days since the data would overrepresent those 3 days
    # and we would like an accurate representation of the frequency of online users during a "normal week"
    global online_freq

    # Count the number of people online at each hour.
    for dicta in big_struct:
        if not (dicta["_GUILD"] in online_freq):
            online_freq[dicta["_GUILD"]] = {"_DAYS":1, "_FREQ":[0 for num in range(24)]}

        online_history = ast.literal_eval(dicta["_SCHEDULE"])
        # Update days as it get larger, but constrain it to 7 days.
        online_freq[dicta["_GUILD"]]["_DAYS"] = min(max(online_freq[dicta["_GUILD"]]["_DAYS"], len(online_history)), 7) 

        for numdicto, dicto in enumerate(online_history, start=1):
            if numdicto <= 7:
                # only count data up to the previous 7th day
                online_hours = list(dicto.values())[0]
                for hr, isOnline in enumerate(online_hours):
                    if isOnline != 0:
                        online_freq[dicta["_GUILD"]]["_FREQ"][hr] += 1

    # Average out the data according to the amount of days recorded so far
    for guild_hash in online_freq:
        num_days = int(online_freq[guild_hash]["_DAYS"])
        online_freq[guild_hash]["_FREQ"] = [round(num/num_days) for num in online_freq[guild_hash]["_FREQ"]]


def csv_order_data(unordered_data : dict) -> list:
    ''' Given dict with keys as labels, return a list of just the data in the correct data as the main label, field. '''
    return [unordered_data[field] if field in unordered_data.keys() else "_NODATA" for field in fields]


def clear_graph_folder() -> None:
    ''' Deletes all files in the graph folder that ends with the .png extension '''
    current_directory = str(Path.cwd())
    graph_directory = "graph_folder/"

    os.chdir(graph_directory) # Change directory to graph_directory
    files = glob.glob("*.png") # find all files that end with .png
    for file_name in files:
        os.unlink(file_name) # Delete the files
    os.chdir(current_directory) # Change back to current directory
