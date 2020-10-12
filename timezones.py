from datetime import datetime as DateTime
from pytz import timezone as pytzTIMEZONE, common_timezones_set, utc as pytzUTC

valid_timezones = common_timezones_set
mainTimeZonesClean = {item.split("/",1)[0] for item in common_timezones_set}
universalTimeZoneFormatted = (", ".join([item for item in common_timezones_set if item.find("/") == -1])).rstrip(", ")
continentsFormatted = (", ".join(sorted(list({item.split("/",1)[0] for item in common_timezones_set if item.find("/") != -1})))).rstrip(", ")

# This file works with the datetime and pytz library, both libraries
# dealing with time and timezones