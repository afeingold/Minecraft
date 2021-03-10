import sys

map_data = []
with open(sys.argv[1]) as file:
    line = file.readline().split(",")
    x_off = int(line[0])
    z_off = int(line[1])
    line = file.readline()
    while line:
        if line == None:
            break
        map_data.append(line.strip("\n").split(","))
        line = file.readline()


rooms = []

for line in map_data:
	for room in line:
		if room[0] == 'r' and room not in rooms:
			rooms.append(room)

print("List of rooms: " + str(rooms))
print(len(rooms))