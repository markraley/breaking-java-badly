import re
import argparse
import time
import matplotlib
import ntpath

# pre-compile commonly used regex expressions

tengen_re = re.compile("ParOldGen: ([0-9]+)K->([0-9]+)K")
permgen_re = re.compile("Metaspace: ([0-9]+)K->([0-9]+)K")
datetime_re = re.compile("^([-0-9T\:]+)\.([0-9]+)([-\+][0-9]+)\:")
reltime_re = re.compile("^ ?([0-9\.]+)\:")
fullgc_re = re.compile("^ \[Full GC")
minorgc_re = re.compile("^ \[GC")

#
# wally1.py by Mark Raley
#
# some basic terms -
#   fgc - full garbage collection
#   chain or wall - sequence of temporally adjacent fgcs
#
# This program looks for full (major) garbage collection log entries
# in the provided log file. Among these any entries of sufficent
# adjacency so as to constitute a chain or wall are tracked.
#
# A fgc scatter plot is then generated, with annotations for chains or
# walls (if any).
#

from collections import namedtuple

#
# GC - tuple
#
# parsed subelements of one GC log entry, either major (paused) or minor
#

gc_param_str = (
                    'start_time duration_time ' # retain trailing space
                    'tenured_start_kb tenured_end_kb '
                    'perm_start_kb perm_end_kb timestamp paused'
                )

class GC(namedtuple('GC', gc_param_str)):
    pass
    # start_time - seconds from server start
    # duration_time - seconds
    # tenured_start_kb - int, optional
    # tenured_end_kb - int, optional
    # perm_start_kb - int, optional
    # perm_end_kb - int, optional
    # timestamp, str, optional
    # paused, boolean

#
# FGC_Chain tuple
#

fgc_chain_param_str = (
        'first_fgc_tuple last_fgc_tuple '       #retain trailing space
        'chain_pause_time chain_minor_time '
        'duration_time '
        'full_gc_count minor_gc_count'
    )

class FGC_Chain(namedtuple('FGC_Chain', fgc_chain_param_str)):
    pass

#
# testGCAdjacency()
#

def testGCAdjacency(last_fgc_tuple, cur_fgc_tuple, pause_ratio_threshold):
    last_start_sec = last_fgc_tuple.start_time
    last_end_sec = last_fgc_tuple.start_time + last_fgc_tuple.duration_time

    cur_start_sec = cur_fgc_tuple.start_time
    cur_end_sec = cur_fgc_tuple.start_time + cur_fgc_tuple.duration_time
    diff_time = cur_start_sec - last_end_sec

    # zero small time discrepencies if present
    if (diff_time < 0.0):
        assert(abs(diff_time) < 0.1)
        diff_time = 0.0

    pause_ratio = (
                    cur_fgc_tuple.duration_time
                    / (diff_time + cur_fgc_tuple.duration_time)
                )

    if (False): # debug output
        print('diff_time',
                round(diff_time,2),
                "{0:.2f}".format(pause_ratio*100.0),
                cur_fgc_tuple.duration_time)

    if (pause_ratio >= pause_ratio_threshold):
        return True
    else:
        return False

#
# parseLegacyGC()
#
# Parse legacy parallel GC log lines from OpenJDK 1.8
#

def parseLegacyGC(line_str):
    has_date_time = False
    has_rel_time = False
    has_meta = False
    paused = False
    is_valid = False
    start_kb, end_kb = 0,0
    perm_start_kb, perm_end_kb = 0,0
    ros = line_str      # initialize rest of string
    datestamp_str = ""
    msec_str = ""

    # attempt a match and and on success capture groups
    # and set the remainder into the ros variable

    # look for absolute and/or relative time stamps

    date_mgrp = datetime_re.match(ros)
    if (date_mgrp is not None):
        has_date_time = True
        datestamp_str = date_mgrp.group(1)
        msec_str = date_mgrp.group(2)
        timezone_str = date_mgrp.group(3)
        ros = ros[date_mgrp.end():]

    rel_mgrp = reltime_re.match(ros)
    if (rel_mgrp is not None):
        has_rel_time = True
        rel_time_str = rel_mgrp.group(1)
        ros = ros[rel_mgrp.end():]

    # determine if the GC is full or not
    # and set the pause flag appropriately

    if (has_date_time or has_rel_time):
        mgrp = fullgc_re.match(ros)
        if (mgrp is not None):
            paused = True
            ros = ros[mgrp.end():]
        else:
            mgrp = minorgc_re.match(ros)
            if (mgrp is not None):
                ros = ros[mgrp.end():]
                real_mgrp = re.search("real=([0-9.]+) secs", ros)
                if (real_mgrp is not None):
                    ros = ros[real_mgrp.end():]
                    real_str = real_mgrp.group(1)
                    is_valid = True
