# Script to make depth histograms (figure 5 in companion manuscript),
# frequency histograms (figure 6 in companion manuscript), and
# confusion matrices (figure 7 in companion manuscript). Requires
# manually labeled data. Run this after generating all data and
# assigning Google and drug name filters (either in first pass or with
# rerun_google.py).

import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import argparse
import os
from sklearn.metrics import ConfusionMatrixDisplay


# codes for colors in plots to indicate manual label
# "unknown" is when there is no manual label
# "?" is when a term is manually labeled as broad (could refer to specific
# drug or to many other related drugs, e.g. benzo)
COLOR_DICT = {"True": "deepskyblue", "False": "firebrick", "Unknown": "dimgray", "?": "lemonchiffon"}


# creates a histogram of google search depth at which a term was
# found vs. number of terms found at that depth
#
# params:
# df (DataFrame) - output of pipeline run with manual labels
# plotdir (str) - directory in which to save output image
# uniq (bool) - flag for only counting each unique term once
# broad (bool) - flag for considering broad terms (terms that refer to the
#                specified drug but also other drugs, e.g. benzo) as True
# namefilter (bool) - flag for whether to remove terms that don't pass the
#                     drug name filter before plotting
def depths_bar(df, plotdir, uniq=True, broad=False, namefilter=False):
    def get_len(df):
        if uniq:
            return len(df["GPT-3 term"].unique())
        else:
            return len(df)

    fig, ax = plt.subplots()
    if uniq:
        ylab = "unique "
    else:
        ylab = ""

    fname = os.path.join(plotdir, "regoogle_depth_bar_%s.png" % ylab.strip())
    if broad:
        fname = fname[:-4] + "_broad.png"
    if namefilter:
        fname = fname[:-4] + "_namefilter.png"
    bar_width = 5
    X = 0

    for i in range(1, max(df["Google depth"]) + 1):
        subdf = df.loc[df["Google depth"] == i]
        if "manual label" in df.columns:
            ax.bar(X, get_len(subdf), width=bar_width, color=COLOR_DICT["True"])
            if not broad:
                ax.bar(X, get_len(subdf.loc[subdf["manual label"] != "True"]), width=bar_width, color=COLOR_DICT["?"])
            ax.bar(X, get_len(subdf.loc[subdf["manual label"] == "False"]), width=bar_width, color=COLOR_DICT["False"])
        else:
            ax.bar(X, get_len(subdf), width=bar_width, color=COLOR_DICT["Unknown"])
        X += bar_width
    plt.xlabel("Google Search Depth", fontsize=15)
    plt.ylabel("Number of %sterms" % ylab, fontsize=15) 
    plt.title(d, fontsize=18)
    if "manual label" in df.columns:
        if broad:
            ax.legend(labels=['True','False'], prop={"size":15})
        else:
            ax.legend(labels=['True','?','False'], prop={"size":15})
    plt.xticks(np.arange(0, bar_width * max(df["Google depth"]), bar_width), range(1, max(df["Google depth"] + 1)))
    plt.savefig(fname, dpi=300, bbox_inches = "tight")
    plt.clf()


