#!/bin/sh

source source_me.sh
for csvfile in task_files/*.csv;
do
	echo "======================================================"
	echo $csvfile
	echo "======================================================"
	./run_bbq_tasks.py --shuffle --flat --max-questions 199 --tasks $csvfile
	sleep 0.1
done
