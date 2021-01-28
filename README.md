# breaking-java-badly
Methodology and code for GC stress testing OpenJDK using different memory collectors under various synthetic loads.

FYI - code here currently uses tabs.

typical test execution from java_heap_tests directory (java files hould be compiled in place).

`./t.sh 1 768 PCFrame02 1 5 ParallelOldGC test`

params are

`<MCL in Millions> <Count in millions> <run id start> <run id end> <collector> <results directory>`


