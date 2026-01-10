import requests
import json
import matplotlib.pyplot as plt

# --- 1. DATA ACQUISITION ---
def fetch_all_phaidra_data(filename="phaidra_audit.json"):
    """
    Fetches all records with a broad field list to ensure format data is captured.
    Interface: filename (str) - path for local data storage.
    """
    base_url = "https://phaidra.ustp.at/api/search/select"
    all_docs = []
    start = 0
    rows_per_page = 100 
    
    try:
        # Requesting multiple format-related fields: file_mimetype, dc_format, resourcetype
        query_params = {
            'q': 'created:[2023-01-01T00:00:00Z TO 2024-12-31T23:59:59Z]',
            'fl': 'pid,dc_license,file_mimetype,dc_format,resourcetype', 
            'wt': 'json',
            'rows': 0
        }
        
        response = requests.get(base_url, params=query_params, timeout=10)
        response.raise_for_status()
        total_found = response.json().get('response', {}).get('numFound', 0)
        
        print(f"DEBUG: Found {total_found} total records. Downloading...")

        while start < total_found:
            query_params.update({'start': start, 'rows': rows_per_page})
            page_res = requests.get(base_url, params=query_params, timeout=15)
            page_res.raise_for_status()
            
            docs = page_res.json().get('response', {}).get('docs', [])
            all_docs.extend(docs)
            start += rows_per_page
            print(f"Harvested: {len(all_docs)} / {total_found}")

        # Requirement: Write data to a file 
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({"response": {"docs": all_docs}}, f)
        return True

    except Exception as e:
        print(f"CRITICAL ERROR during acquisition: {e}")
        return False

# --- 2. DATA ANALYSIS ---
def analyze_data(filename="phaidra_audit.json"):
    """
    Requirement: Function with an interface.
    Processes data using a fallback logic to identify the correct MIME type.
    """
    # Requirement: Read data from a file 
    with open(filename, 'r', encoding='utf-8') as f:
        content = json.load(f)
    
    docs = content.get('response', {}).get('docs', [])
    stats = {} # Requirement: Use an array/dictionary 

    # Requirement: Use at least one loop 
    for item in docs:
        # FALLBACK LOGIC: Try different fields if 'file_mimetype' is empty
        # Requirement: At least one decision used 
        raw_mime = item.get('file_mimetype') or item.get('dc_format') or item.get('resourcetype') or 'unknown'
        lic = item.get('dc_license', 'All Rights Reserved')
        
        # Clean potential list formats (addressing the 'unhashable type' error)
        mime = raw_mime[0] if isinstance(raw_mime, list) and raw_mime else raw_mime
        lic = lic[0] if isinstance(lic, list) and lic else lic

        if mime not in stats:
            stats[mime] = {}
        
        stats[mime][lic] = stats[mime].get(lic, 0) + 1
            
    return stats

# --- 3. VISUALIZATION ---
def plot_stats(stats_map):
    """
    Requirement: Make at least one diagram.
    """
    if not stats_map:
        return

    labels = list(stats_map.keys())
    values = [sum(l.values()) for l in stats_map.values()]

    plt.figure(figsize=(10, 6))
    plt.bar(labels, values, color='skyblue')
    plt.title('Phaidra Repository Distribution (2023-2024)')
    plt.ylabel('Number of Objects')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    plt.savefig('phaidra_audit_chart.png')
    plt.show()

if __name__ == "__main__":
    # Implementation following the Waterfall Model [cite: 4]
    if fetch_all_phaidra_data():
        final_stats = analyze_data()
        
        print("\n--- FINAL AUDIT RESULTS ---")
        for m, lics in final_stats.items():
            print(f"Type: {m:25} | Records: {sum(lics.values())}")
            
        plot_stats(final_stats)