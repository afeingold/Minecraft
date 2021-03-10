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

class retrace_node:
    x = 0
    z = 0
    distance = 3
    
    def __init__(self, x_pos, z_pos):
        self.x = x_pos
        self.z = z_pos
    
    
    def isNearby(self, x_pos, z_pos):
        return self.distance >= math.sqrt((self.z - z_pos)**2)+((self.x - x_pos)**2)



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




    ####
    # Victim Saving Methods
    ####

    encounters = {}                     # Dict of all victim encounters, indexed by hash of location
    current_encounters = {}             # Dict of victim encounters not yet completed
    vic_dict = {}
    green_saves = 0
    yellow_saves = 0



    def victim_knowledge(self, msg):
        factor = int(math.sqrt(len(msg["ground_truth"])))
        offset = int(factor/2)
        cur_z = int(math.floor(self.current_z))
        cur_x = int(math.floor(self.current_x))


        # Close any encounters that have ended in skipping
        for enc in self.current_encounters.items():
            if enc[1].victim_x < cur_x - offset or enc[1].victim_x > cur_x + ((factor - 1) - offset) or enc[1].victim_z < cur_z - offset or enc[1].victim_z > cur_z + ((factor - 1) - offset):
                enc[1].close(self.current_time, "Skipped")
                self.encounters[enc[0]] = enc[1]
                del self.current_encounters[enc[0]]



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

                      
                        if "gold" in msg["ground_truth"][z * factor + x] and hsh not in self.current_encounters:
        
                            victim_room = self.map_data[int(math.floor(z_loc))][int(math.floor(x_loc))]
                            if hsh not in self.vic_dict:
                                self.events.append("Yellow victim at (" + str(int(math.floor(x_loc + self.x_off))) + ", " + str(math.floor(z_loc + self.z_off)) + ") found in " + victim_room + " at " + self.get_data(msg))
                                self.vic_dict[hsh] = "yellow_victim"
                            if victim_room[1:] == self.current_room[1:] or (victim_room in ["r208a","r208c"] and self.current_room in ["r208a","r208c"]) or (victim_room in ["r216a","r216c"] and self.current_room in ["r216a","r216c"]):
                                self.current_encounters[hsh] = victim_encounter(int(math.floor(x_loc + self.x_off)), int(math.floor(z_loc + self.z_off)), "Yellow", self.current_time, victim_room)
                        
                            

                  
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
                        

                            
                        if self.vic_dict[hsh] == "green_victim":
                            self.vic_dict[hsh] = "bone"
                            self.events.append("Green Victim at (" + str(int(math.floor(x_loc + self.x_off))) + ", " + str(math.floor(z_loc + self.z_off)) + ") saved in " + self.current_room + " at " +  self.get_data(msg))
                            self.green_saves += 1
                            if hsh not in self.current_encounters:
                                victim_room = self.map_data[int(math.floor(z_loc))][int(math.floor(x_loc))]
                                self.current_encounters[hsh] = victim_encounter(int(math.floor(x_loc + self.x_off)), int(math.floor(z_loc + self.z_off)), "Green", "ERROR", victim_room)
                        

                        self.current_encounters[hsh].close(self.current_time, "Saved")
                        self.encounters[hsh] = self.current_encounters[hsh]
                        del self.current_encounters[hsh]




    save_threshold = .85                #   Threshold to consider a save first strategy
    def save_strategy(self):
        green_saves = 0
        yellow_saves = 0     
        for i in self.encounters.values():
            if i.action_taken == "Saved":
                if i.victim_type == "Green":
                    green_saves += 1
                elif i.victim_type == "Yellow":
                    yellow_saves += 1
        if green_saves + yellow_saves == 0:
            return "Save none"

        if (yellow_saves / (float)(green_saves + yellow_saves) > self.save_threshold):
            return "Yellow first"
        if (green_saves / (float)(green_saves + yellow_saves) > self.save_threshold):
            return "Green first" #In case this happens should be noted
        return "Save any"
    
    
    ####
    # Get Active Time Methods
    ####
    current_x = 0                       # Current location x
    current_z = 0                       # Current location z
    last_checked_time_x = 0             # x at last checked time
    last_checked_time_z = 0             # z at last checked time
    movement_range = 1                  # Distance player needs to move for 
    movement_time = 1000                # Milliseconds to determine if user has been inactive
    last_movement_check_time = None     # Timestamp of previous checked time
    active_times = 0
    inactive_times = 0
    total_retrace_time = 0
    def get_active_time(self, msg):
        self.current_x = msg["XPos"]
        self.current_z = msg["ZPos"]
        if self.last_checked_time_x == 0 and self.last_checked_time_z == 0:
            self.last_checked_time_x = msg["XPos"]
            self.last_checked_time_z = msg["ZPos"]
            self.last_movement_check_time = self.current_time
            return
        
        #if movement_time has passed since previous checked time
        delta_time = (self.current_time - self.last_movement_check_time)
        if (delta_time.seconds * 1000 + (delta_time.microseconds/1000)) > self.movement_time:
            
            if self.revisiting_a_room:
                self.total_retrace_time += 1


            #Check if the user has been active in the last timeframe
            distance = math.sqrt(((self.last_checked_time_x - msg["XPos"])**2)+((self.last_checked_time_z - msg["ZPos"])**2))

            #Update references to last observation
            self.last_movement_check_time = self.current_time
            self.last_checked_time_x = msg["XPos"]
            self.last_checked_time_z = msg["ZPos"]
        
            if distance >= self.movement_range:
                self.active_times += 1
            elif 'gold' not in msg["ground_truth"] and 'prismarine' not in msg["ground_truth"]:
                self.inactive_times += 1







    ####
    # Retrace Data Methods
    ####
    nodes = []                          # Nodes used for checking exploration
    current_node = None                 # Current exploration node
    total_nodes = 0                     # Total nodes entered
    def get_retrace_amount(self):
    
        # Dont do anything when the player is in the current node
        if self.current_node is not None and self.current_node.isNearby(self.current_x, self.current_z):
            return 
    
        # Check if any node is currently being occupied
        nearby = None
        for node in self.nodes:
            if node.isNearby(self.current_x, self.current_z):
                nearby = node
                break
                
            
        #If no nearby node is in use then this is a new node
        if nearby is None:
            nearby = retrace_node(self.current_x, self.current_z)
            self.nodes.append(nearby)
            self.current_node = nearby
            
        # Either revisiting a node or a new node is found
        self.total_nodes += 1

    current_room = None                 # Space current in
    room_revisits = {}                  # Spaces visited
    revisiting_a_room = False          # True if currently revisiting a room
    def get_room_retrace(self, msg):
        if self.current_room is None:
            self.current_room = self.map_data[int(math.floor(msg["ZPos"])) - self.z_off][int(math.floor(msg["XPos"])) - self.x_off]
            self.room_revisits[self.current_room] = 1
            return
        
        next_room = self.map_data[int(math.floor(msg["ZPos"])) - self.z_off][int(math.floor(msg["XPos"])) - self.x_off]
        if next_room != self.current_room:
            if (next_room == 'r208a' and self.current_room == 'r208c') or (next_room == 'r208c' and self.current_room == 'r208a') or (next_room == 'r216a' and self.current_room == 'r216c') or (next_room == 'r216c' and self.current_room == 'r216a'):
                return
            if next_room not in self.room_revisits:
                self.room_revisits[next_room] = 0
                self.revisiting_a_room = False
            else:
                self.revisiting_a_room = True
            self.current_room = next_room
            self.room_revisits[self.current_room] += 1

    
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
            if self.not_during_report_out():
                self.get_active_time(message)
            #self.get_retrace_amount()
            self.get_room_retrace(message)
            #self.victim_knowledge(message)

        #self.encounters.update(self.current_encounters)
        
        print("ASIST Malmo Data Logger Summary of Participant in Sparky Map")
        print("Active Timeframes (" + str(float(self.movement_time)/1000.0) + " second intervals): " + str(self.active_times))
        print("Inactive Timeframes (" + str(float(self.movement_time)/1000.0) + " second intervals): " + str(self.inactive_times))
        
        print(f"\n Timeframes spent in redundant room visits: {str(self.total_retrace_time)}")
        #print("Save Strategy Type: " + self.save_strategy())
        #print("Green Saves: " + str(self.green_saves))
        #print("Yellow Saves: " + str(self.yellow_saves))
        #print("Unique Retrace Nodes: " + str(len(self.nodes)))
        #print("Total Retrace Nodes: " + str(self.total_nodes))
        #print("Room Revisit Counts: " + str(self.room_revisits))
        #print("Portion of rooms visited: " + str(self.get_num_rooms_visited()) + "/" + str(len(self.rooms)-2))
        #print("Re-entered already-visited rooms " + str(self.get_num_room_retrace()) + " times.")

        print("Mission started at: " + str(self.start_time))

        #print("Victim Encounters: ")

        #for enc in self.encounters.values():
        #    print(enc)

        #for e in self.events:
        #    print(e)
            
if __name__ == "__main__":
    parser = Parse(sys.argv[1], sys.argv[2], sys.argv[3])