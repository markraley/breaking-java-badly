BEGIN {	printf("[\n"); }

/^run/ {
	delete x_arr; delete y_arr; count=0;
}

$1 ~ /^[0-9.]+/ {x_arr[count]=int($1);y_arr[count++]=$2}

/^seconds/ {
	printf("{\n");

	printf("\t\"x_arr\" : [");
	for (i=0;i<count-1;i++) {
		printf("%d,", x_arr[i]);
	}
	printf("%d ]\n", x_arr[count-1]);

	print "\t\t,"

	printf("\t\"y_arr\" : [");
	for (i=0;i<count-1;i++) {
		printf("%d,", y_arr[i]);
	}
	printf("%d ]\n", y_arr[count-1]);

	printf("}\n");
}


END {	printf("]\n"); }