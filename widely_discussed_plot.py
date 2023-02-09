# plots a histogram of number of reddit hits for controlled substances
# to aid the choice of cutoff for whether a drug is "widely discussed"
# used to create supplementary figure A1

import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os



def draw_quartile(percent, df, color="goldenrod", linestyle="solid"):
    quartile = df["hits"].quantile(percent/100)
    plt.axvline(quartile, color=color, linestyle=linestyle)


def main(fname, plotdir):
    df = pd.read_csv(fname, sep="\t")
    bins = np.logspace(start=np.log10(1), stop=np.log10(1900000))
    plt.hist(df["hits"], bins=bins, color="darkgray", edgecolor="black")
    draw_quartile(25, df, linestyle="dashed")
    draw_quartile(50, df)
    draw_quartile(75, df, linestyle="dashed")
    plt.gca().set_xscale("log")
    plt.xlabel("Number of Reddit hits")
    plt.ylabel("Number of drugs of abuse")
    plt.savefig(os.path.join(plotdir, "drug_hits_hist.png"))


if __name__ == "__main__":
    fname = "drugs_of_abuse_counts.tsv"
    plotdir = "plots"
    main(fname, plotdir)
