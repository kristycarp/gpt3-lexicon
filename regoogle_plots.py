import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import argparse
import os
from sklearn.metrics import ConfusionMatrixDisplay


COLOR_DICT = {"True": "deepskyblue", "False": "firebrick", "Unknown": "dimgray", "?": "lemonchiffon"}


# i want to make a bar plot with the different google depths
# colored by whether the term was true or false
def depths_bar(df, d, uniq=True, broad=False, namefilter=False):
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

    fname = os.path.join("plots", d, "regoogle_depth_bar_%s.png" % ylab.strip())
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
    # plt.xticks(np.arange(0, bar_width * max(df["Google depth"]), bar_width * 3), range(1, max(df["Google depth"]) , 3))
    plt.xticks(np.arange(0, bar_width * max(df["Google depth"]), bar_width), range(1, max(df["Google depth"] + 1)))
    plt.savefig(fname, dpi=300, bbox_inches = "tight")
    plt.clf()


def depths_prop(df, d, uniq=True):
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

    fname = os.path.join("plots", d, "regoogle_depth_prop_%s.png" % ylab.strip())
    bar_width = 5
    X = 0

    for i in range(1, max(df["Google depth"]) + 1):
        subdf = df.loc[df["Google depth"] == i]
        if "manual label" in df.columns:
            ax.bar(X, 1, width=bar_width, color=COLOR_DICT["False"])
            ax.bar(X, get_len(subdf.loc[subdf["manual label"] != "False"]) / get_len(subdf), width=bar_width, color=COLOR_DICT["?"])
            ax.bar(X, get_len(subdf.loc[subdf["manual label"] == "True"]) / get_len(subdf), width=bar_width, color=COLOR_DICT["True"])
        X += bar_width
    plt.xlabel("Google Search Depth")
    plt.ylabel("Proportion of %sterms" % ylab) 
    plt.title(d)
    ax.legend(labels=['False','?','True'])
    plt.xticks(np.arange(0, bar_width * max(df["Google depth"]), bar_width * 3), range(1, max(df["Google depth"]) , 3))
    plt.savefig(fname, dpi=300, bbox_inches = "tight")
    plt.clf()


# i also want to make a bar plot of the number of times a term appears
# colored by whether it is true or false
def freq_bar(df, d, cap=-1, broad=False, namefilter=False, googlefilter=False):
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
        if n > 46:
            print(term, str(n))
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
    fname = os.path.join("plots", d, "regoogle_freq_bar.png")
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

    print("number of true terms appearing once: %d" % n_true_ones)
    print("number of false terms appearing once: %d" % n_false_ones)


def freq_prop(df, d, cap=-1):
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

    true_freqs = []
    false_freqs = []
    truish_freqs = []
    for term in df["GPT-3 term"].unique():
        subdf = df.loc[df["GPT-3 term"] == term]
        n = len(subdf)
        if "manual label" in df.columns:
            if subdf["manual label"].tolist()[0] == "True":
                true_freqs.append(n)
            elif subdf["manual label"].tolist()[0] == "False":
                false_freqs.append(n)
            elif subdf["manual label"].tolist()[0] == "?":
                truish_freqs.append(n)

    fig, ax = plt.subplots()
    fname = os.path.join("plots", d, "regoogle_freq_prop.png")
    bar_width = 20
    X = 0
    maxn = max(max(true_freqs), max(false_freqs), max(truish_freqs))
    if cap > 0:
        maxn = min(maxn, cap)

    for i in range(1, maxn + 1):
        if "manual label" in df.columns and count(true_freqs,i) + count(truish_freqs,i) + count(false_freqs,i) != 0:
                ax.bar(X, 1, width=bar_width, color=COLOR_DICT["False"])
                ax.bar(X, (count(true_freqs,i) + count(truish_freqs,i)) / (count(true_freqs,i) + count(false_freqs,i) + count(truish_freqs,i)), width=bar_width, color=COLOR_DICT["?"])
                ax.bar(X, count(true_freqs,i) / (count(true_freqs,i) + count(truish_freqs,i) + count(false_freqs,i)), width=bar_width, color=COLOR_DICT["True"])
        X += bar_width
    plt.xlabel("Number of times generated by GPT-3")
    plt.ylabel("Proportion of terms") 
    plt.title(d)
    ax.legend(labels=['False','?','True'])
    plt.xticks(np.arange(0, bar_width * maxn, bar_width * 10), range(1, maxn + 1 , 10))
    plt.savefig(fname, dpi=300, bbox_inches = "tight")
    plt.clf()


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


