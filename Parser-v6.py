import json
import os
import sys
import time
import math
import sched
from datetime import datetime, time
from operator import itemgetter, attrgetter
from important_timestamps import important_timestamps 

##################################
# End Imports
##################################


class room_visit:
    entry_time = None
    exit_time = None
    room_id = None
    entry_point = None
    exit_point = None
    next_room = None
    victim_encounters = []
    commander_report_outs = []
    duration = None

    def __init__(self, z, x, t, room):
        self.entry_time = t
        self.room_id = room
        self.entry_point = (z, x)
        victim_encounters = []


    def get_duration(self):
        return self.exit_time - self.entry_time


    def close(self, z, x, t,next_room):
        self.exit_point = (z, x)
        self.exit_time = t
        self.next_room = next_room
        self.duration = self.get_duration()
        self.entry_time = self.entry_time.strftime("%M:%S")
        self.exit_time = self.exit_time.strftime("%M:%S")

    def add_victim_encounter(self, enc):
        self.victim_encounters.append(enc)

    def __str__(self):
        s = f"Participant entered room {self.room_id} at time {self.entry_time}. \nList of Victim Encounters: \n"
        #for encounter in self.victim_encounters:
        #    s += f"{str(encounter)}\n"
        s += f"There were {len(self.victim_encounters)} victims encountered in this room.\n"
        s += f"Participant exited room {self.room_id} into room {self.next_room} at time {self.exit_time}.\nIn total, they spent {self.duration.seconds} seconds in that room.\n"
        return s


class victim_encounter:
    victim_x = 0
    victim_z = 0
    victim_type = None
    start_time = None
    end_time = None
    action_taken = None                 # Saved, Skipped, or Mission ended during encounter
    victim_room = None

    def __init__(self, x, z, type, t, room):
        self.victim_x = x
        self.victim_z = z
        self.victim_type = type
        self.start_time = t
        self.victim_room = room

    def __str__(self):
        if self.end_time is None:
            self.end_time = "N/A"
            self.action_taken = "Mission ended during encounter"
        return "Victim Encounter: " + self.victim_type + " victim at (x = " + str(self.victim_x) + ", z = " + str(self.victim_z) + ") in room " + self.victim_room + ". Encounter began at " + str(self.start_time) + ". Encounter ended at " + str(self.end_time) + ". Action taken: " + self.action_taken + "." 

    def close(self, t, action):
        if self.end_time is None:
            self.end_time = t
            self.action_taken = action



##################################
# End Sub Classes
##################################


