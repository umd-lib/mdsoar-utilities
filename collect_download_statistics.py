import requests
import sys
import csv
import pdb
from urllib.parse import urlencode
from collections import defaultdict

# Check if both start and end times are provided
if len(sys.argv) != 3:
    print("Usage: python3 get_statistics1.py <time_start> <time_end>")
    sys.exit(1)

time_start = sys.argv[1]
time_end = sys.argv[2]

# Dictionary of campus names and owningComm values
campus_dict = {
    'eScholarship@Frostburg': 'e34f5843-e595-4050-9f20-3c730277abf8',
    'eScholarship@Goucher': '600e1739-8b79-4b3a-a63e-6e294122173e',
    'Hood College': 'ed384ea7-4a06-4491-b7ef-f81aa1abdea4',
    'Loyola Notre Dame Library': '6083f1c5-cab2-4a29-94aa-48136b67f4e4',
    'eScholarship@Morgan': '2f4b286e-89fe-43d5-acd8-9b23d479e8f6',
    'SOAR@SU': '639afd57-c954-493d-8edd-df0a9cf4a0fd',
    'Stevenson Scholar Exchange @ Stevenson University': 'f2db9a4e-700c-4245-95f0-e8279a94aba7',
    'SOAR @ SMCM': '641f2917-f4e7-4d07-8b84-a6191f83b4de',
    'ScholarWorks@Towson': '113328b5-9ee7-4830-990f-7dffc00104c5',
    'KnowledgeWorks@UBalt': 'd0c2feef-ef35-4aac-a6a2-4824d746cda4',
    'ScholarWorks@UMBC': 'b1076c89-bcbc-455c-b2df-ec2af2d813a2',
    'University of Maryland Eastern Shore': '6e7b8e59-1247-4bfe-8ec5-66017ea52a39'
}

# First query to statistics core
params = {
    'q': f'type:0 AND bundleName:ORIGINAL AND time:["{time_start}" TO "{time_end}"]',
    'fl': 'uid,owningItem,owningComm',
    'q.op': 'OR',
    'indent': 'true',
    'rows': '10000'
}

statistics_url = "http://localhost:8983/solr/statistics/select"

r = requests.get(statistics_url, params=params)
jstuff = r.json()

# Dictionary to store download counts
download_counts = {}

# Dictionary to store unique owningItems for each campus
processed_items_per_campus = defaultdict(set)

if 'response' in jstuff:
    records = jstuff['response']['docs']

    # Calculate download counts
    for record in records:
        owning_item = record['owningItem'][0]
        if owning_item in download_counts:
            download_counts[owning_item] += 1
        else:
            download_counts[owning_item] = 1

    # Open a separate CSV file for each campus
    campus_files = {}
    campus_writers = {}

    # Prepare file writers for each campus
    for campus_key in campus_dict.keys():
        output_filename = f"{campus_key}_{time_start}_{time_end}.csv"
        campus_file = open(output_filename, 'w+', newline='')
        campus_writer = csv.writer(campus_file)
        campus_writer.writerow(['owningItem', 'title', 'url', 'campus', 'Download Count'])  # Updated header
        campus_files[campus_key] = campus_file
        campus_writers[campus_key] = campus_writer

    for record in records:
        owning_item = record['owningItem'][0]

        # Safely handle missing 'owningComm' field and split the string into individual values
        owning_comm_str = record.get('owningComm', [''])[0]
        owning_comm = owning_comm_str.split(',')  # Split by comma to get individual items

        campus = 'N/A'
        matching_comm = 'N/A'  # Default value if no match is found

        # Check if any item in owningComm matches the campus_dict values
        for comm in owning_comm:
            comm = comm.strip()  # Ensure no whitespace issues
            for campus_key, campus_value in campus_dict.items():
                if comm == campus_value:
                    campus = campus_key
                    matching_comm = campus_value  # Set matching_comm to the first found value
                    break
            if matching_comm != 'N/A':  # Break the outer loop as soon as a match is found
                break

        # Only proceed if the campus is found in the campus_dict
        if campus != 'N/A':
            # Skip duplicates within each campus
            if owning_item in processed_items_per_campus[campus]:
                continue
            processed_items_per_campus[campus].add(owning_item)  # Mark as processed for this campus

            # Second query to search core based on owningItem
            search_params = {
                'q': f'search.resourceid:{owning_item}',
                'fl': 'search.resourceid,title',  # Only need title now
                'indent': 'true',
                'rows': '1'
            }
            search_url = "http://localhost:8983/solr/search/select"
            search_response = requests.get(search_url, params=search_params).json()

            if 'response' in search_response and search_response['response']['numFound'] > 0:
                search_record = search_response['response']['docs'][0]
                item_title = search_record.get('title', 'N/A')
            else:
                item_title = 'N/A'

            # Create the URL
            url = f"http://mdsoar.org/items/{owning_item}"

            # Get the download count for the current owning_item
            download_count = download_counts.get(owning_item, 0)

            # Write to the corresponding campus CSV file
            campus_writers[campus].writerow([owning_item, item_title, url, campus, download_count])  # Removed owningComm

    # Close all the files
    for campus_file in campus_files.values():
        campus_file.close()

    print("Separate CSV files have been created for each campus.")
else:
    print("No 'response' key found in the JSON. Check the returned data structure.")
