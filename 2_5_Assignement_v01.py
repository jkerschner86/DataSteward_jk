import requests
import json
import matplotlib.pyplot as plt

# --- 1. DATA ACQUISITION & STORAGE ---
def fetch_and_save_data(filename="phaidra_data.json"):
    """
    Fetches object metadata from Phaidra for 2023-2024 and saves it to a file.
    Interface: filename (str) - where to save the raw data.
    """
    # Phaidra REST API search endpoint (example URL structure)
    base_url = "https://phaidra.ustp.at/api/search/select"
    
    # Query for objects created in 2023 and 2024
    # Using Solr-style query parameters typically used by Phaidra/Fedora
    params = {
        'q': 'created:[2023-01-01T00:00:00Z TO 2024-12-31T23:59:59Z]',
        'wt': 'json',
        'rows': 100  # Limited for the assignment scope
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Write data to a file (Requirement: Read/Write from a file)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        print(f"Successfully saved API data to {filename}")
        return True
    except Exception as e:
        print(f"Error during acquisition: {e}")
        return False

# --- 2. PROCESSING & ANALYSIS ---
def analyze_resource_types(filename="phaidra_data.json"):
    """
    Reads the local file and performs statistics on resource types.
    """
    # Requirement: Read data from a file
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = json.load(f)
    except FileNotFoundError:
        return {}

    # Requirement: Use at least one array/dictionary
    type_counts = {}
    
    # Requirement: Use at least one loop
    # Accessing the list of docs (objects) from the Phaidra response
    docs = content.get('response', {}).get('docs', [])
    
    for item in docs:
        # Extract the resource type (e.g., 'picture', 'video', 'text')
        res_type = item.get('resourcetype', 'unknown')
        
        # Requirement: Use at least one decision
        if res_type in type_counts:
            type_counts[res_type] += 1
        else:
            type_counts[res_type] = 1
            
    return type_counts

# --- 3. VISUALIZATION ---
def create_statistics_diagram(stats_dict):
    """
    Requirement: Make at least one diagram.
    """
    if not stats_dict:
        print("No data available to plot.")
        return

    labels = list(stats_dict.keys())
    values = list(stats_dict.values())

    plt.figure(figsize=(10, 6))
    plt.bar(labels, values, color='skyblue')
    plt.xlabel('Resource Type')
    plt.ylabel('Number of Objects')
    plt.title('Phaidra Repository Statistics (2023-2024)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save and show the diagram
    plt.savefig('phaidra_stats_2023_2024.png')
    plt.show()

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    # 1. Acquisition
    if fetch_and_save_data():
        # 2. Analysis
        stats = analyze_resource_types()
        print("Analysis Results:", stats)
        
        # 3. Visualization
        create_statistics_diagram(stats)