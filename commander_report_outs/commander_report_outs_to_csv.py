import sys

final_csv = []


for i in range(1, 53):
    if i == 49:
        continue

    line_array = []

    with open(f"Participant {i}.txt") as file:
        line = file.readline()
        while line:
            if line == None:
                break
            line_array.extend(line.replace("\n", "").replace(",",";").split('?'))
            line = file.readline()

    final_csv.append(line_array)





with open("commander_report_outs.csv", 'w') as final_file:
    for line in final_csv:
        text_line = ','.join(line)
        final_file.write(f"{text_line}\n")


