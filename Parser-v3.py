import json
import os
import sys
import time
import math
import sched
from datetime import datetime
from operator import itemgetter, attrgetter

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
    
    ####
    # Victim Saving Methods
    ####
    saves = {}
    vic_dict = {}
    green_saves = 0
    yellow_saves = 0
    def victim_knowledge(self, msg):
        factor = int(math.sqrt(len(msg["ground_truth"])))
        offset = int(factor/2)
        cur_z = int(math.floor(self.current_z))
        cur_x = int(math.floor(self.current_x))
        for z in range(factor):
            for x in range(factor):
                x_loc = cur_x + (x - offset) - self.x_off
                z_loc = cur_z + (z - offset) - self.z_off
                if self.in_bounds(x_loc, z_loc):
                    hsh = hash(str(z_loc) + " $$ " + str(x_loc))
                    dist = math.sqrt(((cur_x - self.x_off - x_loc)**2)+((cur_z - self.z_off - z_loc)**2))
                    
                    if offset + 3 >= z and offset - 3 <= z and offset + 3 >= x and offset - 3 <= x:
                        if "prismarine" in msg["ground_truth"][z * factor + x] and hsh not in self.vic_dict:
                            self.vic_dict[hsh] = "green_victim"
                            #self.events.append("Green victim found in " + self.current_room + " at " + self.get_data(msg))
                            self.events.append("Green victim at (" + str(int(math.floor(x_loc + self.x_off))) + ", " + str(math.floor(z_loc + self.z_off)) + ") found at " + self.get_data(msg))

                      
                        if "gold" in msg["ground_truth"][z * factor + x] and hsh not in self.vic_dict:
                            self.vic_dict[hsh] = "yellow_victim"
                            #self.events.append("Yellow victim found in " + self.current_room + " at " + self.get_data(msg))
                            self.events.append("Green victim at (" + str(int(math.floor(x_loc + self.x_off))) + ", " + str(math.floor(z_loc + self.z_off)) + ") found at " + self.get_data(msg))
                        
                            

                  
                    if "bone" in msg["ground_truth"][z * factor + x] and hsh in self.vic_dict:
                        time_del = self.current_time - self.start_time
                        time_del = math.floor(time_del.seconds/60)
                        if self.vic_dict[hsh] == "yellow_victim":
                            if str(time_del) + " mins" not in self.saves:
                                self.saves[str(time_del) + " mins"] = []
                            self.vic_dict[hsh] = "bone"
                            self.saves[str(time_del) + " mins"].append("yellow_victim")
                            self.events.append("Yellow Victim at (" + str(int(math.floor(x_loc + self.x_off))) + ", " + str(math.floor(z_loc + self.z_off)) + ") saved in " + self.current_room + " at " + self.get_data(msg))
                            self.yellow_saves += 1
                            
                        if self.vic_dict[hsh] == "green_victim":
                            if (str(time_del) + " mins") not in self.saves:
                                self.saves[str(time_del) + " mins"] = []
                            self.vic_dict[hsh] = "bone"
                            self.saves[str(time_del) + " mins"].append("green_victim")
                            self.events.append("Green Victim at (" + str(int(math.floor(x_loc + self.x_off))) + ", " + str(math.floor(z_loc + self.z_off)) + ") saved in " + self.current_room + " at " +  self.get_data(msg))
                            self.green_saves += 1

    save_threshold = .85                #   Threshold to consider a save first strategy
    def save_strategy(self):
        green_saves = 0
        yellow_saves = 0     
        for i in self.saves.keys():
            green_saves += self.saves[i].count("green_victim")
            yellow_saves += self.saves[i].count("yellow_victim")
            
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
    active_x = 0                        # Current active location x
    active_z = 0                        # Current active location z
    movement_range = 1                  # Distance player needs to move for  
    movement_time = 1000                # Milliseconds to determine if user has been inactive
    last_movement = None                # Timestamp of last movement
    active_times = 0
    inactive_times = 0
    def get_active_time(self, msg):
        self.current_x = msg["XPos"]
        self.current_z = msg["ZPos"]
        if self.active_x == 0 and self.active_z == 0:
            self.active_x = msg["XPos"]
            self.active_z = msg["ZPos"]
            self.last_movement = self.current_time
            return
        
        #Check if the user has been active in the last timeframe
        distance = math.sqrt(((self.active_x - msg["XPos"])**2)+((self.active_z - msg["ZPos"])**2))
        if distance > self.movement_range:
            self.last_movement = self.current_time
            self.active_x = msg["XPos"]
            self.active_z = msg["ZPos"]
            self.active_times += 1
            return
            
        #Resets the user position after every movement time milliseconds occurs when no movement has been detected
        delta_time = (self.current_time - self.last_movement)
        if (delta_time.seconds * 1000 + (delta_time.microseconds/1000)) > self.movement_time:
            self.inactive_times += 1
            self.last_movement = self.current_time
            self.active_x = msg["XPos"]
            self.active_z = msg["ZPos"]

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
    def get_room_retrace(self, msg):
        if self.current_room is None:
            self.current_room = self.map_data[int(math.floor(msg["ZPos"])) - self.z_off][int(math.floor(msg["XPos"])) - self.x_off]
            self.room_revisits[self.current_room] = 1
            return
        
        next_room = self.map_data[int(math.floor(msg["ZPos"])) - self.z_off][int(math.floor(msg["XPos"])) - self.x_off]
        if next_room != self.current_room:
            if next_room not in self.room_revisits:
                self.room_revisits[next_room] = 0
                #self.events.append("Space " + next_room + " was first visited at " + self.get_data(msg))
            self.current_room = next_room
            self.room_revisits[self.current_room] += 1
                    
    def __init__(self, metadata_file, csv_file):
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

    def start(self):
        for i in range(0, len(self.dataset)):
            message = self.dataset[i]["message"]["data"]
            if not self.inbounds(message):
                continue
            if self.start_time == None:
                self.start_time = datetime.strptime(message["timestamp"],"%Y-%m-%dT%H:%M:%S.%f")
            self.current_time = datetime.strptime(message["timestamp"],"%Y-%m-%dT%H:%M:%S.%f")
            self.get_active_time(message)
            self.get_retrace_amount()
            self.get_room_retrace(message)
            self.victim_knowledge(message)
        
        print("ASIST Malmo Data Logger Summary of Participant in Sparky Map")
        print("Active Timeframes (" + str(float(self.movement_time)/1000.0) + " second intervals): " + str(self.active_times))
        print("Inactive Timeframes (" + str(float(self.movement_time)/1000.0) + " second intervals): " + str(self.inactive_times))
        print("Saves Dictionary: " + str(self.saves))
        print("Save Strategy Type: " + self.save_strategy())
        print("Green Saves: " + str(self.green_saves))
        print("Yellow Saves: " + str(self.yellow_saves))
        print("Unique Retrace Nodes: " + str(len(self.nodes)))
        print("Total Retrace Nodes: " + str(self.total_nodes))
        print("Room Revisit Counts: " + str(self.room_revisits))

        for e in self.events:
            print(e)
            
if __name__ == "__main__":
    parser = Parse(sys.argv[1], sys.argv[2])