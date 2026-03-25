#!/usr/bin/env python3
import argparse
import csv
import os
import pandas as pd


def process_page_path(page_path):
    if pd.isna(page_path):
        return ""

    page_path = str(page_path)

    # Check if the path contains /handle/
    if "/handle/" in page_path:
        page_path = page_path.replace("/handle/", "").split(",")[0]

    # Check if the path starts with /items/, /communities/, or /collections/
    elif page_path.startswith(("/items/", "/communities/", "/collections/")):
        for prefix in ["/items/", "/communities/", "/collections/"]:
            if page_path.startswith(prefix):
                page_path = page_path.replace(prefix, "").split(",")[0]
                break

    # Remove trailing /full
    if page_path.endswith("/full"):
        page_path = page_path[:-len("/full")]

    return page_path.strip()


def generate_page_view_stats(file_a, file_b, campus_uuid_file, output_file):
    # Read CSV files
    df_a = pd.read_csv(file_a, dtype=str, keep_default_na=False)
    df_b = pd.read_csv(file_b, dtype=str, keep_default_na=False)
    campus_uuid_list = pd.read_csv(campus_uuid_file, dtype=str, keep_default_na=False)

    required_a = {"Page title and screen class", "Page path and screen class", "Views"}
    required_b = {"search.resourceid", "location.comm", "handle"}
    required_c = {"uuid", "campusName"}

    if not required_a.issubset(df_a.columns):
        raise ValueError(
            f"{file_a} is missing required columns. Found: {list(df_a.columns)}"
        )
    if not required_b.issubset(df_b.columns):
        raise ValueError(
            f"{file_b} is missing required columns. Found: {list(df_b.columns)}"
        )
    if not required_c.issubset(campus_uuid_list.columns):
        raise ValueError(
            f"{campus_uuid_file} is missing required columns. Found: {list(campus_uuid_list.columns)}"
        )

    uuid_to_campus = {
        row["uuid"]: row["campusName"]
        for _, row in campus_uuid_list.iterrows()
    }

    output_data = []

    for _, row_a in df_a.iterrows():
        page_path_processed = process_page_path(row_a["Page path and screen class"])

        matching_row_b = df_b[
            (df_b["handle"] == page_path_processed) |
            (df_b["search.resourceid"] == page_path_processed)
        ]

        if not matching_row_b.empty:
            location_comm_value = matching_row_b.iloc[0]["location.comm"]

            if pd.notna(location_comm_value) and isinstance(location_comm_value, str):
                location_comm = location_comm_value.split(",")
            else:
                location_comm = []

            campus_list = set()

            for comm_value in location_comm:
                comm_value_cleaned = comm_value.strip().strip("'[] ")
                if comm_value_cleaned in uuid_to_campus:
                    campus_list.add(uuid_to_campus[comm_value_cleaned])

            if page_path_processed in uuid_to_campus:
                campus_list.add(uuid_to_campus[page_path_processed])

            campus = ", ".join(sorted(campus_list)) if campus_list else ""
        else:
            campus = ""

        output_data.append({
            "Page title and screen class": row_a["Page title and screen class"],
            "Page path and screen class": row_a["Page path and screen class"],
            "Views": row_a["Views"],
            "Campus": campus
        })

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    output_columns = [
        "Page title and screen class",
        "Page path and screen class",
        "Views",
        "Campus"
    ]

    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=output_columns)
        writer.writeheader()
        writer.writerows(output_data)

    print(f"Output written to {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate page view statistics using preprocessed GA data and unique handles."
    )
    parser.add_argument("file_a", help="Preprocessed page views CSV from step 1")
    parser.add_argument("file_b", help="Unique handles CSV from step 2")
    parser.add_argument("campus_uuid_list", help="Path to campusuuidlist.csv")
    parser.add_argument(
        "-o", "--output",
        default="Monthy_Stats_Report/PageView_Statistics/PageView_Report.csv",
        help="Output CSV path"
    )

    args = parser.parse_args()
    generate_page_view_stats(args.file_a, args.file_b, args.campus_uuid_list, args.output)


if __name__ == "__main__":
    main()