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


# Count at least how many examples needed

num_examples = {}
for i in range(1,6):
    num_examples[i] = 0

num_examples['not found'] = 0

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
        num_examples[num_example_for_benchmark_id] += 1
    else:
        num_examples['not found'] += 1

for i in range(1,6):
    if num_examples[i] == 0:
        del num_examples[i]

if num_examples['not found'] == 0:
    del num_examples['not found']

N = len(num_examples)

num_examples_keys = num_examples.keys()
num_examples_keys.sort()
num_examples_values = []

for key in num_examples_keys:
    num_examples_values.append(num_examples[key])


# Draw figures
ind = np.arange(N) 
width = 0.35    

fig, ax = plt.subplots()
rects1 = ax.bar(ind, num_examples_values, width, color='blue')


ax.set_ylabel('Number of scenarios')
ax.set_xlabel('Number of example records')
ax.set_xticks(ind + width / 2)
ax.set_xticklabels(('1', '2', 'Not Found'))
ax.set_ylim([0, 30])

plt.savefig('./figures/figure_11_a.png')
plt.close(fig)