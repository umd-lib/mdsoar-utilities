#!/usr/bin/env python3
import argparse
import csv
import os
from collections import defaultdict

import requests


CAMPUS_DICT = {
    "eScholarship@Frostburg": "e34f5843-e595-4050-9f20-3c730277abf8",
    "eScholarship@Goucher": "600e1739-8b79-4b3a-a63e-6e294122173e",
    "Hood College": "ed384ea7-4a06-4491-b7ef-f81aa1abdea4",
    "Loyola Notre Dame Library": "6083f1c5-cab2-4a29-94aa-48136b67f4e4",
    "eScholarship@Morgan": "2f4b286e-89fe-43d5-acd8-9b23d479e8f6",
    "SOAR@SU": "639afd57-c954-493d-8edd-df0a9cf4a0fd",
    "Stevenson Scholar Exchange @ Stevenson University": "f2db9a4e-700c-4245-95f0-e8279a94aba7",
    "SOAR @ SMCM": "641f2917-f4e7-4d07-8b84-a6191f83b4de",
    "ScholarWorks@Towson": "113328b5-9ee7-4830-990f-7dffc00104c5",
    "KnowledgeWorks@UBalt": "d0c2feef-ef35-4aac-a6a2-4824d746cda4",
    "ScholarWorks@UMBC": "b1076c89-bcbc-455c-b2df-ec2af2d813a2",
    "University of Maryland Eastern Shore": "6e7b8e59-1247-4bfe-8ec5-66017ea52a39"
}


def sanitize_filename(name: str) -> str:
    return (
        name.replace("/", "_")
            .replace(":", "-")
            .replace(" ", "_")
    )


def collect_download_statistics(time_start: str, time_end: str, output_dir: str) -> None:
    os.makedirs(output_dir, exist_ok=True)

    statistics_url = "http://localhost:8983/solr/statistics/select"
    search_url = "http://localhost:8983/solr/search/select"

    params = {
        "q": f'type:0 AND bundleName:ORIGINAL AND time:["{time_start}" TO "{time_end}"]',
        "fl": "uid,owningItem,owningComm",
        "q.op": "OR",
        "indent": "true",
        "rows": "10000"
    }

    response = requests.get(statistics_url, params=params, timeout=120)
    response.raise_for_status()
    data = response.json()

    if "response" not in data:
        print("No 'response' key found in the JSON. Check the returned data structure.")
        return

    records = data["response"]["docs"]

    # Count downloads per owningItem
    download_counts = {}
    for record in records:
        owning_item = record["owningItem"][0]
        download_counts[owning_item] = download_counts.get(owning_item, 0) + 1

    processed_items_per_campus = defaultdict(set)

    campus_files = {}
    campus_writers = {}

    try:
        # Open a separate CSV file for each campus
        for campus_key in CAMPUS_DICT.keys():
            safe_campus = sanitize_filename(campus_key)
            output_filename = os.path.join(
                output_dir,
                f"{safe_campus}_{sanitize_filename(time_start)}_{sanitize_filename(time_end)}.csv"
            )

            campus_file = open(output_filename, "w", newline="", encoding="utf-8")
            campus_writer = csv.writer(campus_file)
            campus_writer.writerow(["owningItem", "title", "url", "campus", "Download Count"])

            campus_files[campus_key] = campus_file
            campus_writers[campus_key] = campus_writer

        for record in records:
            owning_item = record["owningItem"][0]

            owning_comm_str = record.get("owningComm", [""])[0]
            owning_comm = owning_comm_str.split(",")

            campus = "N/A"
            matching_comm = "N/A"

            # Match any owningComm to a campus
            for comm in owning_comm:
                comm = comm.strip()
                for campus_key, campus_value in CAMPUS_DICT.items():
                    if comm == campus_value:
                        campus = campus_key
                        matching_comm = campus_value
                        break
                if matching_comm != "N/A":
                    break

            if campus == "N/A":
                continue

            # Only write one row per owningItem per campus
            if owning_item in processed_items_per_campus[campus]:
                continue

            processed_items_per_campus[campus].add(owning_item)

            # Query title from search core
            search_params = {
                "q": f"search.resourceid:{owning_item}",
                "fl": "search.resourceid,title",
                "indent": "true",
                "rows": "1"
            }
            search_response = requests.get(search_url, params=search_params, timeout=120).json()

            if (
                "response" in search_response
                and search_response["response"].get("numFound", 0) > 0
            ):
                search_record = search_response["response"]["docs"][0]
                item_title = search_record.get("title", "N/A")
            else:
                item_title = "N/A"

            url = f"http://mdsoar.org/items/{owning_item}"
            download_count = download_counts.get(owning_item, 0)

            campus_writers[campus].writerow([
                owning_item,
                item_title,
                url,
                campus,
                download_count
            ])

    finally:
        for campus_file in campus_files.values():
            campus_file.close()

    print(f"Separate CSV files have been created in: {output_dir}")


def main():
    parser = argparse.ArgumentParser(
        description="Collect per-campus download statistics for a given time range."
    )
    parser.add_argument("start", help='Start time, e.g. "2026-02-01T00:00:00Z"')
    parser.add_argument("end", help='End time, e.g. "2026-02-28T23:59:59Z"')
    parser.add_argument(
        "-o", "--output",
        default="Monthy_Stats_Report/Download_Statistics",
        help="Output directory for per-campus CSV files"
    )

    args = parser.parse_args()
    collect_download_statistics(args.start, args.end, args.output)


if __name__ == "__main__":
    main()