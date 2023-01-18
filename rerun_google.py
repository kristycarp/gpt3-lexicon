# this script allows for rerunning the Google filter without making new queries
# to GPT-3. main use case for this is if initial Googling returned errors due to
# daily query limits, or if the user decides to changed the definition of 
# the Google filter (e.g. to which depth to filter to)

import pandas as pd
import argparse
import redmed_gpt
from tqdm import tqdm
import pickle


# creates an entirely new DataFrame with the re-Googled results
#
# params:
# args (argparse.Namespace) - command line args
# small (bool) - flag to create small version of df for testing purposes
#                will only create a new df with a max of 30 rows
def make_df(args, small=False):
    try:
        memo = pickle.load(open(args.memo,"rb"))
    except:
        memo = dict()

    df = pd.read_csv(args.f, index_col=0)

    results = []
    added = []
    depths = []

    if small:
        counter = 0
    for _, row in tqdm(df.iterrows()):
        if small:
            if counter == 30:
                break
            else:
                counter += 1
        for google_add in ["", " pill", " drug", " slang"]:
            google, depth, memo = redmed_gpt.in_google_search(row["GPT-3 term"] + google_add, row["seed for prompt"], memo, depth=args.depth)
            if google == True:
                break
        if google != True:
            google_add = None

        results.append(google)
        added.append(google_add)
        depths.append(depth)
        
    pickle.dump(memo, open(args.memo, "wb"))
    
    df = df.drop(labels=["GPT-3 term in Google","GPT-3 term + pill in Google"],axis=1)
    if small:
        df = df.head(30)
    df["Google"] = results
    df["Google added token"] = added
    df["Google depth"] = depths
    df.to_csv(args.f.split("/")[-1][:-4] + args.suffix + ".csv")


# reruns Google search and updates the pipeline-created csv with an additional
# column that has the new Google information
#
# params:
# args (argparse.Namespace) - command line args
def update_df(args):
    api_count = args.count_start
    try:
        memo = pickle.load(open(args.memo,"rb"))
    except:
        memo = dict()

    df = pd.read_csv(args.f, index_col=0)
    updates = []

    if "Google" in df.columns:
        google_col = "Google"
        added_col = "Google added token"
        keeps_depth = True
    else:
        google_col = "GPT-3 term in Google"
        added_col = "token added to Google"
        keeps_depth = False

    for idx, row in tqdm(df.iterrows()):
        try:
            if row[google_col] != "Error" and not "_" in row["GPT-3 term"]:
                continue
        except:
            continue

        ud = dict()
        ud["idx"] = idx

        for google_add in ["", " pill", " drug", " slang"]:
            google, depth, memo, googled = redmed_gpt.in_google_search(str(row["GPT-3 term"]) + google_add, row["seed for prompt"], memo, depth=args.depth, count=True, offline=args.offline)
            if googled:
                api_count += 1
            if google == True:
                break
        if google != True:
            google_add = None

        ud[google_col] = google
        ud[added_col] = google_add
        if keeps_depth:
            ud["Google depth"] = depth
        updates.append(ud)

        if api_count >= 10000:
            print("Search API query quota exceeded. Exiting...")
            break

    for ud in updates:
        df.at[ud["idx"], google_col] = ud[google_col]
        df.at[ud["idx"], added_col] = ud[added_col]
        if keeps_depth:
            df.at[ud["idx"], "Google depth"] = ud["Google depth"]

    pickle.dump(memo, open(args.memo, "wb"))
    df.to_csv(args.f)
    print(api_count)


def main(args):
    update_df(args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', type=str, help="file of gpt3 outputs on which to rerun google")
    parser.add_argument('--memo', type=str, help="memo file name to reduce API requests", default="memo.p")
    parser.add_argument('--depth', type=int, help="how deep to go for google search filter", default=10)
    parser.add_argument('--suffix', type=str, help="suffix to append to new filename")
    parser.add_argument('--count_start', type=int, help="current Google Search API query count for the day", default=0)
    parser.add_argument('--offline', action="store_true", help="Flag to not use Google API, only memoized results")
    args = parser.parse_args()

    main(args)
