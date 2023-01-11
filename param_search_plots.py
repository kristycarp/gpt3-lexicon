import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import argparse
import os

# for each of the params, do a line plot of each of the metrics
# a different line for each of the other param combos
# or also do a version with averaging
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

# out of all models...
# which produces the most terms?
# which produces the most unique terms?
# which produces the most redmed terms?
# which produces the most google validated terms?
# which produces the most terms not in redmed and not validated by google?
# which produces the most terms not in redmed but validated by google?
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
    parser.add_argument('-d', type=str, help="subdirectory of plots folder in which to put outputs")
    parser.add_argument('--plot', type=str, help="type of plot to make")
    parser.add_argument('--col', type=str, help="column to plot")
    parser.add_argument('--param', type=str, help="column to color by")
    args = parser.parse_args()
    main(args)
