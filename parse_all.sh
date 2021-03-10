#!/bin/bash
echo "Parsing JSON files using $1"

for i in 1 2 4 7 9 10 12 13 14 16 17 18 19 20 21 22 23 24 25 26 27 28 29 32 33 36 37 38 39 40 41 42 43 44 45 46 47 48 50 51 52
do
	echo "Parsing Participant $i JSON File"
	python3 '$1' 'Participant $i$.json' 'Sparky.csv' > '.parser_output/participant$i$_$1$_output.txt'
done

echo "Parsing Participant 11 JSON File"