#                   print ('GC', rel_time_str, real_str)

    if ((has_rel_time or has_date_time) and paused):
        tengen_mgrp = tengen_re.search(ros)
        if (tengen_mgrp is not None):
            start_kb = tengen_mgrp.group(1)
            end_kb = tengen_mgrp.group(2)
            ros = ros[mgrp.end():]

            permgen_mgrp = permgen_re.search(ros)
            if (permgen_mgrp is not None):
                perm_start_kb = permgen_mgrp.group(1)
                perm_end_kb = permgen_mgrp.group(2)
                ros = ros[mgrp.end():]
#               print ('perm', perm_start_kb, perm_end_kb)

        real_mgrp = re.search("real=([0-9.]+) secs", ros)
        if (real_mgrp is not None):
            ros = ros[real_mgrp.end():]
            real_str = real_mgrp.group(1)
            is_valid = True

    if (is_valid):
        return GC(
                    float(rel_time_str),
                    float(real_str),
                    int(start_kb),
                    int(end_kb),
                    int(perm_start_kb),
                    int(perm_end_kb),
                    (datestamp_str + "." + msec_str),
                    paused)
    else:
        return None

#
# getETimeFromDateStamp() - not in current use
#
# Test usage - getETimeFromDateStamp("2020-02-06T17:21:16")
#

def getETimeFromDateStamp(timestamp_str):
#   date_time = '29.08.2011 11:05:02'
#   pattern = '%d.%m.%Y %H:%M:%S'
    pattern = '%Y-%m-%dT%H:%M:%S'
    etime_sec = int(time.mktime(time.strptime(timestamp_str, pattern)))
    return etime_sec

#
# parseNum() - expands command line entries into integers for computations
#

def parseNum(num_str):

    mgrp = re.match("([0-9]+)([kmgKMG]?)", num_str)

    if (mgrp is not None):
        value = int(mgrp.group(1))
        factor = 1
        factor_str = mgrp.group(2).upper()
        if (factor_str == "K"):
            factor = 1024
        elif(factor_str == "M"):
            factor = 1024**2
        elif(factor_str == "G"):
            factor = 1024**3
#       print('value', value, factor)
        return value*factor
    else:
        return None

#
# main()
#

