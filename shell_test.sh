#!/bin/bash


echo "Parsing Participant $2 JSON file using $1"
python3 $1 './json_files/Participant 4.json' 'Sparky.csv' >> './parser_output/participant4_parser-v4_output.txt'