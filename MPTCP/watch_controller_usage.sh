if [ ! -z $1 ]
then
	process_name=$1
	echo $1
	echo $process_name
	pid=`ps -elf | grep $process_name | grep -v grep |grep -v "watch_controller_usage.sh" |awk '{print $4}'`
	all=`ps -elf | grep $process_name | grep -v grep |grep -v "watch_controller_usage.sh" `
	echo $pid
	echo $all
	file_name=$process_name".txt"
	echo $file_name
	top -p $pid -b -n 150 -d 1.0 >> $file_name
	echo "------------" >> $file_name
fi


