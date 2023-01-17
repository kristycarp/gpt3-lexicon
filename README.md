!! REPOSITORY UNDER CONSTRUCTION !!

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
- `param_search` contains data from the parameter search stage of pipeline development, which was done with alprazolam, benzphetamine, and heroin. The `*_grid_out.csv` files contain the summary outputs from `analyze.py`. The subdirectories of `param_search` contain the output csvs for each set of parameters swept (with the heroin and benzphetamine sweeps occurring concurrently).

## Requirements
The following dependencies are required to run the scripts contained in this repository:
- matplotlib==3.5.1
- numpy==1.23.1
- openai==0.22.1
- pandas==1.4.3
- python-dotenv==0.21.0
- scipy==1.9.0
- tqdm==4.64.0

We recommend installing the dependencies in a Conda environment. This can be done by running `conda env create -f environment.yml` to create the environment and then `conda activate gpt3` to activate it.

## API credentials
Full usage of the pipeline to create a new lexicon requires the OpenAI API and the Google Custom Search API. Create an OpenAI API key by first [making an OpenAI account](https://beta.openai.com/signup) and then [creating a new secret key](https://beta.openai.com/account/api-keys). Create a Google Custom Search API key by following the instructions [here](https://developers.google.com/custom-search/v1/overview). **Note that both GPT-3 queries and Google search queries cost money!**

Once you have obtained your API keys, create a `.env` file with the following contents:

```
GOOGLE_API_KEY=[your Google private key here]
SEARCH_ENG_ID=[your Google Custom Search Engine ID here]
OPENAI_API_KEY=[your OpenAI private key here]
```

## Usage

## Replicating figures
If you would like to replicate (or make similar plots to) figures from the accompanying manuscript, you may do so with the following commands:
- Figure 1: this does not show results, but rather presents the workflow undertaken by `redmed_gpt.py`
- Figure 2: `python param_search_plots.py -f data/param_search/alprazolam_grid_out.csv --plotdir . --plot box --col n_ungs --param all`
- Figure 3: `python param_search_plots.py -f data/param_search/heroin_grid_out.csv --plotdir . --plot box --col n_ungs --param all` (repeat for benzphetamine)
- Figure 4: `python param_search_plots.py -f data/param_search/alprazolam_grid_out.csv --plotdir . --plot bar --col n_ungs --param all` (repeat for heroin and benzphetamine)
- Figure 5: `python regoogle_plots.py -f data/manual_label/alprazolam.csv --seed alprazolam --plotdir . --plot depth --uniq --broad --namefilter` (repeat for fentanyl)
- Figure 6: `python regoogle_plots.py -f data/manual_label/alprazolam.csv --seed alprazolam --plotdir . --plot freq --uniq --broad --namefilter` (repeat for fentanyl, and with google filter flag for 6c and 6d)
- Figure 7: `python regoogle_plots.py -f data/manual_label/alprazolam.csv --seed alprazolam --plotdir . --plot cm --uniq --broad` (repeat for fentanyl)
- Figure 8: `python largescale_eval.py --plot -d data/big_run --plotdir .` (repeat with widely-discussed flag)