def main():

    # process args

    p = argparse.ArgumentParser()
    p.add_argument("file_source")   # input log file
    p.add_argument("-t", default="")    # title
    p.add_argument("-st", default="")   # sub title (lower left)
    p.add_argument("-fpr", default=.65) # full pause ratio
    p.add_argument("-mbr", default=0.0) # minor bridge ratio
    p.add_argument("-o", default="")    # specify output file
    p.add_argument("-c", default=3)    # minimum full gcs in a chain

    # params that are used to calculate the max tenured space
    p.add_argument("-Xmx", default="2g")
    p.add_argument("-NewRatio", default="2")
    args = p.parse_args()

    # resolve output file name for matplotlib png, use -o if defined
    ofile_str = args.o
    if (len(ofile_str) == 0):
        ofile_str = 'png_' + ntpath.basename(args.file_source) + '.png'

    # calculate the max tenured space (generation) available to the JVM

    xmx = parseNum(args.Xmx)
    nr = parseNum(args.NewRatio)
    max_tenured_space_kb = int(xmx * (nr / (nr + 1.0)) / 1024)

    minimum_chain_count = int(args.c)
    pause_ratio = float(args.fpr)
    minor_pause_ratio = float(args.mbr)
    if (minor_pause_ratio > 0.0):
        use_minor_gcs = True
    else:
        use_minor_gcs = False

    print('xmx', xmx, 'max_tenured_space_kb', max_tenured_space_kb)

    f = open(args.file_source, "r")

    first_found = False

    chain_started = False
    chain_count = 0
    chain_arr = []

    time_arr = []
    tenured_start_arr = []
    tenured_end_arr = []

    title_str = args.t
    subtitle_str = args.st

    # counts and measures minor GCs between full GCs
    bridge_mgc_count, bridge_mgc_time = 0, 0.0

    # if enabled, accumulates any minor GCs that form bridges
    chain_minor_count, chain_minor_time = 0, 0.0

    #
    # scan the provided log file line by line looking for and tracking
    # temporally adjacent fgc entries
    #

    for line in f:
        fgc_tuple = parseLegacyGC(line)

        # reject unrecognized GC lines
        if (fgc_tuple is None):
            continue

        if(not fgc_tuple.paused):
            if (use_minor_gcs): # collect minor gc data if enabled
                bridge_mgc_time += fgc_tuple.duration_time
                bridge_mgc_count += 1
        else:
            # process the fgc found
            time_arr.append(fgc_tuple.start_time)
            tenured_start_arr.append(fgc_tuple.tenured_start_kb
                                    / max_tenured_space_kb * 100.0)
            tenured_end_arr.append(fgc_tuple.tenured_end_kb
                                    / max_tenured_space_kb * 100.0)

            if (not first_found):
                first_found = True
                last_fgc_tuple = fgc_tuple
                bridge_mgc_count, bridge_mgc_time = 0, 0.0
                continue

            cur_fgc_tuple = fgc_tuple

            adjacent = testGCAdjacency(last_fgc_tuple,
                                        cur_fgc_tuple,
                                        pause_ratio)

            fgc_gap_time = (cur_fgc_tuple.start_time
                                -(last_fgc_tuple.start_time
                                    + last_fgc_tuple.duration_time)
                            )
            bridged_adjacent = (bridge_mgc_count > 0
                            and (bridge_mgc_time / fgc_gap_time)
                                                >= minor_pause_ratio)

            # check for adjacency between fgcs, either normal or bridged
            if (adjacent):
                if (not chain_started):
                    chain_started = True
                    chain_count = 2
                    chain_pause_time = (cur_fgc_tuple.duration_time
                                        + last_fgc_tuple.duration_time)
                    chain_start_tuple = last_fgc_tuple
                else:
                    chain_count += 1
                    chain_pause_time += (cur_fgc_tuple.duration_time)
            elif (bridged_adjacent):
                if (not chain_started):
                    chain_started = True
                    chain_count = 2
                    chain_pause_time = (cur_fgc_tuple.duration_time
                                        + last_fgc_tuple.duration_time)
                    chain_start_tuple = last_fgc_tuple

                    chain_minor_count = bridge_mgc_count
                    chain_minor_time = bridge_mgc_time
                else:
                    chain_count += 1
                    chain_pause_time += (cur_fgc_tuple.duration_time)

                    chain_minor_time += bridge_mgc_time
                    chain_minor_count += bridge_mgc_count
            else:
                # chain break found
                # chain is chain_start_tuple <--> last_fgc_tuple inclusive
                if (chain_started and chain_count >= minimum_chain_count):
                    chain_duration_time = (last_fgc_tuple.duration_time
                                        + last_fgc_tuple.start_time
                                        - chain_start_tuple.start_time)
                    chain_arr.append(FGC_Chain(
                                        chain_start_tuple,
                                        last_fgc_tuple,
                                        chain_pause_time,
                                        chain_minor_time,
                                        chain_duration_time,
                                        chain_count,
                                        chain_minor_count))
                    chain_started = False
                    chain_count, chain_pause_time = 0, 0.0
                    chain_start_tuple = None

            last_fgc_tuple = cur_fgc_tuple
            bridge_mgc_count, bridge_mgc_time = 0, 0.0

    #
    # process last open chain if any
    #

    if (chain_started and chain_count >= minimum_chain_count):
        chain_duration_time = (last_fgc_tuple.duration_time
                            + last_fgc_tuple.start_time
                            - chain_start_tuple.start_time)
        chain_arr.append(
                FGC_Chain(chain_start_tuple, last_fgc_tuple,
                            chain_pause_time, chain_minor_time,
                            chain_duration_time,
                            chain_count, chain_minor_count))

    f.close()

    #
    # generate scatter plot of
    #   % tenured space used (y-axis) vs. time (x-axis)
    #

    matplotlib.use('Agg')
    import pylab

    fig,ax = pylab.subplots(1)

    pylab.plot(time_arr, tenured_start_arr, linestyle='-', marker='v')
    pylab.plot(time_arr, tenured_end_arr, linestyle='-', marker='^')

    if (len(title_str) > 0):
        text_str = title_str.replace('*','\n')
        pylab.title(text_str)

    if (len(subtitle_str) > 0):
        text_str = subtitle_str
        ann = ax.annotate(text_str, xy=(.05, .01 ),
                            xycoords="figure fraction", size=11)

    pylab.xlabel('time (seconds)')
    pylab.ylabel('tenured space used (%)')

    # add outside of frame annotations

    trans = ax.get_yaxis_transform() # y in data units, x in axes fraction
    text_str = 'log file: ' + args.file_source
    ann = ax.annotate(text_str, xy=(.80, 106.0 ), xycoords=trans, size=8)

    text_str = 'Xmx: ' + args.Xmx + '    NewRatio: ' + args.NewRatio
    ann = ax.annotate(text_str, xy=(0.0, 106.0 ), xycoords=trans, size=8)

    #
    # annotate with fgc chains (walls)
    #
    # height is % paused (y-axis, scaled down) vs. time interval (x-axis)
    #

    for c in chain_arr:
        first_fgc = c.first_fgc_tuple # first fgc of chain
        last_fgc = c.last_fgc_tuple # last fgc of chain
        pause_per = 100.0 * ((c.chain_pause_time + c.chain_minor_time)
                                    / c.duration_time)
        print('chain', '{:.1f}%'.format(pause_per),
                        '{:.1f} seconds'.format(c.duration_time),
                        first_fgc.timestamp,
                        last_fgc.timestamp)

        rect = matplotlib.patches.Rectangle(
                                (first_fgc.start_time,0),
                                c.duration_time,
                                pause_per * .75, # scale rect height
                                linewidth=1,edgecolor='r',
                                facecolor='none',hatch='//'
                            )
        ax.add_patch(rect)
        height = rect.get_height()
        ax.annotate('{:.1f}%'.format(pause_per),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom', size=8)

    pylab.savefig(ofile_str, dpi=120)

if __name__ == '__main__':
    main()

