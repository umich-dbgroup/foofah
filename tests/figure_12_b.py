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

# FullPrune
full_prune_time = get_sorted_time('./test_result/ted_batch.csv')

# GlobalPrune
global_prune_time = get_sorted_time('./test_result/ted_batch_global_prune.csv')

# PropPrune
prop_prune_time = get_sorted_time('./test_result/ted_batch_op_prune.csv')

# NoPrune
no_prune_time = get_sorted_time('./test_result/ted_batch_no_prune.csv')


x_axis = range(0, 100, 2)

fig, ax = plt.subplots()
ax.plot(x_axis, full_prune_time, '--', color='red', linewidth=4, label='FullPrune')
ax.plot(x_axis, global_prune_time, color='blue', label='GlobalPrune')
ax.plot(x_axis, prop_prune_time, '--', color='orange', linewidth=4, label='PropPrune')
ax.plot(x_axis, no_prune_time, color='green', label='NoPrune')
ax.set_ylabel('Time (seconds)')
ax.set_xlabel('Percentage of test cases')
ax.set_ylim([0, 70])
ax.plot((0, 100), (60, 60), '--', color='black')
ax.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=4, mode="expand", borderaxespad=0.)

plt.savefig('./figures/figure_12_b.png')
plt.close(fig)