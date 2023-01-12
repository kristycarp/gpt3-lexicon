#!/bin/bash

# shell script to rerun Google filter (e.g. if errors occurred, ran out
# of daily queries, changed how filter works)
# uses regoogle_tmp.txt to track number of API requests made in a day
# recommended to run this with a job scheduler
# put arguments for job scheduler here
# use e.g. --export=ALL,i=10 to set $i to 10
# because APIs have rate limiting, must run seeds in series, not in parallel!

tmp=$(wc -l regoogle_tmp.txt)
abort=${tmp:0:1}
if [ $abort -eq 2 ]
then
    echo "API quota reached. Aborting..."
    exit 91
elif [ $abort -eq 1 ]
then
    echo $i
    f=$(ls outputs/dea | head -n $i | tail -n 1)
    count=$(cat regoogle_tmp.txt)
    echo $f
    echo $count
    python rerun_google.py -f outputs/dea/$f --memo memo.p --depth 10 --count_start $count > regoogle_tmp.txt
else
    echo "An error occurred. Check regoogle_tmp.txt. Aborting..."
    exit 91
fi
