import csv

shouldBeMap = dict([(i, 0) for i in range(0, 31)])

with open('log.csv', 'r') as logfile:
    logreader = csv.reader(logfile)
    for i in logreader:
        if len(i) == 2:
            continue
        dataId = int(i[1])
        v = int(i[2])

        if v == '1':
            shouldBeMap.update({ dataId: '0' })
        else:
            shouldBeMap.update({ dataId: '1' })

for i in shouldBeMap.values():
    print(i, end='')
print()