# creates a histogram of term generation frequency vs. number of terms
# generated at that frequency
#
# params:
# df (DataFrame) - output of pipeline run with manual labels
# plotdir (str) - directory in which to save output image
# cap (int) - cap for x axis (excluding outliers for prettier plotting)
#             setting this to -1 means there is no cap
# broad (bool) - flag for considering broad terms (terms that refer to the
#                specified drug but also other drugs, e.g. benzo) as True
# namefilter (bool) - flag for whether to remove terms that don't pass the
#                     drug name filter before plotting
# googlefilter (bool) - flag for whether to remove terms that don't pass the
#                       Google search filter before plotting  
def freq_bar(df, plotdir, cap=-1, broad=False, namefilter=False, googlefilter=False):
    # helper function. returns the number of terms with a given label that occur
    # with the given frequency. if there is an x axis cap, then the bar at that
    # cap will account for all terms occuring at that frequency and more frequently.
    #
    # params:
    # l (list) - list of frequencies for all terms of a given manual label
    # i (int) - which frequency to provide count for
    def count(l, i):
        if cap > 0 and i == cap:
            total = 0
            for j in range(i, max(l) + 1):
                total += l.count(j)
            return total 
        else:
            return l.count(i)

    if type(cap) == type(None):
        cap = -1

    if googlefilter:
        df = df.loc[df["Google"]]

    true_freqs = []
    false_freqs = []
    truish_freqs = []
    freqs = []
    n_true_ones = 0
    n_false_ones = 0
    for term in df["GPT-3 term"].unique():
        subdf = df.loc[df["GPT-3 term"] == term]
        if len(subdf) == 0:
            continue
        n = len(subdf)
        if "manual label" in df.columns:
            if subdf["manual label"].tolist()[0] == "True":
                true_freqs.append(n)
                if n == 1: n_true_ones += 1
            elif subdf["manual label"].tolist()[0] == "False":
                false_freqs.append(n)
                if n == 1: n_false_ones += 1
            elif subdf["manual label"].tolist()[0] == "?":
                truish_freqs.append(n)
                if n == 1: n_true_ones += 1
        else:
            freqs.append(n)

    fig, ax = plt.subplots()
    fname = os.path.join(plotdir, "regoogle_freq_bar.png")
    if broad:
        fname = fname[:-4] + "_broad.png"
    if namefilter:
        fname = fname[:-4] + "_namefilter.png"
    if googlefilter:
        fname = fname[:-4] + "_googlefilter.png"
    bar_width = 50
    X = 0
    if len(freqs) > 0:
        maxn = max(freqs)
    elif broad:
        maxn = max(max(true_freqs), max(false_freqs))
    else:
        maxn = max(max(true_freqs), max(false_freqs), max(truish_freqs))
    if cap > 0:
        maxn = min(maxn, cap)

    for i in range(1, maxn + 1):
        if "manual label" in df.columns:
            ax.bar(X, count(true_freqs,i) + count(false_freqs,i) + count(truish_freqs,i), width=bar_width, color=COLOR_DICT["True"])
            if not broad:
                ax.bar(X, count(false_freqs,i) + count(truish_freqs,i), width=bar_width, color=COLOR_DICT["?"])
            ax.bar(X, count(false_freqs,i), width=bar_width, color=COLOR_DICT["False"])
        else:
            ax.bar(X, count(freqs,i), width=bar_width, color=COLOR_DICT["Unknown"])
        X += bar_width
    plt.xlabel("Number of times generated by GPT-3", fontsize=15)
    plt.ylabel("Number of terms (log scale)", fontsize=15) 
    plt.yscale("log")
    plt.title(d, fontsize=18)
    if "manual label" in df.columns:
        if broad:
            ax.legend(labels=['True','False'], prop={"size":15})
        else:
            ax.legend(labels=['True','?','False'], prop={"size":15})
    plt.xticks(np.arange(0, bar_width * maxn, bar_width * 15), range(1, maxn + 1 , 15))
    plt.savefig(fname, dpi=300, bbox_inches = "tight")
    plt.clf()


# creates np array version of confusion matrix
# precursor step to creating the actual plot
# must assign predicted and real labels first
#
# params:
# df (DataFrame) - output of pipeline run with manual labels and predicted
#                  labels
def confusion_matrix(df):
    df["tn"] = df.apply(lambda row: not row["pred"] and not row["real"], axis=1)
    df["fp"] = df.apply(lambda row: row["pred"] and not row["real"], axis=1)
    df["fn"] = df.apply(lambda row: not row["pred"] and row["real"], axis=1)
    df["tp"] = df.apply(lambda row: row["pred"] and row["real"], axis=1)
    tn = len(df.loc[df["tn"]])
    fp = len(df.loc[df["fp"]])
    fn = len(df.loc[df["fn"]])
    tp = len(df.loc[df["tp"]])
    return np.array([[tn, fp],[fn, tp]])


# plots a confusion matrix using sklearn functions
# must assign predicted and real labels first
#
# params:
# df (DataFrame) - output of pipeline run with manual labels and predicted
#                  labels
# plotdir (str) - directory in which to save output image
# fname (str) - filename of output image
# title (str) - title to put on plot
def save_cm_plot(df, plotdir, fname, title):
    cm = confusion_matrix(df)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm)
    plt.rcParams.update({'font.size': 20})
    disp.plot(im_kw={"vmin": 0, "vmax": 1100})
    plt.title(title)
    plt.savefig(os.path.join(plotdir, fname), bbox_inches="tight")
    plt.clf()


