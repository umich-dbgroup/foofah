import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')

import numpy as np
import matplotlib.pyplot as plt
import csv

test_result = []
with open('./test_result/ted_batch.csv') as csvfile:
    csv_result = csv.reader(csvfile, delimiter=',')
    test_result = list(csv_result)

worst_time_list = []
average_time_list = []

row_id = 0
for row in test_result:
    if row_id == 0:
        row_id += 1
        continue

    benchmark_id = row[0]

    worst_time_temp = []
    average_time_temp = []

    for i in range(1,6):
        if row[i] == '':
            worst_time_temp.append(70)
            average_time_temp.append(70)
        else:
            temp = row[i].split(':')
            time = temp[0]
            result = temp[1]

            if result == 's':
                worst_time_temp.append(float(time))
                average_time_temp.append(float(time))
                break
            else:
                worst_time_temp.append(float(time))
                average_time_temp.append(float(time))

    worst_time = max(worst_time_temp)
    average_time = reduce(lambda x, y: x + y, average_time_temp) / len(average_time_temp)

    worst_time_list.append(worst_time)
    average_time_list.append(average_time)

worst_time_list.sort()
average_time_list.sort()

x_axis = range(0, 100, 2)

fig, ax = plt.subplots()
ax.plot(x_axis, worst_time_list, color='green', label='worst time')
ax.plot(x_axis, average_time_list, '--', color='red', label='average time')
ax.set_ylim([0, 40])
ax.plot((0, 100), (30, 30), '--', color='black')
ax.set_ylabel('Time (seconds)')
ax.set_xlabel('Percentage of test cases')
ax.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)

plt.savefig('./figures/figure_11_b.png')
plt.close(fig)