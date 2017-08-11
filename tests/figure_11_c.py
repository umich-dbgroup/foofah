import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')

import numpy as np
import matplotlib.pyplot as plt
import csv

lengthy_tasks = ['exp0_2', 'exp0_3', 'exp0_15', 'exp0_17', 'exp0_29', 'exp0_30', 'exp0_48', 'exp0_potters_wheel_merge_split', 'exp0_potters_wheel_split_fold', 'exp0_proactive_wrangling_complex', 'exp0_crime_data_wrangler']
complex_tasks = ['exp0_3', 'exp0_4', 'exp0_5', 'exp0_6', 'exp0_8', 'exp0_10', 'exp0_11', 'exp0_13', 'exp0_15', 'exp0_19', 'exp0_25', 'exp0_26', 'exp0_28', 'exp0_30', 'exp0_36', 'exp0_41', 'exp0_45', 'exp0_49', 'exp0_51', 'exp0_potters_wheel_divide', 'exp0_potters_wheel_fold', 'exp0_potters_wheel_unfold', 'exp0_potters_wheel_split_fold', 'exp0_potters_wheel_fold_2', 'exp0_proactive_wrangling_complex', 'exp0_proactive_wrangling_fold', 'exp0_craigslist_data_wrangler', 'exp0_crime_data_wrangler', 'exp0_reshape_table_structure_data_wrangle']

def count_success(file_name):
    test_result = []
    with open(file_name, 'r') as csvfile:
        csv_result = csv.reader(csvfile, delimiter=',')
        test_result = list(csv_result)

    all_count = 0
    lengthy_count = 0
    complex_count = 0

    row_id = 0
    for row in test_result:
        if row_id == 0:
            row_id += 1
            continue

        benchmark_id = row[0]
        num_example_for_benchmark_id = -1
        for i in range(1,6):
            if row[i] == '':
                continue
            else:
                temp = row[i].split(':')
                time = temp[0]
                result = temp[1]

                if result == 's':
                    num_example_for_benchmark_id = i
                    break
                else:
                    continue

        if num_example_for_benchmark_id >= 0:
            all_count += 1

            if benchmark_id in lengthy_tasks:
                lengthy_count += 1

            if benchmark_id in complex_tasks:
                complex_count += 1


    return [all_count * 1.0 / 50 * 100, lengthy_count * 1.0  / len(lengthy_tasks) * 100, complex_count * 1.0  / len(complex_tasks) * 100]



categorical_result = {
'bfs_no_prune': [],
'bfs': [],
'rule': [],
'ted_batch': []
}

categorical_result['bfs_no_prune'] = count_success('./test_result/bfs_no_prune.csv')
categorical_result['bfs'] = count_success('./test_result/bfs.csv')
categorical_result['rule'] = count_success('./test_result/rule_based.csv')
categorical_result['ted_batch'] = count_success('./test_result/ted_batch.csv')


# Draw figues
ind = np.arange(3)  # the x locations for the groups
width = 0.2       # the width of the bars

fig, ax = plt.subplots()
rects1 = ax.bar(ind - 0.3, categorical_result['bfs_no_prune'], width, color='green', label='BFS NoPrune')
rects2 = ax.bar(ind - 0.1, categorical_result['bfs'], width, color='orange', label='BFS')
rects3 = ax.bar(ind + 0.1, categorical_result['rule'], width, color='blue', label='Rule Based')
rects4 = ax.bar(ind + 0.3, categorical_result['ted_batch'], width, color='red', label='TED Batch')


ax.set_ylabel('Percentage of scenarios')
ax.set_xlabel('Test cases and breakdowns')
ax.set_xticks(ind + width / 2)
ax.set_xticklabels(('All', 'Lengthy', 'Complex'))
ax.set_ylim([0, 100])
ax.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=4, mode="expand", borderaxespad=0.)


plt.savefig('./figures/figure_11_c.png')
plt.close(fig)