from collections import deque
from datetime import datetime as DateTime
from pytz import timezone as pytzTIMEZONE, common_timezones_set

# Timezone variables
valid_timezones = common_timezones_set
mainTimeZonesClean = {item.split("/",1)[0] for item in common_timezones_set}
universalTimeZoneFormatted = (", ".join([item for item in common_timezones_set if item.find("/") == -1])).rstrip(", ")
continentsFormatted = (", ".join(sorted(list({item.split("/",1)[0] for item in common_timezones_set if item.find("/") != -1})))).rstrip(", ")

# This file works with the datetime and pytz library, both libraries
# dealing with time and timezones

#pacific_now = DateTime.now(pytzTIMEZONE('US/Pacific'))
#print(int(pacific_now.utcoffset().total_seconds()/3600))


def chunks(lst, n):
    ''' Yield successive n-sized chunks from lst.
        Source: Ned Batchelder from https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks '''
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def adjust_server_frequency_timezone(freq_graph: list, tz: str) -> list:
    ''' Given that a server's frequency graph is in UTC format, adjust the frequency graph
        (by shifting the hours online) by the utc offset of a timezone '''
    if tz == "UTC" or tz == "GMT": 
        # timezone offset of 0, just return
        return freq_graph
    utc_offset = int(DateTime.now(pytzTIMEZONE(tz)).utcoffset().total_seconds()/3600)

    # put graph into dequeue and shift it by utc_offset
    times = deque(freq_graph)
    times.rotate(utc_offset)

    # convert dequeue back to list
    if utc_offset <= 0:
        # if negative shift, zero out the last Nth elements from the array
        times = list(times) 
        for ind in range(len(times)-1-utc_offset,len(times)-1):
            times[ind] = 0
    else:
        # If positive shift, zero out the 1st Nth elements 
        # (assuming we have shifted Nth) from the array,
        times = list(times)
        for ind in range(0, utc_offset):
            times[ind] = 0
    
    # return adjusted list
    return times


def adjust_schedule_timezone(schedule: list, tz: str) -> list:
    ''' Given that a schedule is in UTC format, adjust the schedule (by shifting the hours online) 
        by the utc offset of a timezone '''
    if tz == "UTC" or tz == "GMT": 
        # timezone offset of 0, just return
        return schedule
    utc_offset = int(DateTime.now(pytzTIMEZONE(tz)).utcoffset().total_seconds()/3600)
    
    # break schedule up into days and times
    days = [day for dicto in schedule for day in dicto]
    times = [t for dicto in schedule for time in dicto.values() for t in time]

    # put times into dequeue and shift it by utc_offset
    times = deque(times)
    times.rotate(utc_offset)

    # convert dequeue back to list
    if utc_offset <= 0:
        # if negative shift, zero out the last Nth elements from the array
        times = list(times) 
        for ind in range(len(times)-1-utc_offset,len(times)-1):
            times[ind] = 0
    else:
        # If positive shift, zero out the 1st Nth elements 
        # (assuming we have shifted Nth) from the array,
        times = list(times)
        for ind in range(0, utc_offset):
            times[ind] = 0
    
    # chunk up big list into smaller lists of size 24 (1AM-12AM)
    times = [chunk for chunk in chunks(times, 24)]

    # return the reconstructed datastructure
    return [{day:time} for day, time in zip(days, times)]