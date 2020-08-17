import matplotlib.pyplot as plt


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

def produce_graph(data: list, id: str, name: str) -> None:
    '''Given a list, id, and name it outputs a png that
       displays their hours online O(10)*O(1)'''

    cat_time = ['12AM','1AM','2AM','3AM','4AM','5AM','6AM','7AM','8AM','9AM','10AM','11AM','12PM',
                '1PM','2PM','3PM','4PM','5PM','6PM','7PM','8PM','9PM','10PM','11PM']
    zero_list = [0 for zero in range(24)]
    hour_x = int_to_str([24,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23])

    plt.style.use('seaborn')
    plt.scatter(hour_x, int_to_str(zero_list))
    plt.title(f"{name}'s Active Hours on Discord")
    plt.xlabel(" Hours Online")
    plt.ylabel("Day")
    plt.xticks(hour_x, cat_time, size=6.5)

    for day in range(len(data)):
        day_legend = list((data[day].keys()))[0] 
        bool_activity_list = (list(data[day].values()))[0]
        activity_list = activity_converter(bool_activity_list, int(day_legend))
        plt.scatter(hour_x, move_last(int_to_str(activity_list)))

    plt.scatter(hour_x, int_to_str(zero_list), color="white")
    plt.savefig(f"./graph_folder/{id}.png")
    plt.close()

