import os
import sys


parser_version = sys.argv[1]

# this is a list of participant numbers with a single JSON file. 
# It excludes #11 and #35, which each have a pair of files.
participants = [1,2,4,7,9,12,13,14,16,17,18,19,20,21,22,24,25,26,27,28,29,32,33,36,37,38,39,40,41,42,43,44,45,46,47,48,50,51,52]

if parser_version == '4':
	for p in participants:
		os.system("python3 Parser-v" + parser_version + ".py json_files/Participant\ " + str(p) + ".json Sparky.csv > parser_output/participant" + str(p) + "_parser-v" + parser_version + "_output.txt")
elif parser_version == '5':
	for p in participants:
		os.system("python3 Parser-v" + parser_version + ".py json_files/Participant\ " + str(p) + ".json Sparky.csv " + str(p) + " > parser_output/participant" + str(p) + "_parser-v" + parser_version + "_output.txt")