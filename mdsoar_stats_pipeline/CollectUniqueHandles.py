#!/usr/bin/env python3
import argparse
import csv
import requests

def collect_unique_handles(search_url: str, output_filename: str):
    params = {'q': '*:*','fl': 'search.resourceid,location.comm,handle','indent': 'true','rows': '50000'}
    response = requests.get(search_url, params=params)
    data = response.json()
    records = data.get("response", {}).get("docs", [])
    unique_handles = set()
    with open(output_filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["search.resourceid", "location.comm", "handle"])
        for record in records:
            h = record.get("handle","N/A")
            if h not in unique_handles:
                writer.writerow([record.get("search.resourceid","N/A"), record.get("location.comm","N/A"), h])
                unique_handles.add(h)
    print("Handles collected")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o","--output",default="all_items_unique_handles.csv")
    parser.add_argument("--search-url",default="http://localhost:8983/solr/search/select")
    args = parser.parse_args()
    collect_unique_handles(args.search_url, args.output)

if __name__ == "__main__":
    main()
