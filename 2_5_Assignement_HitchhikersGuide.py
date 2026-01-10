"""
=============================================================================
THE HITCHHIKER’S GUIDE TO THE PHAIDRA METADATA & LICENSE AUDITOR
=============================================================================
"DON'T PANIC" 
This script is essentially a Babel fish for Phaidra. It translates the 
infinite chaos of repository metadata into something mostly harmless.

1. It asks for dates (avoiding the poetry of Vogon bureaucrats).
2. It fetches data (without requiring a towel).
3. It sorts licenses (determining if data is truly 'Open' or just 'Restricted').
4. It provides the Ultimate Answer to Life, the Universe, and Audit Stats.
=============================================================================
"""

import requests   # The Sub-Etha Sens-O-Matic for calling the Phaidra API
import json       # A handy storage compartment for JSON data
import matplotlib.pyplot as plt  # To draw charts more beautiful than a Milliways sunset
import csv        # For people who still like digital paperwork
import numpy as np # Complex math for the Heart of Gold's navigation (and bar charts)

# ---------------------------------------------------------------------------
# PHASE 1: THE DATA HARVESTER (Mostly Harmless)
# ---------------------------------------------------------------------------

def fetch_all_phaidra_data(start_year, end_year, filename="phaidra_audit.json"):
    # The Sub-Etha command center (The API URL)
    base_url = "https://phaidra.ustp.at/api/search/select"
    all_docs = [] # Our digital Infinite Improbability Drive bucket
    start = 0     
    
    # Building the query (Essentially a polite request to the Deep Thought computer)
    query_string = f"created:[{start_year}-01-01T00:00:00Z TO {end_year}-12-31T23:59:59Z]"
    
    try:
        # STEP 1: The 'Handshake' (Asking the computer for the Answer)
        handshake_params = {'q': query_string, 'wt': 'json', 'rows': 0}
        response = requests.get(base_url, params=handshake_params, timeout=10)
        
        # Finding the 'numFound' (The total number of objects in the galaxy)
        total_found = response.json().get('response', {}).get('numFound', 0)
        
        if total_found == 0:
            print(f"\n[!] A total lack of data. This query is as empty as a Vogon's heart.")
            return False

        print(f"\n[OK] {total_found} objects detected. Engines engaged...")

        # STEP 2: The 'Pagination' (Because we can't swallow the universe in one go)
        while start < total_found:
            params = {
                'q': query_string,
                'fl': 'pid,dc_license,file_mimetype,dc_format', 
                'wt': 'json',
                'start': start,   
                'rows': 100       
            }
            page_res = requests.get(base_url, params=params, timeout=15)
            docs = page_res.json().get('response', {}).get('docs', [])
            
            all_docs.extend(docs)
            start += 100 # Moving 100 light-years further into the dataset
            print(f"    Scanning: {len(all_docs)} / {total_found}")

        # STEP 3: The 'Local Cache' (Saving the data before the Earth is demolished)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({"response": {"docs": all_docs}}, f)
        return True

    except Exception as e:
        print(f"ERROR: Something is wrong with the space-time continuum: {e}")
        return False

# ---------------------------------------------------------------------------
# PHASE 2: THE ENCYCLOPEDIA ANALYZER (Sorting the Chaos)
# ---------------------------------------------------------------------------

