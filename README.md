# breaking-java-badly
Methodology and code for GC stress testing of OpenJDK 1.8 using different memory collectors under various synthetic loads.

FYI - code here currently uses tabs.

typical test execution from java_heap_tests directory (java files hould be compiled in place).

`./t.sh 1 768 PCFrame02 1 5 ParallelOldGC test`

see t.sh script for parameter details.

params are

`<MCL in Millions> <Count in millions> <run id start> <run id end> <collector> <results directory>`

Log analyzer in wally/wally1.py - see pdfs in article directory for example outputs

simple run -

`python3 wally1.py gc8.log.file -t 'plot title`

params are

`<JVM output log file> [-t '<plot title> -pause_ratio <float> -Xmx <heap size> -NewRatio <int>]`'

png is generated with decorated name with 'png' added as prefix and suffix
