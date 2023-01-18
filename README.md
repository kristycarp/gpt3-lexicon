# Build colloquial lexicons with GPT-3
A pipeline for the automated querying and filtering of GPT-3 terms to create lexicons of colloquial terms, with a central application in social media-based pharmacovigilance of drugs of abuse (specifically opioids). This repository is a companion to Carpenter and Altman, 2023 (in review).

## Data
This repository contains two directories for relevant data: `lexicon` and `data`.

`lexicon` is intended for quick and easy application to pharmacovigilance research. `lexicon` contains the following files:
- `drugs_of_abuse_lexicon.tsv` is a TSV with each of the 98 drugs of abuse index terms, their DrugBank IDs, indicators of whether they are considered "widely-discussed" (as described in the accompanying manuscript) and their GPT-3 synonyms as determined by the pipeline (pipeline parameters: temperature of 1.0, frequency pnealty of 0.0, presence penalty of 0.0, prompt template as described in manuscript; filters: drug name filter and Google search filter with depth 10 as described in manuscript)
- `manual_label_lexicon.tsv` is a TSV with two rows: one for alprazolam, and one for fentanyl (these are the two drugs that underwent manual labeling). Each row contains the index term, the DrugBank ID, and all of the GPT-3 generated terms for the drug that were determined to be synonyms by a human labeler. These term sets are partitioned into "specific" and "broad" subsets ("specific" indicates that the term is used for just that index term, whereas "broad" indicates that the term could be used for other related drugs as well). Both alprazolam and fentanyl are considered "widely-discussed."

`data` is intended for those who would like to dive deeper into the data, whether to replicate figures, tweak filters, or investigate other aspects of the pipeline results without needing to re-run it themselves. `data` contains three subdirectories:
- `big_run` contains the output csvs for the 98 drugs of abuse, which show each of the GPT-3 generated terms in addition to information about which filters are passed and if the generated term is present in RedMed.
- `manual_label` contains the output csvs for alprazolam and fentanyl, which show the same information as in `big_run` but additionally contain manual (i.e. human) labels.
- `param_search` contains data from the parameter search stage of pipeline development, which was done with alprazolam, benzphetamine, and heroin. The `*_grid_out.csv` files contain the summary outputs from `param_sweep_analysis.py`. The subdirectories of `param_search` contain the output csvs for each set of parameters swept (with the heroin and benzphetamine sweeps occurring concurrently).

## Scripts
The below only is relevant for those who would like to run any of the scripts contained in this repository 

### Requirements
The following dependencies are required to run the scripts contained in this repository:
- matplotlib==3.5.1
- numpy==1.23.1
- openai==0.22.1
- pandas==1.4.3
- python-dotenv==0.21.0
- scipy==1.9.0
- tqdm==4.64.0

We recommend installing the dependencies in a Conda environment. This can be done by running `conda env create -f environment.yml` to create the environment and then `conda activate gpt3` to activate it.

