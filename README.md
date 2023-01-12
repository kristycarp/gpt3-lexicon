!! REPOSITORY UNDER CONSTRUCTION !!

# Build colloquial lexicons with GPT-3
A pipeline for the automated querying and filtering of GPT-3 terms to create lexicons of colloquial terms, with a central application in social media-based pharmacovigilance of drugs of abuse (specifically opioids). This repository is a companion to Carpenter and Altman, 2023 (in review).

## Requirements
The following dependencies are required:
- matplotlib==3.5.1
- numpy==1.23.1
- openai==0.22.1
- pandas==1.4.3
- python-dotenv==0.21.0
- scipy==1.9.0
- tqdm==4.64.0

We recommend installing the dependencies in a Conda environment. This can be done by running `conda env create -f environment.yml` to create the environment and then `conda activate gpt3` to activate it.

## API credentials
Full usage of the pipeline to create a new lexicon requires the OpenAI API and the Google Custom Search API. Create an OpenAI API key by first [making an OpenAI account](https://beta.openai.com/signup) and then [creating a new secret key](https://beta.openai.com/account/api-keys). Create a Google Custom Search API key by following the instructions [here](https://developers.google.com/custom-search/v1/overview). *Note that both GPT-3 queries and Google search queries cost money!*

Once you have obtained your API keys, create a `.env` file with the following contents:

```
GOOGLE_API_KEY=[your Google private key here]
SEARCH_ENG_ID=[your Google Custom Search Engine ID here]
OPENAI_API_KEY=[your OpenAI private key here]
```

## Usage
