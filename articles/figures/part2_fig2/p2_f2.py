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
#		- part two figure two
#		- presents PC Test One (LL) G1 data set
#
# some code fragments taken from matplotlib example boxplot code
#

def label_point(x, y, val, ax):
	a = pd.concat({'x': x, 'y': y, 'val': val}, axis=1)
	for i, point in a.iterrows():
		ax.text(point['x'], point['y'], str(point['val']))

with open('r5_ll_g1gc.json', 'r') as myfile:
    data=myfile.read()

data_obj = json.loads(data)

fig,ax = pylab.subplots(figsize=(7, 5))
fig.subplots_adjust(left=0.1, right=0.95, top=0.85, bottom=0.15)

# Creating plot
bp = ax.boxplot(data_obj)
#ax.set_xticklabels(["1M", "2M", "4M", "8M", "12M", "16M",
#						"20M", "24M", "28M", "32M", "36M", "40M"])
ax.set_xticklabels(["1M", "4M", "12M",
						"20M", "28M", "36M", "44M","48M","52M"])

ax.yaxis.grid(True, linestyle='-', which='major', color='lightgrey',
               alpha=0.5)
ax.set(
    axisbelow=True,  # Hide the grid behind plot objects
    title='Simple Producer-Consumer Test One (Linked List)\n'
    		'Run Times for increasing MCL Settings\nG1',
    xlabel='Maximum Capacity Limit (MCL) Setting',
    ylabel='Total Execution Time (seconds)',
)

# Due to the Y-axis scale being different across samples, it can be
# hard to compare differences in medians across the samples. Add upper
# X-axis tick labels with the sample medians to aid in comparison
# (just use two decimal places of precision)
num_boxes = len(bp['medians'])
medians = np.empty(num_boxes)
print(len(bp['medians']))
for i in range(num_boxes):
#	print(i+1, len(bp['fliers'][i]._y), bp['fliers'][i]._y)
	med = bp['medians'][i]
	median_x = []
	median_y = []
	for j in range(2):
		median_x.append(med.get_xdata()[j])
		median_y.append(med.get_ydata()[j])
	medians[i] = median_y[0]

pos = np.arange(num_boxes) + 1
upper_labels = [str(int(round(s, 0))) for s in medians]
for tick, label in zip(range(num_boxes), ax.get_xticklabels()):
	ax.text(pos[tick], .90, upper_labels[tick],
		transform=ax.get_xaxis_transform(),
		horizontalalignment='center', size='small')

#ax.plot(6, 2228, marker='*', color='green')

plt.show()

plt.savefig('p2_f2.png', format='png', dpi=144)