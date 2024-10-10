# mdsoar-utilities

**This repository contains files for collecting and processing downlaod and page view statsitics from MD-SOAR and related projects.**

**-Collect_download_statistics.py :**

This code retrieves and processes download statistics for specific items from a Solr server based on a given time range. It maps campus names to their corresponding identifiers, queries for records within the specified time frame, and counts the downloads for each item. The script then creates separate CSV files for each campus, containing unique entries of item IDs, titles, URLs, campuses, and download counts, while ensuring no duplicates are written. It handles potential missing data and outputs a message upon successful completion.

Example Usage: 
python3 Collect_download_statistics.py "2022-05-20T00:00:00Z" "2022-05-21T00:00:00Z"


**-Collect_all_unique_handles.py**
This script compiles a list of items with unique handles from a Solr database into a CSV file.

Usage:
python3 collect_all_unique_handles.py


**-Campus_mapping.py**

This code reads data from three CSV files to create a consolidated output CSV. It cleans and processes the Page path and screen class column, matches it with unique handles and location data, and maps these to corresponding campus names based on UUIDs. The final output includes the original page path, view counts, and matched campus names, stored in a new output CSV file.

Note: This code uses the mdsoar-stats.csv file from Google Analytics, as well as the output of the Collect_all_unique_handles.py file as well as the campusuuidlist.csv file. 

Usage: python3 Campus_mapping.py
