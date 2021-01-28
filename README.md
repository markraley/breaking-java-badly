# breaking-java-badly
Methodology and code for GC stress testing of OpenJDK 1.8 using different memory collectors under various synthetic loads.
See PDFs in articles folder for detailed explanation.

FYI - code here currently uses tabs.

# test execution

typical test execution usage from java_heap_tests folder (java files hould be compiled in place).

`./t.sh 1 768 PCFrame02 1 12 ParallelOldGC test`

- 12 tests numbered 1 thru 12 of 768 Million numbers are produced and consumed with a queue size limit of 1 Million are executed.

params are

`<MCL in Millions> <Count in millions> <run id start> <run id end> <collector> <results folder>`

output captured to specified results folder

# GC analysis plot

Log analyzer in wally/wally1.py

simple usage -

`python3 wally1.py gc8.log.file`

params are

`<JVM output log file> [-t '<plot title> -pause_ratio <float> -Xmx <heap size> -NewRatio <int>]`'

output

png is generated with decorated name with 'png' added as prefix and suffix