# 2152 is the divider
class Parse:
    dataset = None                      # Json Data of messages
    map_data = []                       # CSV area data
    current_time = None                 # Current run time
    current_x = 0                       # Current location x
    current_z = 0                       # Current location z
    start_time = None                   # Start time of the run
    x_off = 0                           # X offset of map
    z_off = 0                           # Z offset of map
    events = []
    
    
    def inbounds(self, msg):
        zpos = int(math.floor(msg["ZPos"])) - self.z_off
        xpos = int(math.floor(msg["XPos"])) - self.x_off
        return self.in_bounds(xpos, zpos)
    
    def in_bounds(self, xpos, zpos):
        return len(self.map_data) > zpos and 0 <= zpos and len(self.map_data[0]) > xpos and 0 <= xpos
    
    def get_data(self, msg):
        return (str(self.current_time) + ", Position: (" + str(int(math.floor(self.current_x))) + ", " + str(int(math.floor(self.current_z))) +  ") Yaw & Pitch: (" + str(msg["Yaw"]) + ", " + str(msg["Pitch"])+")")
    

    def not_during_report_out(self):
        day0current_time = self.current_time.replace(year = 1900, month = 1, day = 1)
        return (day0current_time > self.impt_times[0] and day0current_time < self.impt_times[1]) or (day0current_time > self.impt_times[2] and day0current_time < self.impt_times[3]) or (day0current_time > self.impt_times[4] and day0current_time < self.impt_times[6]) or (day0current_time > self.impt_times[7] and day0current_time < self.impt_times[8]) or (day0current_time > self.impt_times[9] and day0current_time < self.impt_times[10])




    def get_current_room(self, msg):
        return self.map_data[int(math.floor(msg["ZPos"])) - self.z_off][int(math.floor(msg["XPos"])) - self.x_off]




    room_visits = []
    current_room_visit = None
    current_room = None                 # Space current in
    room_revisits = {}                  # Spaces visited
    def get_room_retrace(self, msg):
        if self.current_room is None:
            self.current_room = self.get_current_room(msg)
            self.current_room_visit = room_visit(int(math.floor(msg["ZPos"])) - self.z_off, int(math.floor(msg["XPos"])) - self.x_off, self.current_time, self.current_room)
            self.room_visits.append(self.current_room_visit)
            self.room_revisits[self.current_room] = 1
            return
        
        else:
            next_room = self.get_current_room(msg)
            if next_room != self.current_room:
                if (next_room == 'r208a' and self.current_room == 'r208c') or (next_room == 'r208c' and self.current_room == 'r208a') or (next_room == 'r216a' and self.current_room == 'r216c') or (next_room == 'r216c' and self.current_room == 'r216a'):
                    return
                if next_room not in self.room_revisits:
                    self.room_revisits[next_room] = 0

                if next_room[0] != 'd':
                    self.current_room_visit.close(int(math.floor(msg["ZPos"])) - self.z_off, int(math.floor(msg["XPos"])) - self.x_off, self.current_time, next_room)
                    self.current_room_visit = room_visit(int(math.floor(msg["ZPos"])) - self.z_off, int(math.floor(msg["XPos"])) - self.x_off, self.current_time, next_room)
                    self.room_visits.append(self.current_room_visit)
                    self.current_room = next_room
                    self.room_revisits[self.current_room] += 1
                    print(f"Visiting a room: {self.current_room} at time {self.current_time}.")
            else:
                return





    ####
    # Get Active Time Methods
    ####
    
    last_checked_time_x = 0             # x at last checked time
    last_checked_time_z = 0             # z at last checked time
    movement_range = 1                  # Distance player needs to move for 
    movement_time = 1000                # Milliseconds to determine if user has been inactive
    last_movement_check_time = None     # Timestamp of previous checked time
    active_times = 0
    inactive_times = 0
    def get_active_time(self, msg):
        if self.last_checked_time_x == 0 and self.last_checked_time_z == 0:
            self.last_checked_time_x = msg["XPos"]
            self.last_checked_time_z = msg["ZPos"]
            self.last_movement_check_time = self.current_time
            return
        
        #if movement_time has passed since previous checked time
        delta_time = (self.current_time - self.last_movement_check_time)
        if (delta_time.seconds * 1000 + (delta_time.microseconds/1000)) > self.movement_time:
            
            #Check if the user has been active in the last timeframe
            distance = math.sqrt(((self.last_checked_time_x - msg["XPos"])**2)+((self.last_checked_time_z - msg["ZPos"])**2))

            #Update references to last observation
            self.last_movement_check_time = self.current_time
            self.last_checked_time_x = msg["XPos"]
            self.last_checked_time_z = msg["ZPos"]
        
            if distance >= self.movement_range:
                self.active_times += 1
            else:
                self.inactive_times += 1




    ####
    # Victim Saving Methods
    ####

    encounters = {}                     # Dict of all victim encounters, indexed by hash of location
    current_encounters = {}             # Dict of victim encounters not yet completed
    vic_dict = {}
    green_saves = 0
    yellow_saves = 0



    def victim_knowledge(self, msg):
        factor = int(math.sqrt(len(msg["ground_truth"])))  #7, for the 7x7 ground truth square
        offset = int(factor/2)
        cur_z = int(math.floor(self.current_z))
        cur_x = int(math.floor(self.current_x))


        # Close any encounters that have ended in skipping
        encounters_skipped = []
        for enc in self.current_encounters.items():
            if enc[1].victim_x < cur_x - offset or enc[1].victim_x > cur_x + ((factor - 1) - offset) or enc[1].victim_z < cur_z - offset or enc[1].victim_z > cur_z + ((factor - 1) - offset):
                enc[1].close(self.current_time, "Skipped")
                self.encounters[enc[0]] = enc[1]
                encounters_skipped.append(enc[0])
                print("Skipped victim.")

        for enc in encounters_skipped:
            del self.current_encounters[enc]



        for z in range(factor):
            for x in range(factor):
                x_loc = cur_x + (x - offset) - self.x_off
                z_loc = cur_z + (z - offset) - self.z_off
                if self.in_bounds(x_loc, z_loc):
                    hsh = hash(str(z_loc) + " $$ " + str(x_loc))
                    dist = math.sqrt(((cur_x - self.x_off - x_loc)**2)+((cur_z - self.z_off - z_loc)**2))

                    
                    if offset + 3 >= z and offset - 3 <= z and offset + 3 >= x and offset - 3 <= x:
                        if "prismarine" in msg["ground_truth"][z * factor + x] and hsh not in self.current_encounters:
                            
                            victim_room = self.map_data[int(math.floor(z_loc))][int(math.floor(x_loc))]
                            if hsh not in self.vic_dict:
                                self.events.append("Green victim at (" + str(int(math.floor(x_loc + self.x_off))) + ", " + str(math.floor(z_loc + self.z_off)) + ") found in " + victim_room + " while participant in " + self.current_room + " at " + self.get_data(msg))
                                self.vic_dict[hsh] = "green_victim"
                            if victim_room[1:] == self.current_room[1:] or (victim_room in ["r208a","r208c"] and self.current_room in ["r208a","r208c"]) or (victim_room in ["r216a","r216c"] and self.current_room in ["r216a","r216c"]):
                                self.current_encounters[hsh] = victim_encounter(int(math.floor(x_loc + self.x_off)), int(math.floor(z_loc + self.z_off)), "Green", self.current_time, victim_room)
                                self.current_room_visit.add_victim_encounter(self.current_encounters[hsh])
                                print(f"Encountered GREEN victim in room {victim_room} at time {self.current_time}.")
                      
                        if "gold" in msg["ground_truth"][z * factor + x] and hsh not in self.current_encounters:
        
                            victim_room = self.map_data[int(math.floor(z_loc))][int(math.floor(x_loc))]
                            if hsh not in self.vic_dict:
                                self.events.append("Yellow victim at (" + str(int(math.floor(x_loc + self.x_off))) + ", " + str(math.floor(z_loc + self.z_off)) + ") found in " + victim_room + " at " + self.get_data(msg))
                                self.vic_dict[hsh] = "yellow_victim"
                            if victim_room[1:] == self.current_room[1:] or (victim_room in ["r208a","r208c"] and self.current_room in ["r208a","r208c"]) or (victim_room in ["r216a","r216c"] and self.current_room in ["r216a","r216c"]):
                                self.current_encounters[hsh] = victim_encounter(int(math.floor(x_loc + self.x_off)), int(math.floor(z_loc + self.z_off)), "Yellow", self.current_time, victim_room)
                                self.current_room_visit.add_victim_encounter(self.current_encounters[hsh])
                                print(f"Encountered GOLD victim in room {victim_room} at time {self.current_time}.")
                        
                            

                  
                    if "bone" in msg["ground_truth"][z * factor + x] and hsh in self.vic_dict:
                        if self.vic_dict[hsh] == "bone":
                            continue
                            
                        if self.vic_dict[hsh] == "yellow_victim":
                            self.vic_dict[hsh] = "bone"
                            self.events.append("Yellow Victim at (" + str(int(math.floor(x_loc + self.x_off))) + ", " + str(math.floor(z_loc + self.z_off)) + ") saved in " + self.current_room + " at " + self.get_data(msg))
                            self.yellow_saves += 1
                            if hsh not in self.current_encounters:
                                victim_room = self.map_data[int(math.floor(z_loc))][int(math.floor(x_loc))]
                                self.current_encounters[hsh] = victim_encounter(int(math.floor(x_loc + self.x_off)), int(math.floor(z_loc + self.z_off)), "Yellow", "ERROR", victim_room)
                            print("Saved victim")

                            
                        if self.vic_dict[hsh] == "green_victim":
                            self.vic_dict[hsh] = "bone"
                            self.events.append("Green Victim at (" + str(int(math.floor(x_loc + self.x_off))) + ", " + str(math.floor(z_loc + self.z_off)) + ") saved in " + self.current_room + " at " +  self.get_data(msg))
                            self.green_saves += 1
                            if hsh not in self.current_encounters:
                                victim_room = self.map_data[int(math.floor(z_loc))][int(math.floor(x_loc))]
                                self.current_encounters[hsh] = victim_encounter(int(math.floor(x_loc + self.x_off)), int(math.floor(z_loc + self.z_off)), "Green", "ERROR", victim_room)
                            print("Saved victim.")

                        self.current_encounters[hsh].close(self.current_time, "Saved")
                        self.encounters[hsh] = self.current_encounters[hsh]
                        del self.current_encounters[hsh]


    



    
    def get_num_room_retrace(self):
        num_room_revisits = 0           # Number of times participant re-entered a "room" space that they already entered
        for room in self.room_revisits:
            if room[0] == 'r':
                num_room_revisits += (self.room_revisits[room] - 1)
        return num_room_revisits


    
    def get_num_rooms_visited(self):
        num_rooms = 0                       # Number of "room" spaces visited
        for room in self.room_revisits:
            if room[0] == 'r':
                num_rooms += 1
        if 'r208a' in self.room_revisits and 'r208c' in self.room_revisits:
            num_rooms -= 1
        if 'r216a' in self.room_revisits and 'r216c' in self.room_revisits:
            num_rooms -= 1
        return num_rooms
    


    participant = None
    impt_times = []          
    def __init__(self, metadata_file, csv_file, p):
        try:
            self.participant = int(p)
        except: 
            print("Please enter the participant number as the third argument.")
            sys.exit()
        self.impt_times = important_timestamps[self.participant]
        for i in range(11):
            if self.impt_times[i] is None:
                self.impt_times[i] = "23:00:00"
            self.impt_times[i] = datetime.strptime(self.impt_times[i], "%H:%M:%S")


        with open(metadata_file) as json_file:
            self.dataset = json.load(json_file)

                
        with open(csv_file) as file:
            line = file.readline().split(",")
            self.x_off = int(line[0])
            self.z_off = int(line[1])
            line = file.readline()
            while line:
                if line == None:
                    break
                self.map_data.append(line.strip("\n").split(","))
                line = file.readline()


        self.start()

    num_skips = 0
    rooms = []
    def start(self):
        mission = False
        #Make a list of all of the rooms in Sparky
        for line in self.map_data:
            for room in line:
                if room[0] == 'r' and room not in self.rooms:
                    self.rooms.append(room)

        for i in range(0, len(self.dataset)):
            message = self.dataset[i]["message"]["data"]
            x = message["XPos"]
            z = message["ZPos"]
            if not mission and abs(x + 2166.5) < 1 and abs(z - 175.5) < 1:
                mission = True
            if not mission:
                continue
            if not self.inbounds(message):
                continue
            if self.start_time == None:
                self.start_time = datetime.strptime(message["timestamp"],"%Y-%m-%dT%H:%M:%S.%f")
            self.current_time = datetime.strptime(message["timestamp"],"%Y-%m-%dT%H:%M:%S.%f")
            self.current_x = message["XPos"]
            self.current_z = message["ZPos"]
            #if self.not_during_report_out():
            #    self.get_active_time(message)
            #self.get_retrace_amount()
            self.get_room_retrace(message)
            self.victim_knowledge(message)

        self.encounters.update(self.current_encounters)
        self.current_room_visit.close(int(math.floor(message["ZPos"])) - self.z_off, int(math.floor(message["XPos"])) - self.x_off, self.current_time, self.current_room)

        #print("ASIST Malmo Data Logger Summary of Participant in Sparky Map")
        #print("Active Timeframes (" + str(float(self.movement_time)/1000.0) + " second intervals): " + str(self.active_times))
        #print("Inactive Timeframes (" + str(float(self.movement_time)/1000.0) + " second intervals): " + str(self.inactive_times))
        
        #print("Save Strategy Type: " + self.save_strategy())
        #print("Green Saves: " + str(self.green_saves))
        #print("Yellow Saves: " + str(self.yellow_saves))
        #print("Unique Retrace Nodes: " + str(len(self.nodes)))
        #print("Total Retrace Nodes: " + str(self.total_nodes))
        #print("Room Revisit Counts: " + str(self.room_revisits))
        #print("Portion of rooms visited: " + str(self.get_num_rooms_visited()) + "/" + str(len(self.rooms)-2))
        #print("Re-entered already-visited rooms " + str(self.get_num_room_retrace()) + " times.")

        print("Mission started at: " + str(self.start_time) + '/n')

        #print("Victim Encounters: ")

        #for enc in self.encounters.values():
        #    print(enc)

        #for e in self.events:
        #    print(e)
        for room_visit in self.room_visits:
            print(str(room_visit))
            
if __name__ == "__main__":
    parser = Parse(sys.argv[1], sys.argv[2], sys.argv[3])