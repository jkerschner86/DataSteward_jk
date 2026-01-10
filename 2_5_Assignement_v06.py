"""
=============================================================================
FINAL PROJECT: PHAIDRA DATA AUDITOR
=============================================================================
WHAT IS THIS?
This script is like a digital detective. It:
1. Asks you for dates and makes sure you don't type nonsense.
2. Calls the Phaidra library (API) to see what files they have.
3. Sorts those files into "Open Access" (Free) and "Restricted" (Private).
4. Saves everything into Excel files (CSV) and draws pictures (PNG).
=============================================================================
"""

import requests   # Used to "call" the Phaidra website
import json       # Used to save data in a "list" format
import matplotlib.pyplot as plt  # Used to draw the charts
import csv        # Used to create Excel-friendly files
import numpy as np # Used to help position the bars in the chart

# ---------------------------------------------------------------------------
# PHASE 1: THE HARVESTER (Getting the data from the internet)
# ---------------------------------------------------------------------------

def fetch_all_phaidra_data(start_year, end_year, filename="phaidra_audit.json"):
    # The 'URL' is the address of the Phaidra search engine
    base_url = "https://phaidra.ustp.at/api/search/select"
    all_docs = [] # This is our "bucket" where we will put all the records
    start = 0     # We start at the very first record
    
    # We create a "Search Query" (Instructions for the website)
    # We tell it: "Look for things created between January 1st of StartYear and Dec 31st of EndYear"
    query_string = f"created:[{start_year}-01-01T00:00:00Z TO {end_year}-12-31T23:59:59Z]"
    
    try:
        # STEP 1: The 'Handshake' (Asking how much work we have to do)
        handshake_params = {'q': query_string, 'wt': 'json', 'rows': 0}
        response = requests.get(base_url, params=handshake_params, timeout=10)
        
        # We look inside the answer to find 'numFound' (The total number of objects)
        total_found = response.json().get('response', {}).get('numFound', 0)
        
        if total_found == 0:
            print(f"\n[!] No objects found for the period {start_year}-{end_year}.")
            return False

        print(f"\n[OK] Found {total_found} objects. Starting the download...")

        # STEP 2: The 'Pagination' (Going back and forth to get data in small chunks)
        # We fetch 100 items at a time so the website doesn't crash.
        
        while start < total_found:
            params = {
                'q': query_string,
                'fl': 'pid,dc_license,file_mimetype,dc_format', 
                'wt': 'json',
                'start': start,   # This tells the website which 'page' we are on
                'rows': 100       # This tells it to give us 100 items per page
            }
            page_res = requests.get(base_url, params=params, timeout=15)
            docs = page_res.json().get('response', {}).get('docs', [])
            
            # Put the 100 items into our big "bucket"
            all_docs.extend(docs)
            start += 100 # Move the pointer forward to the next page
            print(f"    Downloaded: {len(all_docs)} / {total_found}")

        # STEP 3: The 'Safety Save' (Writing the bucket into a file on your computer)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({"response": {"docs": all_docs}}, f)
        return True

    except Exception as e:
        print(f"ERROR: Something went wrong with the internet! {e}")
        return False

# ---------------------------------------------------------------------------
# PHASE 2: THE ANALYZER (Sorting and Cleaning the data)
# ---------------------------------------------------------------------------

