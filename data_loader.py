import csv
import json

def convert_csv_to_json(csv_path, json_path):
    clubs = []
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        print("CSV headers:", reader.fieldnames)

        for row in reader:
            club = {
                "name": row["\ufeffName"],
                "description": row["Purpose"],
                "tags": [tag.strip().lower() for tag in row["Tags"].split(',')]
            }
            clubs.append(club)
    
    with open(json_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(clubs, jsonfile, indent=2)

# Run this once to generate clubs.json
if __name__ == '__main__':
    convert_csv_to_json('clubs.csv', 'clubs.json')
