"""
PROGRAM: Phaidra Metadata & License Auditor (2023-2024)
PURPOSE: This program automates the auditing of repository objects to see 
         which file formats (MIME-types) use which licenses.
WATERFALL STAGE: Implementation
REQUIREMENTS MET: Loop, Decision, Library, Array/Dict, Diagram, File I/O, Interface.
"""

# [Requirement: Import at least one library]
import requests      # Used to talk to the Phaidra API (Web interaction)
import json          # Used to save and read metadata files (Data storage)
import matplotlib.pyplot as plt  # Used to create the visual audit report (Diagram)

#                                                                       --- PHASE 1: DATA ACQUISITION (Fetching data from the Repository) ---

def fetch_all_phaidra_data(filename="phaidra_audit.json"):
    """
    INTERFACE: filename (The name of the file we create)
    This function handles the 'Harvesting' part of Data Stewardship.
    It uses pagination to make sure we get EVERY object, not just a few.
    """
    base_url = "https://phaidra.ustp.at/api/search/select"
    all_docs = []    # [Requirement: Use at least one array/list]
    start = 0        # Starting point for pagination
    rows_per_page = 100 
    
    # [Requirement: At least one decision - implemented here as Try/Except]
    # I use Try/Except as a 'safety net' in case the internet or server fails.
    try:
        #                                   Step A: Ask the server "How many objects do you have for 2023-2024?"

        # I need to give the server "filters" / "instructions" of what he is supposed to deliver:
        # q         Query           Filters objects by creation date (2023-2024)
        # wt        Writer Type     Ensures data is returned in JSON format
        # rows      Rows	        Controls how many objects are sent in one go (chunk size); Page size
        # fl        Field List      Limits the data downloaded to only the fields relevant to the audit
        #                           "Data Minimization": Instead of downloading all of an objects metadata, I specify only the columns I need:
        #                           PID (unique ID), dc_license ( legal status), file_mimetype, dc_format
        # start	    Start	        Tells the API where to begin the next "page" of results
    
        handshake_params = {
            'q': 'created:[2023-01-01T00:00:00Z TO 2024-12-31T23:59:59Z]',
            'wt': 'json',
            'rows': 0   # 0 rows because we just want the 'numFound' count first.
                        # By setting rows to 0, I tell the server: "I don't want the actual data yet; just give me the metadata header which contains the 'numFound' (total count) value."
        }
        response = requests.get(base_url, params=handshake_params, timeout=10)
        response.raise_for_status() # Check if connection is OK
        
        total_found = response.json().get('response', {}).get('numFound', 0)
        print(f"STATUS: Found {total_found} total objects. Starting full download...")

        #                                   Step B: Harvesting /Pagination Loop

        # [Requirement: At least one loop is used]
        # Loop until every single record is parsed
        
        while start < total_found:
            params = {
                'q': 'created:[2023-01-01T00:00:00Z TO 2024-12-31T23:59:59Z]',
                'fl': 'pid,dc_license,file_mimetype,dc_format,resourcetype', 
                'wt': 'json',
                'start': start,
                'rows': rows_per_page
            }
            page_res = requests.get(base_url, params=params, timeout=15)
            page_res.raise_for_status()
            
            # Add this page of results to our main collection
            docs = page_res.json().get('response', {}).get('docs', [])
            all_docs.extend(docs)
            
            start += rows_per_page
            print(f"Downloading... {len(all_docs)} of {total_found} reached.")

        # [Requirement: Write to a file]
        # We save the raw data so we don't have to download it again if we restart.
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({"response": {"docs": all_docs}}, f)
        return True

    except Exception as error:
        print(f"CRITICAL ERROR: The data harvest failed. Reason: {error}")
        return False

# --- PHASE 2: DATA ANALYSIS (Cleaning and Sorting the metadata) ---

def analyze_data(filename="phaidra_audit.json"):
    """
    INTERFACE: filename (The file to read from)
    This function processes 'dirty' metadata and organizes it into a statistics table.
    """
    # [Requirement: Read data from a file]
    with open(filename, 'r', encoding='utf-8') as f:
        content = json.load(f)
    
    docs = content.get('response', {}).get('docs', [])
    stats_table = {} # Dictionary to store: {Format: {License: Count}}

    for item in docs:
        # DATA STEWARDSHIP LOGIC: Metadata Fallback
        # We check multiple fields to find the format, just in case one is empty.
        # [Requirement: Decision logic]
        raw_format = item.get('file_mimetype') or item.get('dc_format') or item.get('resourcetype') or 'Unknown Format'
        raw_license = item.get('dc_license', 'All Rights Reserved')
        
        # DATA CLEANING: Solve the 'List' vs 'String' issue
        # Sometimes Phaidra sends ['PDF'] instead of 'PDF'. We clean it here.
        clean_format = raw_format[0] if isinstance(raw_format, list) and raw_format else raw_format
        clean_license = raw_license[0] if isinstance(raw_license, list) and raw_license else raw_license

        # Organize the clean data into our statistics table
        if clean_format not in stats_table:
            stats_table[clean_format] = {}
        
        # Increment the count for this specific license
        stats_table[clean_format][clean_license] = stats_table[clean_format].get(clean_license, 0) + 1
            
    return stats_table

# --- PHASE 3: VISUALIZATION (Generating the Audit Report) ---

def plot_audit_report(stats):
    """
    Converts the analyzed data into a visual bar chart for the documentation.
    """
    if not stats: return

    # Prepare labels (MIME types) and total counts for the Y-axis
    formats = list(stats.keys())
    totals = [sum(license_counts.values()) for license_counts in stats.values()]

    # [Requirement: Make at least one diagram]
    plt.figure(figsize=(12, 7))
    plt.bar(formats, totals, color='forestgreen')
    
    # Labeling the chart for professional reporting
    plt.title('Phaidra Repository Audit: File Format Distribution (2023-2024)', fontsize=14)
    plt.xlabel('Metadata Format / MIME-type', fontsize=12)
    plt.ylabel('Number of Objects', fontsize=12)
    plt.xticks(rotation=45, ha='right') # Rotate text so it doesn't overlap
    
    plt.tight_layout()
    plt.savefig('phaidra_audit_chart.png') # Save diagram for the PDF report
    plt.show()

# --- MAIN WORKFLOW (Orchestrating the Waterfall model steps) ---

if __name__ == "__main__":
    # STEP 1: Harvest data from the Web to a File
    if fetch_all_phaidra_data():
        
        # STEP 2: Analyze and Clean the Data
        audit_results = analyze_data()
        
        # STEP 3: Verification (Print results to verify against Phaidra Web Dashboard)
        print("\n" + "="*40)
        print("VERIFICATION SUMMARY FOR DOCUMENTATION")
        print("="*40)
        for fmt, licenses in audit_results.items():
            total_for_this_type = sum(licenses.values())
            print(f"FORMAT: {fmt:25} | TOTAL: {total_for_this_type}")
        
        # STEP 4: Create the final Diagram
        plot_audit_report(audit_results)