def analyze_and_export(filename="phaidra_audit.json"):
    # Open the file we saved earlier
    with open(filename, 'r', encoding='utf-8') as f:
        content = json.load(f)
    
    docs = content.get('response', {}).get('docs', [])
    detailed_list = [] # For the giant Excel list
    stats = {}         # For the summary table and charts
    
    # These are the "magic words" that tell us a file is free to use (Open Access)
    open_keywords = ['cc-by', 'creative commons', 'public domain', 'open-access', 'cc0']

    for item in docs:
        # --- THE FALLBACK (Finding the file type) ---
        # If 'mimetype' is empty, we look at 'dc_format'. If that's empty, we say 'Unknown'.
        raw_format = item.get('file_mimetype') or item.get('dc_format') or 'Unknown'
        raw_lic = item.get('dc_license', 'All Rights Reserved')
        
        # --- THE CLEANER (Fixing list errors) ---
        # Sometimes the data comes in like ['PDF']. We just want the word 'PDF'.
        mime = raw_format[0] if isinstance(raw_format, list) else raw_format
        lic = raw_lic[0] if isinstance(raw_lic, list) else raw_lic

        # Save this row for our giant CSV list
        detailed_list.append({'PID': item.get('pid'), 'Format': mime, 'License': lic})

        # --- THE CATEGORIZER (Open vs Restricted) ---
        if mime not in stats:
            stats[mime] = {'Total': 0, 'Open': 0, 'Restricted': 0}
        
        stats[mime]['Total'] += 1
        
        # We check if any of our "magic open words" are in the license text
        is_open = any(key in lic.lower() for key in open_keywords)
        if is_open:
            stats[mime]['Open'] += 1
        else:
            stats[mime]['Restricted'] += 1

    # --- THE CLERK (Writing the CSV files) ---
    # CSV 1: Every single object found
    with open('phaidra_detailed_list.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['PID', 'Format', 'License'])
        writer.writeheader()
        writer.writerows(detailed_list)

    # CSV 2: Summary of numbers
    with open('phaidra_summary_stats.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Format', 'Total', 'OpenAccess', 'Restricted'])
        for m, c in stats.items():
            writer.writerow([m, c['Total'], c['Open'], c['Restricted']])

    return stats

# ---------------------------------------------------------------------------
# PHASE 3: THE ARTIST (Drawing the PNG charts)
# ---------------------------------------------------------------------------

def plot_all_results(stats, start_y, end_y):
    if not stats: return
    mimes = list(stats.keys())
    
    # CHART 1: Total Volume
    totals = [stats[m]['Total'] for m in mimes]
    plt.figure(figsize=(10, 6))
    plt.bar(mimes, totals, color='skyblue')
    plt.title(f'Total Files Found ({start_y}-{end_y})')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('report_totals.png')
    plt.show()

    # CHART 2: Side-by-Side Comparison (Open vs Restricted)
    
    x = np.arange(len(mimes))
    width = 0.35
    plt.figure(figsize=(12, 7))
    plt.bar(x - width/2, [stats[m]['Open'] for m in mimes], width, label='Open Access', color='seagreen')
    plt.bar(x + width/2, [stats[m]['Restricted'] for m in mimes], width, label='Restricted', color='indianred')
    plt.title(f'Legal Status Comparison ({start_y}-{end_y})')
    plt.xticks(x, mimes, rotation=45, ha='right')
    plt.legend()
    plt.tight_layout()
    plt.savefig('report_licenses.png')
    plt.show()

# ---------------------------------------------------------------------------
# MAIN WORKFLOW (The "Engine" that runs everything)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("="*45)
    print("   PHAIDRA DATA STEWARD AUDIT TOOL")
    print("="*45)
    
    # LOOP: Keep asking until the user gives a valid START year
    
    while True:
        user_start = input("Step 1: Enter START year (2008 or later): ")
        if not user_start.isdigit(): # If it's not a number...
            print(f"'{user_start}' is not a year! Please type numbers only.")
        elif int(user_start) < 2008: # If it's a number but too small...
            print(f"Too old! Phaidra records only start in 2008.")
        else: # If it's perfect...
            break # Exit the waiting room

    # LOOP: Keep asking until the user gives a valid END year
    while True:
        user_end = input("Step 2: Enter END year: ")
        if not user_end.isdigit():
            print(f"'{user_end}' is not a year!")
        elif int(user_end) < int(user_start):
            print(f"The end year cannot be before the start year!")
        else:
            break
    
    # RUN THE PHASES:
    if fetch_all_phaidra_data(user_start, user_end):
        results = analyze_and_export()
        plot_all_results(results, user_start, user_end)
        
        print("\n" + "-"*45)
        print("ALL DONE! Check your folder for:")
        print("1. phaidra_detailed_list.csv (Excel List)")
        print("2. report_totals.png (Chart 1)")
        print("3. report_licenses.png (Chart 2)")
        print("-" * 45)