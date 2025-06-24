import json
import csv

def convert_json_to_csv():
    """Convert the entire keyword JSON file to CSV format"""
    
    # Output CSV file
    output_file = 'all_keywords.csv'
    
    # Read the keyword database line by line and collect all valid entries
    keywords = []
    
    print("Reading JSON file...")
    with open('backend/keyword_ids_06_23_2025.json', 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if line and line.startswith('{"id":') and line.endswith('}'):
                try:
                    item = json.loads(line)
                    if 'name' in item and 'id' in item:
                        keywords.append((item['name'], item['id']))
                except json.JSONDecodeError:
                    continue
            
            # Progress indicator every 10000 lines
            if line_num % 10000 == 0:
                print(f"Processed {line_num} lines...")
    
    # Sort by ID for consistency
    print("Sorting keywords by ID...")
    keywords.sort(key=lambda x: x[1])
    
    # Write to CSV
    print(f"Writing {len(keywords)} keywords to CSV...")
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['keyword', 'id'])
        for keyword, keyword_id in keywords:
            writer.writerow([keyword, keyword_id])
    
    print(f"Conversion complete! CSV file created: {output_file}")
    print(f"Total keywords: {len(keywords)}")

if __name__ == "__main__":
    convert_json_to_csv() 