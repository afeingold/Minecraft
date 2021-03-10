import datetime
from important_timestamps import important_timestamps


print(important_timestamps[1][0])

print(datetime.datetime.strptime(important_timestamps[1][0], "%H:%M:%S").replace(year = 1950))