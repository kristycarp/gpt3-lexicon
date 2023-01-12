#!/bin/bash

# shell script to conduct largescale run of pipeline
# recommended to run this with a job scheduler
# put arguments for job scheduler here
# use e.g. --export=ALL,i=10 to set $i to 10
# because APIs have rate limiting, must run seeds in series, not in parallel!

echo $i
cat controlled_seed.txt | awk -F',' '{print $'$i'}' > tmp_seed_i.txt
cat tmp_seed_i.txt
python redmed_gpt.py --temp 1 --freq 0 --pres 0 --prompts 1000 --save --outdir outputs/dea --seeds tmp_seed_i.txt