### API credentials
Full usage of the pipeline to create a new lexicon requires the OpenAI API and the Google Custom Search API. Create an OpenAI API key by first [making an OpenAI account](https://beta.openai.com/signup) and then [creating a new secret key](https://beta.openai.com/account/api-keys). Create a Google Custom Search API key by following the instructions [here](https://developers.google.com/custom-search/v1/overview). **Note that both GPT-3 queries and Google search queries cost money!**

Once you have obtained your API keys, create a `.env` file with the following contents:

```
GOOGLE_API_KEY=[your Google private key here]
SEARCH_ENG_ID=[your Google Custom Search Engine ID here]
OPENAI_API_KEY=[your OpenAI private key here]
```

### Usage
The different components of this repository are: conducting the parameter sweep, characterizing performance with manually-labeled data, deploying the pipeline to new index terms, and applying the generated lexicon. We expect most users will be most interested in the latter, in which case the only relevant files are those in the `lexicon` directory, and no conda environment, API keys, or usage of other scripts in this repository are necessary. Instructions for the other three components are below. You may also use `python [SCRIPTNAME] --help` to see additional documentation of arguments for any of the python scripts.

#### Conducting the parameter sweep
- create `.env` file (see above)
- run GPT-3 query pipeline for each index term and each parameter set to try: `python gpt_queries.py --engine [GPT-3 ENGINE] --temp [TEMPERATURE] --tokens [MAXIMUM TOKENS] --freq [FREQUENCY PENALTY] --pres [PRESENCE PENALTY] --prompts [NUMBER OF PROMPTS] --queries_per_prompt [NUMBER OF QUERIES PER PROMPT] --memo [NAME OF MEMO FILE] --seeds [INDEX TERM FILE] --outdir [OUTPUT CSV DIRECTORY] --depth [DEPTH OF GOOGLE SEARCH] [optional flags: --counterexamples --save]` (note most arguments have default values that many will find acceptable for their uses, see `python gpt_queries.py --help` for more info)
- analyze results of parameter sweep: `python param_sweep_analysis.py --seed [INDEX TERM] -d [CSV DIRECTORY] -o [OUTFILE NAME]`
- plot results of parameter sweep: `python param_sweep_plots.py -f [INFILE NAME] --plotdir [PLOT DIRECTORY] --col [COLUMN OF INFILE TO PLOT] --param [PARAMETER TO ANALYZE SWEEP OF]`

#### Characterizing performance with manually-labeled data
- run GPT-3 query pipeline for each index term to label and evaluate: `python gpt_queries.py --engine [GPT-3 ENGINE] --temp [TEMPERATURE] --tokens [MAXIMUM TOKENS] --freq [FREQUENCY PENALTY] --pres [PRESENCE PENALTY] --prompts [NUMBER OF PROMPTS] --queries_per_prompt [NUMBER OF QUERIES PER PROMPT] --memo [NAME OF MEMO FILE] --seeds [INDEX TERM FILE] --outdir [OUTPUT CSV DIRECTORY] --depth [DEPTH OF GOOGLE SEARCH] [optional flags: --counterexamples --save]` (note most arguments have default values that many will find acceptable for their uses, see `python gpt_queries.py --help` for more info)
- manually label all generated terms from the above (see manuscript for labeling process)
- plot results of manually-labeled analysis: `python manual_label_plots.py -f [INPUT CSV] --seed [INDEX TERM] --plotdir [PLOT DIRECTORY] [optional flags: --uniq --broad --namefilter --googlefilter]`

#### Deploying the pipeline to new index terms
- run GPT-3 query pipeline for each index term to label and evaluate: `python gpt_queries.py --engine [GPT-3 ENGINE] --temp [TEMPERATURE] --tokens [MAXIMUM TOKENS] --freq [FREQUENCY PENALTY] --pres [PRESENCE PENALTY] --prompts [NUMBER OF PROMPTS] --queries_per_prompt [NUMBER OF QUERIES PER PROMPT] --memo [NAME OF MEMO FILE] --seeds [INDEX TERM FILE] --outdir [OUTPUT CSV DIRECTORY] --depth [DEPTH OF GOOGLE SEARCH] [optional flags: --counterexamples --save]` (note most arguments have default values that many will find acceptable for their uses, see `python gpt_queries.py --help` for more info)
- if errors ocur in Googling process due to volume, re-run the Google searches (without querying GPT-3 again): `python rerun_google.py -f [CSV FILE TO UPDATE] --memo [NAME OF MEMO FILE] --depth [DEPTH OF GOOGLE SEARCH] --suffix [SUFFIX FOR UPDATED FILENAME] --count_start [START FOR API USAGE COUNT] [optional flags: --offline]`
- plot results of largescale run: `python largescale_plots.py -d [CSV DIRECTORY] --plotdir [PLOT DIRECTORY] [optional flags: --plot --widelydiscussed]`
- create lexicon TSV: `python create_lexicons.py [optional flags: --generated --manual]`

### Replicating figures
If you would like to replicate (or make similar plots to) figures from the accompanying manuscript, you may do so with the following commands:
- Figure 1: this does not show results, but rather presents the workflow undertaken by `gpt_queries.py`
- Figure 2: `python param_sweep_plots.py -f data/param_search/alprazolam_grid_out.csv --plotdir . --plot box --col n_ungs --param all`
- Figure 3: `python param_sweep_plots.py -f data/param_search/heroin_grid_out.csv --plotdir . --plot box --col n_ungs --param all` (repeat for benzphetamine)
- Figure 4: `python param_sweep_plots.py -f data/param_search/alprazolam_grid_out.csv --plotdir . --plot bar --col n_ungs --param all` (repeat for heroin and benzphetamine)
- Figure 5: `python manual_label_plots.py -f data/manual_label/alprazolam.csv --seed alprazolam --plotdir . --plot depth --uniq --broad --namefilter` (repeat for fentanyl)
- Figure 6: `python manual_label_plots.py -f data/manual_label/alprazolam.csv --seed alprazolam --plotdir . --plot freq --uniq --broad --namefilter` (repeat for fentanyl, and with google filter flag for 6c and 6d)
- Figure 7: `python manual_label_plots.py -f data/manual_label/alprazolam.csv --seed alprazolam --plotdir . --plot cm --uniq --broad` (repeat for fentanyl)
- Figure 8: `python largescale_plots.py --plot -d data/big_run --plotdir .` (repeat with widely-discussed flag)
