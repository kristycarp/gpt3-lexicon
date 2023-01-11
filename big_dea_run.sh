#!/bin/bash

#SBATCH --time=2-0:00:00
#SBATCH --mem=64G
#SBATCH --output=./logs/dea_%j.out
#SBATCH --error=./logs/dea_%j.err
#SBATCH --partition=rbaltman
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=kcarp@stanford.edu
#SBATCH --job-name=dea_drugs

echo $i
cat controlled_seed.txt | awk -F',' '{print $'$i'}' > tmp_seed_i.txt
cat tmp_seed_i.txt
python redmed_gpt.py --temp 1 --freq 0 --pres 0 --prompts 1000 --save --outdir dea --seeds tmp_seed_i.txt
# python redmed_gpt.py --temp 1 --freq 0 --pres 0 --prompts 1 --save --outdir dea --seeds tmp_seed_i.txt
