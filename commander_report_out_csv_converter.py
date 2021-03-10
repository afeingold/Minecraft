import os



final_csv = []






for i in range(1, 53):
    if i == 49:
        continue

    final_csv.append([])

    with open(f"Participant {i}.txt") as file:
        line = file.readline90
        while line:
            if line == None:
                break
            final_csv[i].append(line.split('?'))
            line = file.readLine()




with open("commander_report_outs.csv", 'w') as final_file:
    for line in final_csv:
        final_file.write(','.join(line))


