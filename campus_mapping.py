import csv
import pandas as pd

# Read CSV files mdsoar-stats, all_unique_handles, and campus_uuid_list
file_a = pd.read_csv('data-export.csv')
file_b = pd.read_csv('all_items_unique_handles.csv')
campus_uuid_list = pd.read_csv('campusuuidlist.csv')

# Function to process 'Page path and screen class' column and match with file all_unique_handles
def process_page_path(page_path):
    # Check if the path starts with /handle/
    if '/handle/' in page_path:
        page_path = page_path.replace('/handle/', '').split(',')[0]
    # Check if the path starts with /items/, /communities/, or /collections/
    elif page_path.startswith(('/items/', '/communities/', '/collections/')):
        # Remove the specific prefix and keep the rest of the value
        for prefix in ['/items/', '/communities/', '/collections/']:
            if page_path.startswith(prefix):
                page_path = page_path.replace(prefix, '').split(',')[0]
                break

    # Check if the path ends with '/full' and remove it
    if page_path.endswith('/full'):
        page_path = page_path[:-len('/full')]  # Remove the '/full' substring

    return page_path

# Dictionary for fast lookup from campus_uuid_list
uuid_to_campus = {row['uuid']: row['campusName'] for _, row in campus_uuid_list.iterrows()}

# Initialize output data list
output_data = []

# Iterate through rows of file mdsoar-stats
for _, row_a in file_a.iterrows():
    page_path_processed = process_page_path(row_a['Page path and screen class'])
    
    # Find matching handle or resourceid in file all_unique_handles
    matching_row_b = file_b[(file_b['handle'] == page_path_processed) | (file_b['search.resourceid'] == page_path_processed)]

    if not matching_row_b.empty:
        location_comm_value = matching_row_b.iloc[0]['location.comm']

        # Ensure that location_comm is a string before splitting
        if pd.notna(location_comm_value) and isinstance(location_comm_value, str):
            location_comm = location_comm_value.split(',')
        else:
            location_comm = []

        campus_list = set()  # Use a set to store unique campus names

        # Match location.comm with campus_uuid_list and get corresponding campusName
        for comm_value in location_comm:
            # Clean comm_value by stripping whitespace and unwanted characters
            comm_value_cleaned = comm_value.strip().strip("'[] ")  # Remove extra quotes, brackets, and whitespace
            
            # Check if the cleaned value exists in uuid_to_campus
            if comm_value_cleaned in uuid_to_campus:
                campus_list.add(uuid_to_campus[comm_value_cleaned])  # Add matching campus to the set

        # If location_comm is empty but the value itself is present in uuid_to_campus
        if page_path_processed in uuid_to_campus:
            campus_list.add(uuid_to_campus[page_path_processed])

        campus = ', '.join(campus_list) if campus_list else ''  # Join all matching campuses or set empty
    else:
        campus = ''
    
    # Append the processed row to the output data
    output_data.append({
        'Page title and screen class': row_a['Page title and screen class'],  # Include 'Page title and screen class'
        'Page path and screen class': row_a['Page path and screen class'],
        'Views': row_a['Views'],
        'Campus': campus
    })

# Write output CSV file
output_file = 'Monthly-report.csv'
output_columns = ['Page title and screen class', 'Page path and screen class', 'Views', 'Campus']

with open(output_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=output_columns)
    writer.writeheader()
    writer.writerows(output_data)

print(f"Output written to {output_file}")
