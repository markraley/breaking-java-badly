BEGIN {	printf("[\n"); pair_count=0}

/^run/ {
	delete run_arr; run_count=0;
}

$1 ~ /^[0-9.]+/ {run_arr[run_count++]=$2}

/^seconds/ {
	asort(run_arr);
	printf("{\"x\":%d, \"y\":%d},\n",$2, int(run_arr[int(run_count/2)]/1024))

}


END {	printf("]\n"); }