import requests
import json
import matplotlib.pyplot as plt

# --- PHASE 1: DATA ACQUISITION ---

def fetch_all_phaidra_data(start_year, end_year, filename="phaidra_audit.json"):
    """
    INTERFACE: start_year (str), end_year (str).
    Fetches records using the validated date range.
    """
    base_url = "https://phaidra.ustp.at/api/search/select"
    all_docs = []
    start = 0
    rows_per_page = 100 
    
    query_string = f"created:[{start_year}-01-01T00:00:00Z TO {end_year}-12-31T23:59:59Z]"
    
    try:
        handshake_params = {'q': query_string, 'wt': 'json', 'rows': 0}
        response = requests.get(base_url, params=handshake_params, timeout=10)
        response.raise_for_status()
        
        total_found = response.json().get('response', {}).get('numFound', 0)
        
        if total_found == 0:
            print(f"\n[!] No objects found for the period {start_year}-{end_year}.")
            return False

        print(f"\n[OK] Found {total_found} objects. Starting harvest...")

        while start < total_found:
            params = {
                'q': query_string,
                'fl': 'pid,dc_license,file_mimetype,dc_format,resourcetype', 
                'wt': 'json',
                'start': start,
                'rows': rows_per_page
            }
            page_res = requests.get(base_url, params=params, timeout=15)
            page_res.raise_for_status()
            
            docs = page_res.json().get('response', {}).get('docs', [])
            all_docs.extend(docs)
            start += rows_per_page
            print(f"    Progress: {len(all_docs)} / {total_found}")

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({"response": {"docs": all_docs}}, f)
        return True

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        return False

# --- PHASE 2: DATA ANALYSIS ---

def analyze_data(filename="phaidra_audit.json"):
    with open(filename, 'r', encoding='utf-8') as f:
        content = json.load(f)
    
    docs = content.get('response', {}).get('docs', [])
    stats = {}

    for item in docs:
        raw_format = item.get('file_mimetype') or item.get('dc_format') or item.get('resourcetype') or 'Unknown'
        raw_lic = item.get('dc_license', 'All Rights Reserved')
        
        mime = raw_format[0] if isinstance(raw_format, list) and raw_format else raw_format
        lic = raw_lic[0] if isinstance(raw_lic, list) and raw_lic else raw_lic

        if mime not in stats:
            stats[mime] = {}
        stats[mime][lic] = stats[mime].get(lic, 0) + 1
            
    return stats

# --- PHASE 3: VISUALIZATION ---

def plot_report(stats, start_y, end_y):
    if not stats: return
    formats = list(stats.keys())
    counts = [sum(l.values()) for l in stats.values()]

    plt.figure(figsize=(10, 6))
    plt.bar(formats, counts, color='darkcyan')
    plt.title(f'Phaidra Audit: File Formats ({start_y} - {end_y})')
    plt.ylabel('Count')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('phaidra_audit_chart.png')
    plt.show()

# --- MAIN WORKFLOW (With Input Validation) ---

if __name__ == "__main__":
    print("="*45)
    print("   PHAIDRA REPOSITORY AUDIT TOOL")
    print("="*45)
    
    # --- VALIDATION FOR START YEAR ---
    while True:
        user_start = input("Enter start year (2008 or later): ")
        
        # 1. First, check if it is NOT a number
        if not user_start.isdigit():
            print(f"Error: '{user_start}' is not a year. Please use numbers only.")
        
        # 2. If it IS a number, check if it's too small
        else:
            if int(user_start) < 2008:
                print(f"Error: {user_start} is too early. Phaidra records start in 2008.")
            else:
                # If it's a number AND it's >= 2008, we finally break
                break

    # --- VALIDATION FOR END YEAR ---
    while True:
        user_end = input("Enter end year (e.g., 2025): ")
        
        if not user_end.isdigit():
            print(f"Error: '{user_end}' is not a year. Please use numbers only.")
        else:
            if int(user_end) < int(user_start):
                print(f"Error: End year cannot be before start year ({user_start}).")
            else:
                break
    
    if fetch_all_phaidra_data(user_start, user_end):
        results = analyze_data()
        
        print("\n" + "-"*40)
        print(f"AUDIT SUMMARY ({user_start} - {user_end})")
        print("-"*40)
        for m, lics in results.items():
            print(f"{m:25} | Records: {sum(lics.values())}")
        
        plot_report(results, user_start, user_end)