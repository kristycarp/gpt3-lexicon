# main script for running pipeline
# does the process shown in figure 1 of accompanying manuscript
# must set up OpenAI API, Google Search API, and .env before using

import os
import random
import openai
import numpy as np
import pandas as pd
import argparse
import json
import requests
import pickle
import time
from dotenv import load_dotenv



# obtains all the candidate redmed synonyms to sample from for prompt
def get_candidate_examples(seed, redmed):
    subdf = redmed.loc[redmed["drug"] == seed]
    terms = set()
    for col in subdf.columns[2:7]: # only include misspellings and pillmarks, and single words in known
        l = subdf[col].tolist()[0].split(",")
        if len(l) <= 1:
            if l == "" or l == ["-"]:
                continue
        for t in l:
            if col in subdf.columns[3:7] or len(t.split("_")) == 1:
                terms.add(t)
    return terms


# uses a prompt template (either with or without counterexamples) and
# randomly sampled redmed synonyms to create a prompt with which to query GPT-3
def get_prompt(seed, terms, include_counterexamples=False, redmed=None, verbose=True): 
    if include_counterexamples:
        examples = random.sample(list(terms),2)
    else:
        examples = random.sample(list(terms),3)
    examples = [e.replace("_"," ") for e in examples]
    if verbose:
        print(examples)

    # alternate prompt template with counterexamples
    # hardcoded for alprazolam example as a test
    # not changed from hardcoded version since it performed worse than
    # the other prompt
    if include_counterexamples:
        prompt = "these are not synonyms for %s:\n 1. ativan\n2. zoloft\n3. lexapro\n4. klonopin\n" % (seed)
        prompt += "but these are synonyms for %s:\n 1. %s\n2. %s\n3." % (seed, examples[0], examples[1])
    else:
        prompt = "ways to say %s:\n1. %s\n2. %s\n3. %s\n4." % (seed, examples[0], examples[1], examples[2])

    return prompt


# submit query to GPT-3, collect response, clean and parse
def query(eng, prompt, temp, maxt, freq, pres):
    response = openai.Completion.create(engine=eng,
                                        prompt=prompt,
                                        temperature=temp,
                                        max_tokens=maxt,
                                        frequency_penalty=freq,
                                        presence_penalty=pres)
    time.sleep(1.5) # must space out queries for rate limiting

    rtext = response["choices"][0]["text"].replace("\"","").lower()
    rtext = rtext.split("\n")
    clean_rtext = []
    clean_rtext.append(rtext[0][1:].replace(" ","_"))
    if len(rtext) > 1:
        for i in range(1, len(rtext)):
            if rtext[i][0].isnumeric() and rtext[i][1] == ".":
                clean_rtext.append(rtext[i][2:].strip().replace(" ","_"))
            elif rtext[i][:2].isnumeric() and rtext[i][2] == ".":
                clean_rtext.append(rtext[i][3:].strip().replace(" ","_"))
            else:
                print("warning: response not formatted as list!")
                print(rtext[i])

    return clean_rtext


# checks to see if any of the terms in terms (a list) are present in
# the generated response r (a string)
def redmed_term_in_response(r, terms):
    r_tokens = [r.lower() for r in r.split("_")]
    for t in terms:
        t_tokens = t.split("_")
        if len(t_tokens) == 1:
            if t in r_tokens:
                return True
        else:
            if len(r_tokens) < len(t_tokens):
                continue
            for i in range(len(r_tokens) - len(t_tokens) + 1):
                match = True
                for j in range(i, i+len(t_tokens)):
                    if r_tokens[j] != t_tokens[j-i]:
                        match = False
                        break
                if match:
                    return True
    return False


# uses the google search api to search for a term
# will return true if a seed term appears in the top 10 search results
def in_google_search(term, seed, memo, depth=10, count=False, offline=False):
    googled = False
    term = term.replace("_"," ")
    if not term in memo.keys():
        memo[term] = dict()
    if not seed in memo[term].keys():
        memo[term][seed] = dict()
        memo[term][seed]["result"] = False
        memo[term][seed]["depth"] = -1
    if memo[term][seed]["depth"] == -1:
        for start in range(1, depth, 10):
            if not memo[term][seed]["depth"] == -1:
                break
            google_key_name = "google_search_response_%d" % (start)
            if not google_key_name in memo[term].keys():
                if offline:
                    if count:
                        return "Error", -1, memo, googled
                    else:
                        return "Error", -1, memo
                    
                response = requests.get("https://customsearch.googleapis.com/customsearch/v1?key=%s&cx=%s&q=%s&start=%d" % (os.environ.get("GOOGLE_API_KEY"), os.environ.get("SEARCH_ENG_ID"), term, start))
                googled = True
                time.sleep(1.5)
                if response.status_code == 200:
                    memo[term][google_key_name] = response.text
                else:
                    print(response.status_code)
                    if count:
                        return "Error", -1, memo, googled
                    else:
                        return "Error", -1, memo
            j = json.loads(memo[term][google_key_name])
            if int(j["searchInformation"]["totalResults"]) < start:
                break
            try:
                for idx, elem in enumerate(j['items']):
                    if redmed_term_in_response(elem["title"].replace(" ","_"), [seed]) or ("snippet" in elem.keys() and redmed_term_in_response(elem["snippet"].replace(" ","_"), [seed])):
                        memo[term][seed]["result"] = True
                        memo[term][seed]["depth"] = idx + start
                        break
            except Exception as e:
                print(repr(e))
                memo[term].pop(seed)
                if count:
                    return "Error", -1, memo, googled
                else:
                    return "Error", -1, memo
    if count:
        return memo[term][seed]["result"], memo[term][seed]["depth"], memo, googled
    else:
        return memo[term][seed]["result"], memo[term][seed]["depth"], memo