def save_cm_plot(df, d, fname, title):
    cm = confusion_matrix(df)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm)
    plt.rcParams.update({'font.size': 20})
    disp.plot(im_kw={"vmin": 0, "vmax": 1100})
    plt.title(title)
    plt.savefig(os.path.join("plots", d, fname), bbox_inches="tight")
    plt.clf()


def make_all_cms(df, d):
    fname = "regoogle_cm_"
    freq_cutoff = 1

    # put frequency information into  df before dropping duplicates
    df["freq"] = df.apply(lambda row: df["GPT-3 term"].value_counts()[row["GPT-3 term"]], axis=1)

    df.drop_duplicates(subset=["GPT-3 term"], inplace=True)
    df["real"] = df.apply(lambda row: row["manual label"] == "True" or row["manual label"] == "?", axis=1) # MAY WANT TO CHANGE THIS LATER

    if not "filtered name" in df.columns:
        df = drugname_filter(df)
    

    # using google depth 10 to classify gpt3 results
    # also uses drug name filter
    if "filter prediction" in df.columns:
        df["pred"] = df["filter prediction"]
    else:
        df["pred"] = df.apply(lambda row: row["Google depth"] > 0 and row["Google depth"] <= 10 and not row["filtered name"], axis=1)
    save_cm_plot(df, d, fname + "all_google_10_true.png", "Confusion Matrix when all terms passing any Google filter with depth 10 are predicted True")

    # using frequency + drug name filter
    df["pred"] = df.apply(lambda row: row["freq"] > freq_cutoff and not row["filtered name"], axis=1)
    save_cm_plot(df, d, fname + "freq%d_true.png" % freq_cutoff, "Confusion Matrix when all terms with frequency %d and passing name filter are predicted True" % freq_cutoff)

    # using frequency + drug name filter + google
    if "filter prediction" in df.columns:
        df["pred"] = df.apply(lambda row: row["filter prediction"] and row["freq"] > freq_cutoff, axis=1)
    else:
        df["pred"] = df.apply(lambda row: row["Google depth"] > 0 and row["Google depth"] <= 10 and not row["filtered name"] and row["freq"] > freq_cutoff, axis=1)
    save_cm_plot(df, d, fname + "all_google_10_name_freq%d_true.png" % freq_cutoff, "Confusion Matrix when all terms passing any Google filter with depth 10 and name and freq filters are predicted True")
    

    # blindly all taking gpt3 results as true
    df["pred"] = True * len(df)
    save_cm_plot(df, d, fname + "gpt3_true.png", "Confusion Matrix when all GPT-3 generated terms are predicted True")

    # using redmed to classify gpt3 results
    df["pred"] = df.apply(lambda row: row["Seed of GPT-3 term in RedMed"] == row["seed for prompt"], axis=1)
    save_cm_plot(df, d, fname + "redmed_true.png", "Confusion Matrix when all terms present in RedMed are predicted True")
    '''
    # using google depth 30 to classify gpt3 results
    df["pred"] = df.apply(lambda row: row["Google depth"] > 0 and row["Google depth"] <= 30, axis=1)
    save_cm_plot(df, d, fname + "all_google_30_true.png", "Confusion Matrix when all terms passing any Google filter with depth 30 are predicted True")

    # using google depth 9 to classify gpt3 results
    df["pred"] = df.apply(lambda row: row["Google depth"] > 0 and row["Google depth"] <= 10, axis=1)
    save_cm_plot(df, d, fname + "all_google_10_true.png", "Confusion Matrix when all terms passing any Google filter with depth 9 are predicted True")

    # using solo google depth 30 to classify gpt3 results
    df["pred"] = df.apply(lambda row: row["Google depth"] > 0 and row["Google depth"] <= 30 and type(row["Google added token"]) == float, axis=1)
    save_cm_plot(df, d, fname + "solo_google_30_true.png", "Confusion Matrix when all terms passing solo Google filter with depth 30 are predicted True")

    # using solo google depth 9 to classify gpt3 results
    df["pred"] = df.apply(lambda row: row["Google depth"] > 0 and row["Google depth"] <= 9 and type(row["Google added token"]) == float, axis=1)
    save_cm_plot(df, d, fname + "solo_google_9_true.png", "Confusion Matrix when all terms passing solo Google filter with depth 9 are predicted True")

    # using solo + pill google depth 30 to classify gpt3 results
    df["pred"] = df.apply(lambda row: row["Google depth"] > 0 and row["Google depth"] <= 30 and (type(row["Google added token"]) == float or row["Google added token"] == " pill"), axis=1)
    save_cm_plot(df, d, fname + "solo_pill_google_30_true.png", "Confusion Matrix when all terms passing solo or \"pill\" Google filter with depth 30 are predicted True")

    # using solo + pill google depth 9 to classify gpt3 results
    df["pred"] = df.apply(lambda row: row["Google depth"] > 0 and row["Google depth"] <= 9 and (type(row["Google added token"]) == float or row["Google added token"] == " pill"), axis=1)
    save_cm_plot(df, d, fname + "solo_pill_google_9_true.png", "Confusion Matrix when all terms passing solo or \"pill\" Google filter with depth 9 are predicted True")

    # using solo + pill + drug google depth 30 to classify gpt3 results
    df["pred"] = df.apply(lambda row: row["Google depth"] > 0 and row["Google depth"] <= 30 and (type(row["Google added token"]) == float or row["Google added token"] == " pill" or row["Google added token"] == " drug"), axis=1)
    save_cm_plot(df, d, fname + "solo_pill_drug_google_30_true.png", "Confusion Matrix when all terms passing solo, \"pill\", or \"drug\" Google filters with depth 30 are predicted True")

    # using solo + pill + drug google depth 9 to classify gpt3 results
    df["pred"] = df.apply(lambda row: row["Google depth"] > 0 and row["Google depth"] <= 9 and (type(row["Google added token"]) == float or row["Google added token"] == " pill" or row["Google added token"] == " drug"), axis=1)
    save_cm_plot(df, d, fname + "solo_pill_drug_google_9_true.png", "Confusion Matrix when all terms passing solo, \"pill\", or \"drug\" Google filters with depth 9 are predicted True")
    '''

