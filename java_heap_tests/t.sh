#!/bin/bash
size=$1
num_count=$2
test_name=$3 #compiled test expected to be in sub-directory of the same name
rep_start=$4
rep_count=$5
collector=$6
target_dir=$7
output_log="${target_dir}/r.dat"

for i in $(seq $rep_start $rep_count)
do
echo "run ${i} - ${size} ${num_count} ${test_name} ${collector} ${output_log}" \
	| tee -a "${output_log}"
sleep 7
start=$SECONDS
java -cp "${test_name}" -XX:+Use${collector} -XX:+PrintGCDetails -XX:+PrintGCDateStamps \
	-XX:+ExitOnOutOfMemoryError -Xmx2g -Xloggc:"${target_dir}/gc8.log" \
	${test_name} $size $num_count | tee -a "${output_log}"
end=$SECONDS
echo "seconds" $(($end-$start)) | tee -a "${output_log}"

cp "${target_dir}/gc8.log" "${target_dir}/gc8.log.${i}"

done
