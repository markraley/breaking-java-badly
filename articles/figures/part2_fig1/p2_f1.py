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
#       - part two figure one
#       - contrasts PC Test One (LL) G1 and PO (Parallel Old) data sets
#
# some code fragments taken from matplotlib example boxplot code
#

def set_box_color(bp, color):
    plt.setp(bp['boxes'], color=color)
    plt.setp(bp['whiskers'], color=color)
    plt.setp(bp['caps'], color=color)
    plt.setp(bp['medians'], color=color)

def build_median_arr(bp):
    num_boxes = len(bp['medians'])
    median_arr = np.empty(num_boxes)
    for i in range(num_boxes):
    #   print(i+1, len(bp['fliers'][i]._y), bp['fliers'][i]._y)
        med = bp['medians'][i]
        median_x = []
        median_y = []
        for j in range(2):
            median_x.append(med.get_xdata()[j])
            median_y.append(med.get_ydata()[j])
        median_arr[i] = median_y[0]
    return median_arr

def label_point(x, y, val, ax):
    a = pd.concat({'x': x, 'y': y, 'val': val}, axis=1)
    for i, point in a.iterrows():
        ax.text(point['x'], point['y'], str(point['val']))

# Producer-Consumer Test One - LL, PO
with open('r4_LL_PO.json', 'r') as myfile:
    ds1 =myfile.read()

ds1_obj = json.loads(ds1)

# Producer-Consumer Test One - LL, G1
with open('r5_LL_G1.json', 'r') as myfile:
    ds2 =myfile.read()

ds2_obj = json.loads(ds2)

fig,ax = pylab.subplots(figsize=(7, 5))
fig.subplots_adjust(left=0.1, right=0.95, top=0.85, bottom=0.15)

# Creating plot
# bp = ax.boxplot(ds1_obj, positions=np.array(range(len(ds1_obj)))*1.0)
bp1 = ax.boxplot(ds1_obj,
                    positions=np.array(range(len(ds1_obj)))*1.0 - 0.1,
                    widths=0.175,
                    sym='')
bp2 = ax.boxplot(ds2_obj,
                    positions=np.array(range(len(ds2_obj)))*1.0 + 0.1,
                    widths=0.175,
                    sym='')

set_box_color(bp1, '#D7191C') # colors are from http://colorbrewer2.org/
set_box_color(bp2, '#2C7BB6')
ax.set_xticklabels(["1M", "4M", "12M",
                        "20M", "28M", "36M", "44M"])

print(plt.xlim())

ax.yaxis.grid(True, linestyle='-', which='major', color='lightgrey',
               alpha=0.5)
ax.set(
    axisbelow=True,  # Hide the grid behind plot objects
    title=('Simple Producer-Consumer Test One (Linked List)\n'
                'Run Times for increasing MCL Settings\n'
                'compares Parallel Old with G1'),
    xlabel='Maximum Capacity Limit (MCL) Setting',
    ylabel='Total Execution Time (seconds)',
)

# build and display change in group median as percentage across top of plot

median1_arr = build_median_arr(bp1)
median2_arr = build_median_arr(bp2)

diff_arr = np.subtract(median2_arr, median1_arr)
per_arr = np.divide(diff_arr, median1_arr)
num_boxes = len(median1_arr)
plt.xticks(range(num_boxes))

print(median1_arr)
print(median2_arr)
print(diff_arr)
print(per_arr)

if (True):
    #pos = np.arange(num_boxes) + 1
    pos = np.array(range(num_boxes))*1.0
    upper_labels = [ str(round(s * 100.0, 1)) + '%' for s in per_arr ]
    for tick, label in zip(range(num_boxes), ax.get_xticklabels()):
        ax.text(pos[tick], 0.96, upper_labels[tick],
            transform=ax.get_xaxis_transform(),
            horizontalalignment='center', size='small')

# generate legend

plt.plot([], c='#D7191C', label='Parallel Old')
plt.plot([], c='#2C7BB6', label='G1')

plt.legend(loc="upper center",bbox_to_anchor=(0.5, 0.82))

plt.show()

plt.savefig('p2_f1.png', format='png', dpi=144)