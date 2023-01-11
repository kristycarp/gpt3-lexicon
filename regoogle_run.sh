#!/bin/bash

#SBATCH --time=1-0:00:00
#SBATCH --mem=128G
#SBATCH --output=./logs/regoogle_%j.out
#SBATCH --error=./logs/regoogle_%j.err
#SBATCH --partition=rbaltman
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=kcarp@stanford.edu
#SBATCH --job-name=googling

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
