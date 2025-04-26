from flask import Flask, render_template, request, jsonify
import joblib
import csv
import json
import subprocess

app = Flask(__name__)
model = joblib.load('club_model.pkl')

tag_groups = {
    "STEM": [
        "engineering", "science", "robotics", "computer science", 
        "geography", "physics", "biology", "chemistry", "civil engineering", 
        "mechanical engineering", "electrical engineering", "aerospace engineering",
        "cybersecurity", "automotive engineering", "research", 
        "data science", "mathematics"
    ],
    "Leadership": [
        "leadership", "networking", "management", "public speaking"
    ],
    "Business/Finance": [
        "trading", "marketing", "statistics", "finance"
    ],
    "Cultural": [
        "asian community", "black community", "latino community", "international", 
        "palestenian community", "japanese culture", "chinese culture", 
        "hispanic community", "french community", "afghan community", 
        "language", "persian culture", "southeast asian", "islander", 
        "hawaiian culture", "italian community", "iraqi community"
    ],
    "Greek Life": [
        "sorority", "fraternity", "co-ed"
    ],
    "Arts & Media": [
        "music", "film", "photography", "fashion", "graphic design", 
        "comedy", "sound engineering", "media production", "journalism", "videography"
    ],
    "Literature": [
        "books", "reading", "philosophy"
    ],
    "Dance": [
        "latin dance"
    ],
    "Crafting": [
        "crocheting", "jewelry making", "ceramics", "furniture"
    ],
    "Gaming": [
        "board games"
    ],
    "Volunteering & Service": [
        "volunteering", "service", "education", "outreach", 
        "homeless support", "social work"
    ],
    "Medical & Healthcare": [
        "healthcare", "nursing", "veterinary medicine", "pre-med", 
        "public health", "mental health", "physical therapy", 
        "dental", "rehabilitation"
    ],
    "Social & Events": [
        "social"
    ],
    "Religion & Spirituality": [
        "christian", "buddhism", "bible study", "judaism", 
        "muslim", "prayer", "spirituality", "faith-based"
    ],
    "Military": [
        "ROTC"
    ],
    "Politics": [
        "pre-law", "democrat", "republican", "model united nations", 
        "policy making", "mock trial", "debate", "activism"
    ],
    "Sports": [
        "basketball", "volleyball", "sailing", "boxing", "badminton", 
        "gymnastics", "softball", "running", "field hockey", 
        "powerlifting", "surfing", "muay thai", "skateboarding", "fitness"
    ],
    "Gender": [
        "women-led", "LGBTQ+"
    ]
}


# ========================
# Global Variables
# ========================
swipes = {
    "right": [],
    "left": [],
    "tag_scores": {}
}

user_profile = {"tags": []}
club_roster = []
seen_club_names = set()

# ========================
# Load Club Data
# ========================
with open('clubs.json', 'r') as f:
    clubs = json.load(f)

# ========================
# Routes
# ========================
@app.route('/')
def profile():
    # Try retraining model (but don't crash app if fails)
    try:
        if os.path.exists('training_data.csv'):
            subprocess.run(['python', 'train_model.py'], check=True)
            global model
            model = joblib.load('club_model.pkl')
            print("✅ Model retrained.")
        else:
            print("")
    except Exception as e:
        print("", e)

    # Split groups into two halves for two columns
    all_groups = list(tag_groups.items())
    mid = len(all_groups) // 2
    left_groups = all_groups[:mid]
    right_groups = all_groups[mid:]

    return render_template('profile.html', 
                           left_groups=left_groups, 
                           right_groups=right_groups)

@app.route('/submit_profile', methods=['POST'])
def submit_profile():
    selected_tags = request.form.getlist('tags')
    user_profile['tags'] = selected_tags

    swipes["right"].clear()
    swipes["left"].clear()
    swipes["tag_scores"].clear()
    club_roster.clear()
    seen_club_names.clear()

    for club in clubs:
        if any(tag in club['tags'] for tag in selected_tags):
            if club['name'] not in seen_club_names:
                club_roster.append(club)
                seen_club_names.add(club['name'])

    return render_template('index.html', clubs=club_roster)

@app.route('/swipe', methods=['POST'])
def swipe():
    data = request.get_json()
    direction = data.get('direction')
    club_id = data.get('club_id')

    club = next((c for c in clubs if c['name'] == club_id), None)

    if club:
        swipes[direction].append(club_id)

        for tag in club['tags']:
            if tag not in swipes["tag_scores"]:
                swipes["tag_scores"][tag] = 0
            swipes["tag_scores"][tag] += 1 if direction == "right" else -1

        if direction == "right" and model:
            for tag in club['tags']:
                for other in clubs:
                    if tag in other['tags'] and other['name'] not in seen_club_names:
                        input_text = ' '.join(user_profile['tags']) + ' ' + ' '.join(other['tags'])
                        prob = model.predict_proba([input_text])[0][1]
                        if prob > 0.5:
                            club_roster.append(other)
                            seen_club_names.add(other['name'])

        label = 1 if direction == "right" else 0
        with open('training_data.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([','.join(user_profile['tags']), ','.join(club['tags']), label])

    return jsonify({"status": "ok"})

@app.route('/saved')
def saved():
    liked_clubs = [club for club in clubs if club['name'] in swipes['right']]
    return render_template('saved.html', clubs=liked_clubs)

@app.route('/chat')
def chat():
    club_name = request.args.get('club', 'Club Chat')  # <-- fallback if none given
    return render_template('chat.html', club_name=club_name)



if __name__ == '__main__':
    app.run(debug=True)