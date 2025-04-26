import csv
import json

def convert_csv_to_json(csv_path, json_path):
    clubs = []
    with open(csv_path, newline='', encoding='cp1252') as csvfile:
        reader = csv.DictReader(csvfile)
        print("CSV headers:", reader.fieldnames)

        for row in reader:
            club = {
                "name": row.get("Name") or row.get("\ufeffName") or "Unnamed Club",
                "description": row.get("Purpose", ""),
                "tags": [tag.strip().lower() for tag in row.get("Tags", "").split(',')],
                "email": row.get("Email Address", "")  # ✨ new line to grab email
            }
            clubs.append(club)
    
    with open(json_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(clubs, jsonfile, indent=2)

# Run this once to generate clubs.json
if __name__ == '__main__':
    convert_csv_to_json('clubs.csv', 'clubs.json')
