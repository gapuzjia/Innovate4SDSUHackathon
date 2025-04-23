from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

tag_groups = {
    "STEM": ["engineering", "technology", "science", "math", "robotics"],
    "Leadership": ["leadership", "networking", "business"],
    "Cultural": ["asian community", "black community", "latino community", "international"],
    "Greek Life": ["sorority", "fraternity", "greek life"],
    "Arts & Media": ["music", "film", "photography", "art"],
    "Volunteering & Service": ["volunteering", "nonprofit", "service"],
    "Health": ["healthcare", "mental health", "fitness"],
    "Social & Events": ["events", "social", "games"],
}

swipes = {
    "right": [],
    "left": [],
    "tag_scores": {}  # <-- THIS LINE
}



# Load clubs from file
with open('clubs.json', 'r') as f:
    clubs = json.load(f)

# After loading clubs
with open('clubs.json', 'r') as f:
    clubs = json.load(f)

# Get all unique tags from clubs
all_tags = sorted({tag for club in clubs for tag in club['tags']})


# In-memory user profile and swipes (mock for now)
user_profile = {"tags": []}

@app.route('/')
def profile():
    return render_template('profile.html', tag_groups=tag_groups)



@app.route('/submit_profile', methods=['POST'])
def submit_profile():
    selected_tags = request.form.getlist('tags')
    user_profile['tags'] = selected_tags

    # Filter clubs that share tags with the user
    matching_clubs = []
    for club in clubs:
        if any(tag in club['tags'] for tag in selected_tags):
            matching_clubs.append(club)

    def score_club(club, user_tags):
        # How many tags match initial user profile
        base_score = len(set(club['tags']) & set(user_tags))

        # How many tags are learned to be good/bad
        learned_score = sum(swipes["tag_scores"].get(tag, 0) for tag in club['tags'])

        return base_score + learned_score


    # Reset swipe memory
    swipes["right"].clear()
    swipes["left"].clear()

    return render_template('index.html', clubs=matching_clubs)


@app.route('/swipe', methods=['POST'])
def swipe():
    data = request.get_json()
    direction = data.get('direction')
    club_id = data.get('club_id')
    
    club = next((c for c in clubs if c['id'] == club_id), None)
    if club:
        swipes[direction].append(club_id)

        for tag in club['tags']:
            if tag not in swipes["tag_scores"]:
                swipes["tag_scores"][tag] = 0
            swipes["tag_scores"][tag] += 1 if direction == "right" else -1

    return jsonify({"status": "ok"})


@app.route('/saved')
def saved():
    liked_clubs = [club for club in clubs if club['id'] in swipes['right']]
    return render_template('index.html', clubs=liked_clubs)

if __name__ == '__main__':
    app.run(debug=True)