def analyze_and_export(filename="phaidra_audit.json"):
    # Opening our copy of the Guide
    with open(filename, 'r', encoding='utf-8') as f:
        content = json.load(f)
    
    docs = content.get('response', {}).get('docs', [])
    detailed_list = [] 
    stats = {}         
    
    # Magic words for Open Access (Items that are actually useful to the galaxy)
    open_keywords = ['cc-by', 'creative commons', 'public domain', 'open-access', 'cc0']

    for item in docs:
        # --- THE FALLBACK (Identifying the beast) ---
        raw_format = item.get('file_mimetype') or item.get('dc_format') or 'Unknown Entity'
        raw_lic = item.get('dc_license', 'Strictly Restricted (Vogon Style)')
        
        # --- THE CLEANER ---
        mime = raw_format[0] if isinstance(raw_format, list) else raw_format
        lic = raw_lic[0] if isinstance(raw_lic, list) else raw_lic

        detailed_list.append({'PID': item.get('pid'), 'Format': mime, 'License': lic})

        # --- THE CATEGORIZER ---
        if mime not in stats:
            stats[mime] = {'Total': 0, 'Open': 0, 'Restricted': 0}
        
        stats[mime]['Total'] += 1
        
        # Searching for 'Open' keywords (The 'mostly harmless' license types)
        is_open = any(key in lic.lower() for key in open_keywords)
        if is_open:
            stats[mime]['Open'] += 1
        else:
            stats[mime]['Restricted'] += 1

    # --- THE ARCHIVIST (Creating the CSV files) ---
    with open('phaidra_detailed_list.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['PID', 'Format', 'License'])
        writer.writeheader()
        writer.writerows(detailed_list)

    with open('phaidra_summary_stats.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Format', 'Total', 'OpenAccess', 'Restricted'])
        for m, c in stats.items():
            writer.writerow([m, c['Total'], c['Open'], c['Restricted']])

    return stats

# ---------------------------------------------------------------------------
# PHASE 3: THE VISUALIZER (Diagrams for Galactic Stakeholders)
# ---------------------------------------------------------------------------

def plot_all_results(stats, start_y, end_y):
    if not stats: return
    mimes = list(stats.keys())
    
    # CHART 1: The General State of the Galaxy
    totals = [stats[m]['Total'] for m in mimes]
    plt.figure(figsize=(10, 6))
    plt.bar(mimes, totals, color='skyblue')
    plt.title(f'Total Objects Found ({start_y}-{end_y})')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('report_totals.png')
    plt.show()

    # CHART 2: Legal Status (Open vs Restricted)
    x = np.arange(len(mimes))
    width = 0.35
    plt.figure(figsize=(12, 7))
    plt.bar(x - width/2, [stats[m]['Open'] for m in mimes], width, label='Mostly Harmless (Open)', color='seagreen')
    plt.bar(x + width/2, [stats[m]['Restricted'] for m in mimes], width, label='Vogon-Style (Restricted)', color='indianred')
    plt.title(f'License Comparison ({start_y}-{end_y})')
    plt.xticks(x, mimes, rotation=45, ha='right')
    plt.legend()
    plt.tight_layout()
    plt.savefig('report_licenses.png')
    plt.show()

# ---------------------------------------------------------------------------
# THE ENGINE (Don't Panic!)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("="*45)
    print("   HITCHHIKER'S GUIDE TO PHAIDRA AUDITING")
    print("="*45)
    
    # VALIDATION: Looking for a Start Year (Preferably not the beginning of the Universe)
    while True:
        user_start = input("Step 1: Input a numeric Start Year (2008+): ")
        if not user_start.isdigit(): 
            print(f"That is not a year, that is a string. Resistance is futile.")
        elif int(user_start) < 2008: 
            print(f"Data is missing from the galactic archives before 2008.")
        else: 
            break 

    # VALIDATION: End Year
    while True:
        user_end = input("Step 2: Input a numeric End Year: ")
        if not user_end.isdigit():
            print(f"Input must be numeric. Deep Thought is confused.")
        elif int(user_end) < int(user_start):
            print(f"Time travel is not currently supported. End year must be later.")
        else:
            break
    
    # EXECUTION:
    if fetch_all_phaidra_data(user_start, user_end):
        results = analyze_and_export()
        plot_all_results(results, user_start, user_end)
        
        print("\n" + "-"*45)
        print("THE AUDIT IS COMPLETE!")
        print("The files have been generated. Thank you for using the Guide.")
        print("Don't forget your towel.")
        print("-" * 45)