# creates several different confusion matrices using different ways to
# classify gpt-3 generated terms as "true" (i.e. as gpt-3 synonyms).
# plots are saved in separate files.
#
# params:
# df (DataFrame) - output of pipeline run with manual labels
# plotdir (str) - directory in which to save output images
def make_all_cms(df, plotdir):
    fname = "regoogle_cm_"
    freq_cutoff = 1

    # put frequency information into  df before dropping duplicates
    df["freq"] = df.apply(lambda row: df["GPT-3 term"].value_counts()[row["GPT-3 term"]], axis=1)

    df.drop_duplicates(subset=["GPT-3 term"], inplace=True)
    df["real"] = df.apply(lambda row: row["manual label"] == "True" or row["manual label"] == "?", axis=1) # allows broad terms -- change if you want higher specificity!

    if not "filtered name" in df.columns:
        df = drugname_filter(df)
    
    # using google depth 10 to classify gpt3 results
    # also uses drug name filter
    if "filter prediction" in df.columns:
        df["pred"] = df["filter prediction"]
    else:
        df["pred"] = df.apply(lambda row: row["Google depth"] > 0 and row["Google depth"] <= 10 and not row["filtered name"], axis=1)
    save_cm_plot(df, plotdir, fname + "all_google_10_true.png", "Confusion Matrix when all terms passing any Google filter with depth 10 are predicted True")
    
    # only using drug name filter to classify gpt3 results
    df["pred"] = df.apply(lambda row: not row["filtered name"], axis=1)
    save_cm_plot(df, plotdir, fname + "drugname_only_true.png", "Confusion Matrix when all terms passing drugname filter are predicted True")
    
    # using frequency + drug name filter
    df["pred"] = df.apply(lambda row: row["freq"] > freq_cutoff and not row["filtered name"], axis=1)
    save_cm_plot(df, plotdir, fname + "freq%d_true.png" % freq_cutoff, "Confusion Matrix when all terms with frequency %d and passing name filter are predicted True" % freq_cutoff)

    # using frequency + drug name filter + google
    if "filter prediction" in df.columns:
        df["pred"] = df.apply(lambda row: row["filter prediction"] and row["freq"] > freq_cutoff, axis=1)
    else:
        df["pred"] = df.apply(lambda row: row["Google depth"] > 0 and row["Google depth"] <= 10 and not row["filtered name"] and row["freq"] > freq_cutoff, axis=1)
    save_cm_plot(df, plotdir, fname + "all_google_10_name_freq%d_true.png" % freq_cutoff, "Confusion Matrix when all terms passing any Google filter with depth 10 and name and freq filters are predicted True")
    
    # blindly all taking gpt3 results as true
    df["pred"] = True * len(df)
    save_cm_plot(df, plotdir, fname + "gpt3_true.png", "Confusion Matrix when all GPT-3 generated terms are predicted True")

    # using redmed to classify gpt3 results
    df["pred"] = df.apply(lambda row: row["Seed of GPT-3 term in RedMed"] == row["seed for prompt"], axis=1)
    save_cm_plot(df, plotdir, fname + "redmed_true.png", "Confusion Matrix when all terms present in RedMed are predicted True")
    


# label or drop proposed terms that match a known drug name
#
# params:
# df (DataFrame) - output of pipeline run
# drop (bool) - whether to drop rows that don't pass drug name filter (versus
#               adding a False label in the "filtered name" column being created
def drugname_filter(df, drop=False):
    redmed = pd.read_csv("redmed_lexicon.tsv",sep="\t")
    df["filtered name"] = df.apply(lambda row: row["GPT-3 term"] in redmed["drug"].tolist() and not row["GPT-3 term"] == row["seed for prompt"], axis=1)
    if drop:
        df = df.loc[df["filtered name"] == False]
    return df


def main(args):
    df = pd.read_csv(args.f, index_col=0)
    df = df.loc[df["seed for prompt"] == args.seed]
    if args.broad:
        df["manual label"] = df.apply(lambda row: "True" if row["manual label"] == "?" else row["manual label"], axis=1)
    if args.namefilter:
        drop = args.plot != "cm"
        if "name filter" in df.columns:
            if drop:
                df = df.loc[df["name filter"]]
        else:
            df = drugname_filter(df, drop=drop)

    if args.plot == "depth":
        depths_bar(df, args.plotdir, uniq=args.uniq, broad=args.broad, namefilter=args.namefilter)
    elif args.plot == "freq":
        freq_bar(df, args.plotdir, cap=args.cap, broad=args.broad, namefilter=args.namefilter, googlefilter=args.googlefilter)
    elif args.plot == "cm":
       make_all_cms(df, args.plotdir) 


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', type=str, help="input filename")
    parser.add_argument('--seed', type=str, help="index term (seed term)")
    parser.add_argument('--plotdir', type=str, help="directory in which to save plots")
    parser.add_argument('--plot', type=str, help="what data to plot (depth, frequency, or confusion matrix)")
    parser.add_argument('--uniq', action="store_true", help="flag for only accounting for each unique term once")
    parser.add_argument('--cap', type=int, help="x axis cap")
    parser.add_argument('--broad', action="store_true", help="flag for counting broad terms (e.g. \"optiates\", \"sedatives\", etc.) as true positives instead of \"?\"")
    parser.add_argument('--namefilter', action="store_true", help="flag for filtering out generated terms that are in the redmed drug name list")
    parser.add_argument('--googlefilter', action="store_true", help="flag for filtering out generated terms that do not pass the google filter")
    args = parser.parse_args()
    main(args)
