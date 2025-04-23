from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

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
swipes = {"right": [], "left": []}

@app.route('/')
def profile():
    return render_template('profile.html', tags=all_tags)


@app.route('/submit_profile', methods=['POST'])
def submit_profile():
    selected_tags = request.form.getlist('tags')
    user_profile['tags'] = selected_tags
    return render_template('index.html', clubs=clubs)

@app.route('/swipe', methods=['POST'])
def swipe():
    data = request.get_json()
    direction = data.get('direction')
    club_id = data.get('club_id')
    if direction in swipes:
        swipes[direction].append(club_id)
    return jsonify({"status": "ok"})

@app.route('/saved')
def saved():
    liked_clubs = [club for club in clubs if club['id'] in swipes['right']]
    return render_template('index.html', clubs=liked_clubs)

if __name__ == '__main__':
    app.run(debug=True)
