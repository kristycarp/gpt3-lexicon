# This script is for analyzing the results of the parameter sweep.
# The resulting output file can be visualized with param_search_plots.py

import pandas as pd
import os
from tqdm import tqdm
import argparse


def main(args):
    fs = os.listdir(args.d)
    fs = [f for f in fs if os.path.isfile(os.path.join(args.d, f))]

    dic = dict()
    dic["model"] = []
    dic["temp"] = []
    dic["freq"] = []
    dic["pres"] = []
    dic["prompts"] = []
    dic["queries_per_prompt"] = []
    dic["counter"] = []
    dic["n_terms"] = []
    dic["n_uniq"] = []
    dic["n_terms_same_redmed_seed"] = []
    dic["n_terms_other_redmed_seed"] = []
    dic["n_terms_redmed_inside"] = []
    dic["n_terms_not_seed_yes_inside"] = []
    dic["n_terms_not_seed_not_inside"] = []
    dic["n_terms_google_alone"] = []
    dic["n_terms_google_pill"] = []
    dic["n_terms_google"] = []
    dic["n_terms_not_redmed_yes_google"] = []
    dic["n_terms_not_redmed_not_google"] = []
    dic["n_uniq_same_redmed_seed"] = []
    dic["n_uniq_other_redmed_seed"] = []
    dic["n_uniq_redmed_inside"] = []
    dic["n_uniq_not_seed_yes_inside"] = []
    dic["n_uniq_not_seed_not_inside"] = []
    dic["n_uniq_google_alone"] = []
    dic["n_uniq_google_pill"] = []
    dic["n_uniq_google"] = []
    dic["n_uniq_not_redmed_yes_google"] = []
    dic["n_uniq_not_redmed_not_google"] = []
    dic["n_ungs"] = []

    redmed_df = pd.read_csv("redmed_lexicon.tsv",sep="\t")

    for f in tqdm(fs):
        model, _, temp, _, freq, _, pres, _, prompts, _, _, _, queries_per_prompt, _, counter = f[:-4].split("_")
        dic["model"].append(model)
        dic["temp"].append(float(temp) / 100)
        dic["freq"].append(float(freq) / 100)
        dic["pres"].append(float(pres) / 100)
        dic["prompts"].append(prompts)
        dic["queries_per_prompt"].append(queries_per_prompt)
        dic["counter"].append(counter)

        df = pd.read_csv(os.path.join(args.d, f))
        df = df.loc[df["seed for prompt"] == args.seed]

        # number of terms generated
        dic["n_terms"].append(len(df))

        # number of unique terms generated
        dic["n_uniq"].append(len(df["GPT-3 term"].unique()))

        # number of terms in redmed under the same seed
        tmp = df.loc[df["Seed of GPT-3 term in RedMed"] == args.seed]
        dic["n_terms_same_redmed_seed"].append(len(tmp))
        dic["n_uniq_same_redmed_seed"].append(len(tmp["GPT-3 term"].unique()))

        # number of terms in redmed under a different seed
        not_redmed = df.loc[df["Seed of GPT-3 term in RedMed"] != args.seed]
        tmp = not_redmed.loc[not_redmed["Seed of GPT-3 term in RedMed"] != "False"]
        dic["n_terms_other_redmed_seed"].append(len(tmp))
        dic["n_uniq_other_redmed_seed"].append(len(tmp["GPT-3 term"].unique()))

        # number of terms with a redmed term inside of them
        tmp = df.loc[df["RedMed term inside GPT-3 term"]]
        dic["n_terms_redmed_inside"].append(len(tmp))
        dic["n_uniq_redmed_inside"].append(len(tmp["GPT-3 term"].unique()))

        # number of terms that are not in redmed but have a redmed term inside of them
        tmp = not_redmed.loc[not_redmed["RedMed term inside GPT-3 term"]]
        dic["n_terms_not_seed_yes_inside"].append(len(tmp))
        dic["n_uniq_not_seed_yes_inside"].append(len(tmp["GPT-3 term"].unique()))

        # number of terms that are not in redmed and don't have a redmed term inside of them
        tmp = not_redmed.loc[-not_redmed["RedMed term inside GPT-3 term"]]
        dic["n_terms_not_seed_not_inside"].append(len(tmp))
        dic["n_uniq_not_seed_not_inside"].append(len(tmp["GPT-3 term"].unique()))

        # number of terms validated by google
        tmp = df.loc[df["GPT-3 term in Google"] == "True"]
        google_terms = tmp["GPT-3 term"].tolist()
        dic["n_terms_google_alone"].append(len(tmp))
        dic["n_uniq_google_alone"].append(len(tmp["GPT-3 term"].unique()))

        # number of terms validated by google when adding "pill"
        tmp = df.loc[df["GPT-3 term + pill in Google"] == "True"]
        dic["n_terms_google_pill"].append(len(tmp))
        dic["n_uniq_google_pill"].append(len(tmp["GPT-3 term"].unique()))

        # total number of terms validated by google in some way
        tmp = df.loc[df["GPT-3 term in Google"] == "False"]
        tmp = tmp.loc[tmp["GPT-3 term + pill in Google"] == "True"]
        yes_google_terms = set(google_terms + tmp["GPT-3 term"].tolist())
        dic["n_terms_google"].append(dic["n_terms_google_alone"][-1] + len(tmp))
        dic["n_uniq_google"].append(len(yes_google_terms))

        # number of terms not in redmed and not validated by google
        tmp = not_redmed.loc[not_redmed["GPT-3 term in Google"] == "False"]
        tmp = tmp.loc[tmp["GPT-3 term + pill in Google"] == "False"]
        dic["n_terms_not_redmed_not_google"].append(len(tmp))
        dic["n_uniq_not_redmed_not_google"].append(len(tmp["GPT-3 term"].unique()))

        # number of terms that are not in redmed but are validated by google in some way
        dic["n_terms_not_redmed_yes_google"].append(len(not_redmed) - dic["n_terms_not_redmed_not_google"][-1])
        not_redmed_yes_google = set(not_redmed["GPT-3 term"].tolist()).intersection(yes_google_terms)
        dic["n_uniq_not_redmed_yes_google"].append(len(not_redmed_yes_google))

        # number of UNGSes (unique novel gpt-3 synonyms)
        # aka unique terms not in redmed that pass google and drug name filter
        df["pass name filter"] = df.apply(lambda row: not row["GPT-3 term"] in redmed_df["drug"].tolist() or row["GPT-3 term"] == row["seed for prompt"], axis=1)
        pass_name_filter = set(df.loc[df["pass name filter"]]["GPT-3 term"].tolist())
        dic["n_ungs"].append(len(pass_name_filter.intersection(not_redmed_yes_google)))

    df = pd.DataFrame()
    for k in dic.keys():
        df[k] = dic[k]
    df.to_csv(args.outfname)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=str, help="index term (seed term)")
    parser.add_argument('-d', type=str, help="directory of parameter search output files")
    parser.add_argument('-o', type=str, help="name of analysis output file")
    args = parser.parse_args()

    main(args)
