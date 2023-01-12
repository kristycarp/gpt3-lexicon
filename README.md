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
Full usage of the pipeline to create a new lexicon requires the OpenAI API and the Google Custom Search API. 

## Usage
