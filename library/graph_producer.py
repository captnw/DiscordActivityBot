import matplotlib.pyplot as plt
from glob import glob as globGLOB
from os import chdir as osCHDIR, unlink as osUNLINK
from pathlib import Path

def activity_converter(hour : list, day : int) -> list:
    '''Given a list of bools and an int it will convert
       all True values in that list into the given int'''
    return [day if time == True else 0 for time in hour]


def int_to_str(int_list : list) -> list:
    '''Takes a list of ints and converts them into a list of stirngs'''
    return [str(item) if item != 0 else str(0) for item in int_list]


def move_last(int_list: list) -> list:
    '''Takes the last element and moves it to the front'''
    last = int_list[-1]
    int_list.pop(-1)
    int_list.insert(0, last)
    return int_list


def produce_user_graph(data: list, hashed_id: str, name: str, time_zone: str) -> None:
    '''Given a list, hashed_id, and name it outputs a png that
       displays their hours online O(10)*O(1)'''

    cat_time = ['12AM','1AM','2AM','3AM','4AM','5AM','6AM','7AM','8AM','9AM','10AM','11AM','12PM',
                '1PM','2PM','3PM','4PM','5PM','6PM','7PM','8PM','9PM','10PM','11PM']
    zero_list = [0 for zero in range(24)]
    hour_x = int_to_str([24,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23])

    plt.style.use('seaborn')
    plt.scatter(hour_x, int_to_str(zero_list))
    plt.title(f"{name}'s Active Hours on Discord")
    plt.xlabel(f"Hours (AM/PM) {time_zone} format")
    plt.ylabel("Day")
    plt.xticks(hour_x, cat_time, size=6.5)

    for day in range(len(data)):
        day_legend = list((data[day].keys()))[0] 
        bool_activity_list = (list(data[day].values()))[0]
        activity_list = activity_converter(bool_activity_list, int(day_legend))
        plt.scatter(hour_x, move_last(int_to_str(activity_list)))

    plt.scatter(hour_x, int_to_str(zero_list), color="white")
    plt.savefig(f"./graph_folder/UserAct_{hashed_id}.png")
    plt.close()


def produce_server_graph(data_hours: list, guild_name: str, guild_hash: str, days_recorded: int, time_zone: str) -> None:
    ''' Given a list of ints, makes a bar graph png that displays the cumulative hours of all users online '''
    data_hours = move_last(data_hours); # move the last data to the front of the list so that we start with 12 AM
    cat_time = ['12AM','1AM','2AM','3AM','4AM','5AM','6AM','7AM','8AM','9AM','10AM','11AM','12PM',
                '1PM','2PM','3PM','4PM','5PM','6PM','7PM','8PM','9PM','10PM','11PM']
    hour_x = int_to_str([24,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23])
    title_message = ""
    ylabel_message = ""

    if days_recorded == 1:
        title_message = guild_name + f" server activity for today"
        ylabel_message = "People online"
    else:
        title_message = guild_name + " server activity for the last " + str(days_recorded) + f" days"
        ylabel_message = "People online (on average)"

    plt.style.use('seaborn')
    plt.bar(hour_x, data_hours, align = "center")
    plt.title(title_message)
    plt.xlabel(f"Hours (AM/PM) {time_zone} format")
    plt.ylabel(ylabel_message)
    plt.xticks(hour_x, cat_time, size = 6.5)

    plt.savefig(f"./graph_folder/GuildAct_{guild_hash}.png")
    plt.close()


def clear_graph_folder() -> None:
    ''' Deletes all files in the graph folder that ends with the .png extension '''
    current_directory = str(Path.cwd())
    graph_directory = "graph_folder/"

    osCHDIR(graph_directory) # Change directory to graph_directory
    files = globGLOB("*.png") # find all files that end with .png
    for file_name in files:
        osUNLINK(file_name) # Delete the files
    osCHDIR(current_directory) # Change back to current directory