# creates plots for use in comparing parameter settings
# use after analyze.py
# was used to create figures 2,3,4 in the accompanying manuscript

import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import argparse
import os


# for the specified params, create a box plot showing the aggregate
# of all pipeline runs with each setting of that param
# used to create figures 2 and 3 in the accompanying manuscript
def param_box_plot(df, col, param, d):
    if col == "all":
        cols = df.columns[7:]
    elif col == "uniq" or col == "terms":
        cols = [c for c in df.columns if col in c]
    else:
        cols = [col]
    if param == "all":
        params = ["temp","pres","freq","counter"]
    else:
        params = [param]

    for c in cols:
        for p in params:
            fname = os.path.join("plots", d, "param_box_%s_sep_by_%s.png" % (c, p))
            data = []
            vals = sorted(df[p].unique().tolist())
            for val in vals:
                temp = df.loc[df[p] == val]
                data.append(temp[c].tolist())
            fig, ax = plt.subplots()
            plt.ylabel(c)
            plt.xlabel(p)
            ax.boxplot(data, labels=vals)
            plt.savefig(fname)
            plt.clf()


# creates a bar plot showing each individual pipeline run with certain
# parameter settings. this allows for comparison of the whole set of parameters
# instead of just examining one at a time
# used for figure 4 of the accompanying manuscript
def top_model_bar_plot(df, col, param, d):
    color_dict = {"temp": {0: "white", 0.3: "white", 0.5: "white", 0.6: "white", 1: "gray"},
                  "freq": {0: "white", 0.3: "white", 0.5: "white", 0.6: "white", 1: "gray"},
                  "pres": {0: "white", 0.3: "white", 0.5: "white", 0.6: "white", 1: "gray"},
                  "counter": {True: "gray", False: "white"}}
    hatch_dict = {"temp": {0: '', 0.3: "//", 0.5: "xx", 0.6: "xxxx", 1: ""},
                  "freq": {0: '', 0.3: "//", 0.5: "xx", 0.6: "xxxx", 1: ""},
                  "pres": {0: '', 0.3: "//", 0.5: "xx", 0.6: "xxxx", 1: ""},
                  "counter": {True: "", False: ""}}

    if col == "all":
        cols = df.columns[7:]
    elif col == "uniq" or col == "terms":
        cols = [c for c in df.columns if col in c]
    else:
        cols = [col]
    if param == "all":
        params = ["temp","pres","freq","counter"]
    else:
        params = [param]

    for c in cols:
        for p in params:
            fname = os.path.join("plots", d, "top_model_bar_%s_color_by_%s.png" % (c, p))
            fig, ax = plt.subplots()
            bar_width=3
            X = 0
            plot_df = df.sort_values(c,ascending=False)
            labels = plot_df.apply(get_param_label, axis=1).tolist()
            in_legend = dict()
            for i in range(len(df)):
                color_key = plot_df[p].tolist()[i]
                color = color_dict[p][color_key]
                hatch = hatch_dict[p][color_key]
                fill = color == "gray"
                if color_key in in_legend.keys():
                    ax.bar(X, plot_df[c].tolist()[i], width=bar_width, color=color, edgecolor='black', fill=fill, hatch=hatch)
                else:
                    in_legend[color_key], = ax.bar(X, plot_df[c].tolist()[i], width=bar_width, color=color, edgecolor='black', fill=fill, hatch=hatch)
                X += bar_width
            plt.xlabel("Models")
            plt.ylabel(c)
            ax.legend(handles = in_legend.values(),
                      labels = in_legend.keys())
            plt.savefig(fname, dpi=300, bbox_inches="tight")
            plt.clf()


# returns nicely formatted labels for plotting
def get_param_label(row):
    return "temp=%.1f, freq=%.1f, pres=%.1f, counterexamples=%s" % (row["temp"], row["freq"], row["pres"], row["counter"])


def main(args):
    df = pd.read_csv(args.f, index_col=0)
    if args.plot == "bar":
        top_model_bar_plot(df, args.col, args.param, args.d)
    elif args.plot == "box":
        param_box_plot(df, args.col, args.param, args.d)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', type=str, help="input filename")
    parser.add_argument('--plotdir', type=str, help="directory in which to save plots")
    parser.add_argument('--plot', type=str, help="type of plot to make (bar or box)")
    parser.add_argument('--col', type=str, help="column to plot (all, uniq, terms, n_ungs, etc)")
    parser.add_argument('--param', type=str, help="column to color by (all, temp, pres, freq, or counter)")
    args = parser.parse_args()
    main(args)
