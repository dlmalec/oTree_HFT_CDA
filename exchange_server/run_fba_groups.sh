#!/bin/bash

if [ "$#" -ne 2 ]; 
then
        echo "usage: ./run_fba_groups.sh [num_groups] [interval]"
        exit 1
fi

groups=$1
timestamp=$(date +'%Y-%m-%d_%H:%M:%S')
interval=$2

./stop_all.sh

if [ -z "$1" ];
then
	groups=1
fi

for i in `seq $groups`;
do
	mkdir -p fba_data
	python3 run_exchange_server.py --host 0.0.0.0 --port 900$i --mechanism fba \
    --interval ${interval} --book_log CDA_DATA/${timestamp}_group_$i.log &
done
