import matplotlib.pyplot as plt


def activity_converter(hour : list, day : int) -> list:
    return [day if time == True else 0 for time in hour]

def int_to_str(int_list : list) -> list:
    return [str(item) if item != 0 else str(0) for item in int_list]

def produce_graph(data: list, id: str) -> None:
    for day in range(len(data)):
        day_legend = list(data[day].keys())[0] 
        bool_activity_list = list(data[day].values())[0]
        activity_list = activity_converter(bool_activity_list, int(day_legend))
        plt.scatter(hour_x, int_to_str(activity_list))
    plt.savefig(f"./graph_folder/{id}.png")
    plt.show()

plt.style.use('seaborn')
zero_list = [0 for zero in range(24)]
hour_x = [num for num in range(1, 25)]
print(zero_list, hour_x)
#plt.scatter(hour_x, int_to_str(zero_list))

plt.title("Active Hours on discord")
plt.xlabel("Hours Online")
plt.ylabel("Day")
plt.xticks(hour_x)
