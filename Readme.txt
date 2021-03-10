ASIST Malmo Data Logger Summary

Background:  CRA Malmo Data Logger gernates Minecraft malmo data from a Participant going 
		through the ASIST Search and Resecue task, in this case using the 
		Sparky map. The logger tracks a 7x7 block area of the block types.
		The logger also captures x,y,z plus pitch+yaw orientation area. 
		Logger records a data entry every 0.2 seconds (approx 5 times a second).
		The parser reduces this large data logger file to key events and info.
		A *victim save* is considered when a prismarine  block (green) or a gold
		block (yellow) changes to a bone block in the same location.
		*Retrace* is revisiting an "area", a 3-radius block-circle area 
		(ie., a "node"), which allows for a 3 block set of steps to not count as
		traveing to a new occupied area, referred to as a node variable in the code.
		

Usage:
  Open command line, such as Powershell on windows and type
  > python .\Parser-v3.py '.\Participant 4.json' .\Sparky.csv > participant4_parser-v3_output.txt

The analysis and output is wrt locations defined by map (e.g., Sparky.csv)

Output:
  Open the selected output file, e.g., "parse_output.txt"
  Review summary info:
	* Active Timeframes 	= amount of "time" spent moving. 
					Currently active seconds
					Timeframe is set to 1 sec of movement > 1 block
	* Inactive Timeframes 	= amount of "time" spent not moving
	* Saves Dictionary	= numbered list of victim saves in order
					min #:[unique victims saved in that minute]
	* Save Strategy Types	
		Yellow first 	= If the yellow to green saves > threshold (e.g. 85%)
		Green first 	= If the yellow to green saves < threshold (e.g. 85%)
		Save any	= Other wise
  	* Unique Retrace Nodes	= Count of unique retrace of locations, count once for unique locs
	* Total Retrace Nodes	= Count for every time a location is revisited
	* Room Revisit Counts	= Count for every unique room/area revisit, finding victims, save victims. Comma seperated list