import os
import sys

#participants 3, 5, 11, 35 have weird json files and so are not parsed.

participants = [1,2,4,7,9,12,13,14,16,17,18,19,20,21,22,24,25,26,27,28,29,32,33,36,37,38,39,40,41,42,43,44,45,46,47,48,50,51,52]


active_time = {}

for p in participants:
	v4_filepath = f"parser_output/participant{p}_parser-v4_output.txt"
	v5_filepath = f"parser_output/participant{p}_parser-v5_output.txt"
	active_time[p] = {}
	with open(v4_filepath) as v4file:
		v4file.readline()
		active_time[p]['v4active'] = v4file.readline().strip('\n').split(' ')[5]
		active_time[p]['v4inactive'] = v4file.readline().strip('\n').split(' ')[5]
	with open(v5_filepath) as v5file:
		v5file.readline()
		active_time[p]['v5active'] = v5file.readline().strip('\n').split(' ')[5]
		active_time[p]['v5inactive'] = v5file.readline().strip('\n').split(' ')[5]

#print(active_time)

#for p in active_time.values():
#	print(int(p['v4active']) - int(p['v5active']))

#largest difference in active count is 27, for participant 2


print("participant, portion_active")
for p in active_time.items():
	prop = round(int(p[1]['v5active']) / (int(p[1]['v5active']) + int(p[1]['v5inactive'])), 2)
	print(f"{p[0]}, {prop}")


'''for p in active_time.items():
	secs = int(p[1]['v5active']) + int(p[1]['v5inactive'])
	print(f"Total seconds in game (not including CROs) for participant {str(p[0])}: {str(secs)}")
'''
