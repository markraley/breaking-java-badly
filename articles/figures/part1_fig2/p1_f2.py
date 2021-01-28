import matplotlib
matplotlib.use('Agg')

import json

import pandas as pd
import matplotlib.pyplot as plt
import pylab
import numpy as np

#
# generates boxplot for "Breaking Java Badly" article series
#
#		- part one figure two
#		- presents PC Test One (LL) Parallel Old data set
#
# some code fragments taken from matplotlib example boxplot code
#

def label_point(x, y, val, ax):
	a = pd.concat({'x': x, 'y': y, 'val': val}, axis=1)
	for i, point in a.iterrows():
		ax.text(point['x'], point['y'], str(point['val']))

with open('r4_ll_pogc.json', 'r') as myfile:
    data=myfile.read()

data_obj = json.loads(data)

print(len(data_obj))
for d in data_obj:
	print(len(d))

fig,ax = pylab.subplots(figsize=(7, 5))
fig.subplots_adjust(left=0.1, right=0.95, top=0.85, bottom=0.15)

# Creating plot
bp = ax.boxplot(data_obj)
ax.set_xticklabels(["1M", "4M", "12M",
						"20M", "28M", "36M", "40M"])

ax.yaxis.grid(True, linestyle='-', which='major', color='lightgrey',
               alpha=0.5)
ax.set(
    axisbelow=True,  # Hide the grid behind plot objects
    title=('Simple-Producer Consumer Test One (Linked List)\n'
    		'Run Times for increasing MCL Settings\n'
    		'ParallelOldGC'),
    xlabel='Maximum Capacity Limit (MCL) Setting',
    ylabel='Total Execution Time (seconds)',
)

num_boxes = len(bp['medians'])
medians = np.empty(num_boxes)
print(len(bp['medians']))
for i in range(num_boxes):
	print(i+1, len(bp['fliers'][i]._y), bp['fliers'][i]._y)
	med = bp['medians'][i]
	median_x = []
	median_y = []
	for j in range(2):
		median_x.append(med.get_xdata()[j])
		median_y.append(med.get_ydata()[j])
	medians[i] = median_y[0]

pos = np.arange(num_boxes) + 1
upper_labels = [str(int(round(s, 0))) for s in medians]
weights = ['bold', 'semibold']
for tick, label in zip(range(num_boxes), ax.get_xticklabels()):
	k = tick % 2
	ax.text(pos[tick], .90, upper_labels[tick],
		transform=ax.get_xaxis_transform(),
		horizontalalignment='center', size='small',
		weight=weights[k])

# mark OOMs and single longest run (see test battery results file)
ax.plot(7, 795, marker='*', color='red')
ax.plot(7, 639, marker='*', color='red')
ax.plot(7, 630, marker='*', color='red')
ax.plot(7, 912, marker='*', color='red')

ax.plot(6, 2228, marker='*', color='green')

plt.show()

plt.savefig('p1_f2.png', format='png', dpi=144)