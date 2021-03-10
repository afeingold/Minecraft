import os
import sys

#participants 3, 5, 11, 35 have weird json files and so are not parsed.

participants = [1,2,4,7,9,12,13,14,16,17,18,19,20,21,22,24,25,26,27,28,29,32,33,36,37,38,39,40,41,42,43,44,45,46,47,48,50,51,52]


portion_rooms_visited = {}
num_room_revisits = {}
timeframes_in_room_revisits = {}
total_timeframes = {}

for p in participants:
    v4_filepath = f"parser_output/participant{p}_parser-v4_output.txt"
    v5_filepath = f"parser_output/participant{p}_parser-v5_output.txt"
    portion_rooms_visited[p] = -1
    num_room_revisits[p] = -1
    timeframes_in_room_revisits[p] = -1
    total_timeframes[p] = -1
    with open(v4_filepath) as v4file:
        for i in range(9):
            v4file.readline()
        portion_rooms_visited[p] = float(v4file.readline().strip('\n').split(' ')[-1].split('/')[0]) / 18
        num_room_revisits[p] = int(v4file.readline().strip('\n').split(' ')[3])
    with open(v5_filepath) as v5file:
        v5file.readline()
        total_timeframes[p] = int(v5file.readline().strip('\n').split(' ')[5])
        total_timeframes[p] += int(v5file.readline().strip('\n').split(' ')[5])
        v5file.readline()
        timeframes_in_room_revisits[p] = int(v5file.readline().strip('\n').split(' ')[-1])
        

#print(portion_rooms_visited)

#for p in portion_rooms_visited.values():
#   print(int(p['v4active']) - int(p['v5active']))

#largest difference in active count is 27, for participant 2






print("participant, portion_rooms_visited, num_room_revisits, portion_revisiting_rooms")
for p in participants:
    print(f"{p}, {portion_rooms_visited[p]}, {num_room_revisits[p]}, {timeframes_in_room_revisits[p]/total_timeframes[p]}")


'''for p in portion_rooms_visited.items():
    secs = int(p[1]['v5active']) + int(p[1]['v5inactive'])
    print(f"Total seconds in game (not including CROs) for participant {str(p[0])}: {str(secs)}")
'''
