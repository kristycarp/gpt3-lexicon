# creates largescale evaluation plots after pipeline run and filters
# used to create figure 8 in the accompanying manuscript

import pandas as pd
import os
import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt
import argparse


def main(args):
    discussed_list = open("controlled_widely_discussed.txt","r").read().split("\n")

    if args.widelydiscussed:
        suffix = "_widely_discussed"
    else:
        suffix = ""

    n = 0
    n_blank = 0
    n_terms = []
    n_uniq = []
    n_filter = []
    n_ungs = []
    redmed = pd.read_csv("redmed_lexicon.tsv",sep="\t")
    for fname in os.listdir(args.d):
        if args.widelydiscussed and not fname[:-4] in discussed_list: 
        continue
        df = pd.read_csv(os.path.join(args.d, fname), index_col=0)
        if "Google" in df.columns:
            google_col = "Google"
        else:
            google_col = "GPT-3 term in Google"
        if len(df) == 0:
            n_blank += 1
            continue
        if "Error" in df[google_col].tolist():
            print(fname)
            continue
        n += 1
        
        n_terms.append(len(df))
        n_uniq.append(len(df["GPT-3 term"].unique()))
        filter_df = df.loc[df.apply(lambda row: (row[google_col] == True or row[google_col] == "True") and (row["GPT-3 term"] == row["seed for prompt"] or not row["GPT-3 term"] in redmed["drug"].tolist()),axis=1)]
        if len(filter_df) == 0:
            n_filter.append(0)
            n_ungs.append(0)
        else:
            n_filter.append(len(filter_df["GPT-3 term"].unique()))
            n_ungs.append(len(filter_df.loc[filter_df.apply(lambda row: row["seed for prompt"] != row["Seed of GPT-3 term in RedMed"], axis=1)]["GPT-3 term"].unique()))

    if args.plot:
        plt.hist(n_terms, 20, color="darkgray", edgecolor="black")
        plt.xlabel("Total number of terms generated")
        plt.ylabel("Drugs")
        plt.savefig(os.path.join(args.plotdir, "total%s.png" % suffix))
        plt.clf()

        plt.hist(n_uniq, 20, color="darkgray", edgecolor="black")
        plt.xlabel("Number of unique terms generated")
        plt.ylabel("Drugs")
        plt.savefig(os.path.join(args.plotdir, "unique%s.png" % suffix))
        plt.clf()

        plt.hist(n_filter, 20, color="darkgray", edgecolor="black")
        plt.xlabel("Number of unique GPT-3 synonyms")
        plt.ylabel("Drugs")
        plt.savefig(os.path.join(args.plotdir, "filter%s.png" % suffix))
        plt.clf()

        plt.hist(n_ungs, 20, color="darkgray", edgecolor="black")
        plt.xlabel("Number of UNGSes")
        plt.ylabel("Drugs")
        plt.savefig(os.path.join(args.plotdir, "ungs%s.png" % suffix))
        plt.clf()

    print("Number of drugs skipped bc blank: %d" % n_blank)
    print("Number of drugs analyzed: %d" % n)
    print("Average total number of terms generated: %d" % int(sum(n_terms) / n))
    print("Average number of unique terms generated: %d" % int(sum(n_uniq) / n))
    print("Average number of unique GPT-3 synonyms: %d" % int(sum(n_filter) / n))
    print("Average number of UNGSes: %d" % int(sum(n_ungs) / n))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--plot', action="store_true", help="Flag to generate new plots and save as .png")
    parser.add_argument('--widelydiscussed', action="store_true", help="Flag to indicate that only widely-discussed drugs should be included in analysis")
    parser.add_argument('-d', type=str, help="directory of query pipeline output files to analyze")
    parser.add_argument('--plotdir', type=str, help="directory in which to save plots")
    args = parser.parse_args()

    main(args)
