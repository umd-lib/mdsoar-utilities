#!/usr/bin/env python3
import subprocess
import argparse
import os


def run(cmd):
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_csv")
    parser.add_argument("campus")
    parser.add_argument("start")
    parser.add_argument("end")
    parser.add_argument("--label", required=True)
    args = parser.parse_args()

    pre = f"{args.label}_preprocessed.csv"
    handles = f"handles_{args.label}.csv"
    pageview_output = f"Monthy_Stats_Report/PageView_Statistics/{args.label}_PageView.csv"
    download_output = "Monthy_Stats_Report/Download_Statistics"

    os.makedirs("Monthy_Stats_Report/PageView_Statistics", exist_ok=True)
    os.makedirs("Monthy_Stats_Report/Download_Statistics", exist_ok=True)

    run(["python3", "Preprocessing.py", args.input_csv, "-o", pre])
    run(["python3", "CollectUniqueHandles.py", "-o", handles])
    run(["python3", "PageViewStats.py", pre, handles, args.campus, "-o", pageview_output])
    run(["python3", "DownloadStats.py", args.start, args.end, "-o", download_output])


if __name__ == "__main__":
    main()