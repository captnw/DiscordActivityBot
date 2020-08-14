import matplotlib.pyplot as plt

plt.style.use('seaborn')
zeroList = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
boolList = [1,0,0,1,0,1,0,1,1,0,1,1,1,1,0,1,0,0,1,1,1,1,1,1]
hour_x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
struct = [{'29': boolList}, {'30': boolList}, {'31': boolList}, {'1': boolList}, {'2': boolList}]
plt.title("Active Hours on discord")
plt.xlabel("Hours Online")
plt.ylabel("Day")
plt.xticks(hour_x)
plt.scatter(hour_x, int_to_str(zeroList))

def activity_converter(hour : list, day : int) -> list:
    return [day if time == True else 0 for time in hour]

def int_to_str(intList : list) -> list:
    return [str(item) if item != 0 else str(0) for item in intList]

def produce_graph(data: list) -> None:
    for day in range(len(data)):
        day_legend = list(data[day].keys())[0] 
        bool_activity_list = list(data[day].values())[0]
        activity_list = activity_converter(bool_activity_list, int(day_legend))
        plt.scatter(hour_x, int_to_str(activity_list))

plt.show()
plt.savefig('./graph/plot.png')
