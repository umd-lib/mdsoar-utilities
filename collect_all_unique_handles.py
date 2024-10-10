import requests
import csv
from urllib.parse import urlencode

# Solr search core URL
search_url = "http://localhost:8983/solr/search/select"

# Parameters for querying all items in the search core
params = {
    'q': '*:*',  # This fetches all items in the database
    'fl': 'search.resourceid,location.comm,handle',  # Specify the fields to retrieve
    'indent': 'true',
    'rows': '50000'  # Adjust the row limit based on the expected size of the database
}

# Make the request to Solr to retrieve all records
r = requests.get(search_url, params=params)
jstuff = r.json()

if 'response' in jstuff:
    records = jstuff['response']['docs']
    output_filename = "all_items_unique_handles.csv"
    
    # Set to track unique handles
    unique_handles = set()

    # Open the CSV file for writing
    with open(output_filename, 'w+', newline='') as csvfile:
        filewriter = csv.writer(csvfile)
        # Write the header row
        filewriter.writerow(['search.resourceid', 'location.comm', 'handle'])
        
        # Write data for each record, ensuring unique handles
        for record in records:
            resource_id = record.get('search.resourceid', 'N/A')
            location_comm = record.get('location.comm', 'N/A')
            handle = record.get('handle', 'N/A')
            
            # Only write the row if the handle is unique
            if handle not in unique_handles:
                filewriter.writerow([resource_id, location_comm, handle])
                unique_handles.add(handle)
    
    print(f"CSV file '{output_filename}' with unique handles has been created.")
else:
    print("No 'response' key found in the JSON. Check the returned data structure.")