# searches for a term in the whole redmed lexicon
# if that term is present in the lexicon, will return the seed term it belongs to
# if that term is not present in the lexicon, will return False
def find_seed_for_term(term, df):
    df["all"] = df.apply(lambda row: row["drug"] + "," + row["known"] + "," + row["misspellingPhon"] + "," + row["edOne"] + "," + row["edTwo"] + "," + row["pillMark"] + "," + row["google_ms"] + "," + row["google_title"] + "," + row["google_snippet"] + "," + row["ud_slang"], axis=1)
    df["contains_term"] = df.apply(lambda row: term in row["all"].split(","), axis=1)
    df = df.loc[df["contains_term"]]
    if len(df) == 0:
        return [False, ""]
    else:
        return [True, df["drug"].tolist()[0]]


def main(args):
    openai.api_key = os.environ.get("OPENAI_API_KEY")
    redmed = pd.read_csv("redmed_lexicon.tsv",sep="\t")
    seeds = open(args.seeds,"r").read().strip().split(",")
    print(seeds)

    if args.save:
        gpt_terms = []
        gpt_seeds = []
        redmed_seeds_for_gpt_term = []
        redmed_term_in_gpt_term = []
        gpt_google = []
        gpt_google_add = []
        gpt_google_depth = []

    try:
        memo = pickle.load(open(args.memo,"rb"))
    except:
        memo = dict()

    for seed in seeds:
        try:
            terms = get_candidate_examples(seed, redmed)
        except IndexError:
            print("Insufficient RedMed terms to sample examples from. Exiting.")
            continue
        for i in range(args.prompts):
            try:
                prompt = get_prompt(seed, terms, include_counterexamples=args.counterexamples, verbose=not args.save)
            except ValueError:
                print("Insufficient RedMed terms to sample examples from. Exiting.")
                break
            for j in range(args.queries_per_prompt):
                while True:
                    try:
                        response = query(args.engine, prompt, args.temp, args.tokens, args.freq, args.pres)
                    except:
                        continue
                    else:
                        break
                for r in response:
                    seed_for_term = find_seed_for_term(r, redmed)
                    term_in_response = redmed_term_in_response(r, terms)
                    for google_add in ["", " pill", " drug", " slang"]:
                        google, depth, memo = in_google_search(r + google_add, seed, memo, depth=args.depth)
                        if google == "True":
                            break
                    if google != "True":
                        google_add = None
                    if args.save:
                        gpt_terms.append(r)
                        gpt_seeds.append(seed)
                        if seed_for_term[0]:
                            redmed_seeds_for_gpt_term.append(seed_for_term[1])
                        else:
                            redmed_seeds_for_gpt_term.append(seed_for_term[0])
                        redmed_term_in_gpt_term.append(term_in_response)
                        gpt_google.append(google)
                        gpt_google_add.append(google_add)
                        gpt_google_depth.append(depth)
                    else:
                        if seed_for_term[0]:
                            seed_for_term[1] = " (%s)" % seed_for_term[1]
                        print("%s (In RedMed: %s%s; Includes RedMed Term for %s: %s; Google Search validation: %s (%s))" % (r, seed_for_term[0], seed_for_term[1], seed, term_in_response, google, google_add))
                if not args.save:
                    print("")

    pickle.dump(memo, open(args.memo, "wb"))

    if args.save:
        if len(seeds) == 1:
            outfname = "%s.csv" % seeds[0]
        else:
            outfname = "_".join([args.engine, "temp", str(int(args.temp*100)), "freq", str(int(args.freq*100)), "pres", str(int(args.pres*100)), "prompts", str(args.prompts), "queries_per_prompt", str(args.queries_per_prompt), "counter", str(args.counterexamples)])+".csv"

        outdf = pd.DataFrame(data=np.array([gpt_terms, gpt_seeds, redmed_seeds_for_gpt_term, redmed_term_in_gpt_term, gpt_google, gpt_google_add, gpt_google_depth]).T, columns=['GPT-3 term','seed for prompt', 'Seed of GPT-3 term in RedMed', 'RedMed term inside GPT-3 term', 'Google', 'Google added token', 'Google depth'])
        outdf.to_csv(os.path.join("outputs", args.outdir, outfname))


if __name__ == "__main__":
    load_dotenv()

    parser = argparse.ArgumentParser()
    parser.add_argument('--engine', type=str, help="GPT-3 engine to use.", default="text-davinci-002")
    parser.add_argument('--temp', type=float, help="Sampling temperature. Higher values means the model will take more risks.", default=0.5)
    parser.add_argument('--tokens', type=int, help="The maximum number of tokens to generate in the completion.", default=2048)
    parser.add_argument('--freq', type=float, help="Frequency penalty. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim.", default=0)
    parser.add_argument('--pres', type=float, help="Presence penalty. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics.", default=0)
    parser.add_argument('--prompts', type=int, help="Number of prompts to generate per seed.", default=1)
    parser.add_argument('--queries_per_prompt', type=int, help="Number of times to query with each prompt.", default=1)
    parser.add_argument('--counterexamples', action="store_true", help="Flag for including counterexamples in the prompt.")
    parser.add_argument('--memo', type=str, help="Memo file name to reduce API requests.", default="memo.p")
    parser.add_argument('--save', action="store_true", help="Flag for saving outputs to csv.")
    parser.add_argument('--seeds', type=str, help="file containing seeds to use for prompts", default="defaultseed.txt")
    parser.add_argument('--outdir', type=str, help="directory within the outputs folder in which to save the outputs", default="")
    parser.add_argument('--depth', type=int, help="how deep to go for google search filter", default=10)
    args = parser.parse_args()

    main(args)