# label or drop proposed terms that match a known drug name
def drugname_filter(df, drop=False):
    print(len(df))
    redmed = pd.read_csv("redmed_lexicon.tsv",sep="\t")
    df["filtered name"] = df.apply(lambda row: row["GPT-3 term"] in redmed["drug"].tolist() and not row["GPT-3 term"] == row["seed for prompt"], axis=1)
    if drop:
        df = df.loc[df["filtered name"] == False]
    print(len(df))
    return df


def main(args):
    df = pd.read_csv(args.f, index_col=0)
    df = df.loc[df["seed for prompt"] == args.d]
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
        if args.type == "bar":
            depths_bar(df, args.d, uniq=args.uniq, broad=args.broad, namefilter=args.namefilter)
        elif args.type == "prop":
            depths_prop(df, args.d, args.uniq)
    elif args.plot == "freq":
        if args.type == "bar":
            freq_bar(df, args.d, cap=args.cap, broad=args.broad, namefilter=args.namefilter, googlefilter=args.googlefilter)
        elif args.type == "prop":
            freq_prop(df, args.d)
    elif args.plot == "cm":
       make_all_cms(df, args.d) 

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', type=str, help="input filename")
    parser.add_argument('-d', type=str, help="subdirectory of plots folder in which to put outputs")
    parser.add_argument('--plot', type=str, help="what data to plot (depth, frequency, or confusion matrix)")
    parser.add_argument('--type', type=str, help="type of plot to make (bar or proportion)")
    parser.add_argument('--uniq', action="store_true", help="flag for only accounting for each unique term once")
    parser.add_argument('--cap', type=int, help="x axis cap")
    parser.add_argument('--broad', action="store_true", help="flag for counting broad terms (e.g. \"optiates\", \"sedatives\", etc.) as true positives instead of \"?\"")
    parser.add_argument('--namefilter', action="store_true", help="flag for filtering out generated terms that are in the redmed drug name list")
    parser.add_argument('--googlefilter', action="store_true", help="flag for filtering out generated terms that do not pass the google filter")
    args = parser.parse_args()
    main(args)
