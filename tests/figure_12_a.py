import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')

import numpy as np
import matplotlib.pyplot as plt
import csv

def get_sorted_time(file_name):
    test_result = []
    with open(file_name) as csvfile:
        csv_result = csv.reader(csvfile, delimiter=',')
        test_result = list(csv_result)

    sorted_time = []

    row_id = 0
    for row in test_result:
        if row_id == 0:
            row_id += 1
            continue

        benchmark_id = row[0]

        time_temp = []

        for i in range(1,6):
            if row[i] == '':
                time_temp.append(70)
            else:
                temp = row[i].split(':')
                time = temp[0]
                result = temp[1]

                if (result == 's'):
                    time_temp.append(float(time))
                    break
                else:
                    time_temp.append(float(time))

        # The time for this benchmark is the total time (including the failed ones) the user experience until Foofah returns a perfect program for this benchmark.
        sorted_time.append(sum(time_temp))

    sorted_time.sort()
    return sorted_time


# TED Batch
ted_batch_time = get_sorted_time('./test_result/ted_batch.csv')

# BFS
bfs_time = get_sorted_time('./test_result/bfs.csv')

# Rule based
rule_time = get_sorted_time('./test_result/rule_based.csv')

# BFS NoPrune
bfs_no_prune_time = get_sorted_time('./test_result/bfs_no_prune.csv')

x_axis = range(0, 100, 2)

fig, ax = plt.subplots()
ax.plot(x_axis, ted_batch_time, color='red', label='Ted Batch')
ax.plot(x_axis, rule_time, color='blue', label='Rule')
ax.plot(x_axis, bfs_time, color='orange', label='BFS')
ax.plot(x_axis, bfs_no_prune_time, color='green', label='BFS NoPrune')
ax.set_ylabel('Time (seconds)')
ax.set_xlabel('Percentage of test cases')
ax.set_ylim([0, 70])
ax.plot((0, 100), (60, 60), '--', color='black')
ax.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=4, mode="expand", borderaxespad=0.)

plt.savefig('./figures/figure_12_a.png')
plt.close(fig)