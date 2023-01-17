# to create the TSVs in the `lexicon` directory

import pandas as pd
import numpy as np
import os
import argparse


# obtains the DrugBank ID for a given index term
#
# params:
# redmed (DataFrame) - RedMed lexicon in a pandas DataFrame
# idx_term (str) - index term to look up
def get_dbid(redmed, idx_term):
    row = redmed.loc[redmed["drug"] == idx_term]
    dbid = row["dbid"].tolist()[0]
    return dbid


# creates the lexicon TSV for generated GPT-3 synonyms
#
# params:
# d (str) - name of directory in which pipeline output files are located
# outfname (str) - name of TSV file to write out
def generated_lexicon(d, outfname):
    redmed = pd.read_csv("redmed_lexicon.tsv",sep="\t")
    discussed_list = open("controlled_widely_discussed.txt","r").read().split("\n")
    csvs = [f for f in os.listdir(d) if f[-4:] == ".csv"]

    idxs = []
    dbids = []
    widely_discussed = []
    gpt_synonyms = []

    for f in csvs:
        df = pd.read_csv(os.path.join(d, f), index_col=0)
        idx_term = df["seed for prompt"].unique().tolist()[0]
        if "Google" in df.columns:
            google_col = "Google"
        else:
            google_col = "GPT-3 term in Google"
        filter_df = df.loc[df.apply(lambda row: (row[google_col] == True or row[google_col] == "True") and (row["GPT-3 term"] == row["seed for prompt"] or not row["GPT-3 term"] in redmed["drug"].tolist()),axis=1)]
        terms = filter_df["GPT-3 term"].unique().tolist()
        terms = ["\'%s\'" % t for t in terms]

        idxs.append(idx_term)
        dbids.append(get_dbid(redmed, idx_term))
        widely_discussed.append(idx_term in discussed_list)
        gpt_synonyms.append(",".join(terms))

    data_dic = {"index term": idxs, "DrugBank ID": dbids, "widely discussed": widely_discussed, "GPT-3 synonyms": gpt_synonyms}
    outdf = pd.DataFrame(data=data_dic)
    outdf.to_csv(outfname, index=False, sep="\t")


# creates the lexicon TSV for generated, manually-labeled synonyms
#
# params:
# d (str) - name of directory in which pipeline output files with manual labels are located
# outfname (str) - name of TSV file to write out
def manual_lexicon(d, outfname):
    redmed = pd.read_csv("redmed_lexicon.tsv",sep="\t")
    csvs = [f for f in os.listdir(d) if f[-4:] == ".csv"]

    idxs = []
    dbids = []
    specific_syns = []
    broad_syns = []

    for f in csvs:
        df = pd.read_csv(os.path.join(d, f), index_col=0)
        idx_term = df["seed for prompt"].unique().tolist()[0]
        true_df = df.loc[df["manual label"] == "True"]
        spec = true_df["GPT-3 term"].unique().tolist()
        spec = ["\'%s\'" % t for t in spec]
        broad_df = df.loc[df["manual label"] == "?"]
        broad = broad_df["GPT-3 term"].unique().tolist()
        broad = ["\'%s\'" % t for t in broad]

        idxs.append(idx_term)
        dbids.append(get_dbid(redmed, idx_term))
        specific_syns.append(",".join(spec))
        broad_syns.append(",".join(broad))

    data_dic = {"index term": idxs, "DrugBank ID": dbids, "specific synonyms": specific_syns, "broad synonyms": broad_syns}
    outdf = pd.DataFrame(data=data_dic)
    outdf.to_csv(outfname, index=False, sep="\t")

def main(args):
    if args.generated:
        generated_lexicon(args.generated_dir, args.generated_fname)
    if args.manual:
        manual_lexicon(args.manual_dir, args.manual_fname)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--generated', action="store_true", help="Flag for creating the `drugs_of_abuse_lexicon.tsv` file with generated GPT-3 synonyms")
    parser.add_argument('--generated_dir', type=str, help="directory in which output csvs from GPT-3 query pipeline are located", default="data/big_run")
    parser.add_argument('--generated_fname', type=str, help="output filename for lexicon of generated GPT-3 synonyms", default="lexicon/drugs_of_abuse_lexicon.tsv")
    parser.add_argument('--manual', action="store_true", help="Flag for creating the `manual_label_lexicon.tsv` file with manually labeled synonyms")
    parser.add_argument('--manual_dir', type=str, help="directory in which output csvs from GPT-3 query pipeline, WITH MANUAL LABELS, are located", default="data/manual_label")
    parser.add_argument('--manual_fname', type=str, help="output filename for lexicon of manually-labeled generated synonyms", default="lexicon/manual_label_lexicon.tsv")
    args = parser.parse_args()

    main(args)
