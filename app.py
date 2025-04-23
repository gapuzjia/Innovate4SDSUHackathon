from flask import Flask, render_template, request, jsonify
import joblib
import csv
import json
import subprocess


app = Flask(__name__)
model = joblib.load('club_model.pkl')

# ========================
# Tag Groups (shortened here, use your full version)
# ========================
tag_groups = {
    "STEM": [
        "engineering", "technology", "science", "math", "robotics", "computer science", 
        "geology", "physics", "biology", "chemistry", "civil engineering", 
        "mechanical engineering", "electrical engineering", "aerospace engineering",
        "cybersecurity", "automotive engineering", "research", "data science",
        "machine learning", "artificial intelligence", "coding", "software development",
        "hardware", "bioinformatics", "environmental science"],
    "Leadership": [
        "leadership", "networking", "management", "mentorship", "student government",
        "public speaking", "professional development", "career readiness"],
    "Business/Finance": [
        "trading", "stocks", "marketing", "investing", "actuarial studies", "statistics", 
        "accounting", "economics", "finance", "entrepreneurship", "business development", 
        "consulting", "e-commerce", "sales", "branding", "startups"],
    "Cultural": [
        "asian community", "black community", "latino community", "international", 
        "japanese culture", "chinese culture", "hispanic community", "korean culture", 
        "afghan community", "african community", "filipino culture", "indigenous", 
        "middle eastern", "arab", "islander", "diaspora"],
    "Greek Life": [
        "sorority", "fraternity", "co-ed", "greek council", "divine nine", "panhellenic"],
    "Arts & Media": [
        "music", "film", "photography", "art", "fashion", "stage directing",
        "stage production", "graphic design", "comedy", "drag", "writing", 
        "sound engineering", "media production", "broadcasting", "journalism",
        "animation", "videography", "creative writing", "editing"],
    "Literature": [
        "books", "reading", "novels", "literary analysis", "book club", "poetry"],
    "Dance": [
        "color guard", "majorette", "cultural dance", "latin dance", "k-pop", 
        "hip hop", "ballet", "contemporary", "step", "jazz", "tap", "folk dance"],
    "Crafting": [
        "crocheting", "jewelry making", "sewing", "ceramics", "diy", "resin art", 
        "painting", "calligraphy", "scrapbooking"],
    "Gaming": [
        "casual gaming", "competitive gaming", "board games", "esports", 
        "tabletop games", "video games", "game development", "D&D"],
    "Volunteering & Service": [
        "volunteering", "nonprofit", "service", "education", "outreach", 
        "community service", "philanthropy", "tutoring", "charity", 
        "fundraising", "youth outreach", "homeless support"],
    "Medical & Healthcare": [
        "healthcare", "nursing", "veterinary medicine", "pre-med", "nutrition", 
        "public health", "mental health", "physical therapy", "dental", 
        "pharmacy", "emergency medicine", "first aid", "wellness"],
    "Social & Events": [
        "events", "social", "games", "parties", "hangouts", "network mixers",
        "student life", "icebreakers", "club fairs"],
    "Religion & Spirituality": [
        "christian", "catholic", "buddhism", "youth group", "bible study", 
        "judaism", "muslim", "hindu", "interfaith", "prayer", "spirituality", 
        "meditation", "faith-based", "chaplaincy"],
    "Military": [
        "navy", "air force", "army", "ROTC", "marines", "veterans", "military families"],
    "Politics": [
        "pre-law", "democrat", "republican", "model united nations", "policy making", 
        "mock trial", "debate", "activism", "legislation", "advocacy", "campaigning"],
    "Sports": [
        "basketball", "volleyball", "pickleball", "tennis", "table tennis",
        "water sports", "boxing", "badminton", "gymnastics", "softball", 
        "swimming", "field hockey", "powerlifting", "surfing", "jiu-jitsu",
        "soccer", "football", "track and field", "ultimate frisbee", "wrestling", 
        "rock climbing", "martial arts", "fencing", "equestrian", "cheerleading", "fitness"],
    "Gender": [
        "women-led", "LGBTQ+", "gender equality", "feminism", "men's health", 
        "queer support", "non-binary", "women in stem", "gender inclusivity"]
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
club_roster = []               # Dynamic swipeable list
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
    # Retrain the model by running train_model.py
    try:
        subprocess.run(['python', 'train_model.py'], check=True)
        print("✅ Retraining successful.")
    except subprocess.CalledProcessError as e:
        print("❌ Retraining failed:", e)

    # Reload updated model
    global model
    model = joblib.load('club_model.pkl')

    return render_template('profile.html', tag_groups=tag_groups)



@app.route('/submit_profile', methods=['POST'])
def submit_profile():
    selected_tags = request.form.getlist('tags')
    user_profile['tags'] = selected_tags

    # Reset all memory
    swipes["right"].clear()
    swipes["left"].clear()
    swipes["tag_scores"].clear()
    club_roster.clear()
    seen_club_names.clear()  # ← FIXED THIS LINE

    # Add initial clubs based on profile tags
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

        # Real-time learning via tag_scores
        for tag in club['tags']:
            if tag not in swipes["tag_scores"]:
                swipes["tag_scores"][tag] = 0
            swipes["tag_scores"][tag] += 1 if direction == "right" else -1

        # Expand club_roster based on swiped-right tags
        if direction == "right":
            for tag in club['tags']:
                for other in clubs:
                   if tag in other['tags'] and other['name'] not in seen_club_names:
                    input_text = ' '.join(user_profile['tags']) + ' ' + ' '.join(other['tags'])
                    prob = model.predict_proba([input_text])[0][1]
                    if prob > 0.5:  # or adjust threshold to be stricter like 0.6
                        club_roster.append(other)
                        seen_club_names.add(other['name'])


        # Save swipe for future training
        label = 1 if direction == "right" else 0
        with open('training_data.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([','.join(user_profile['tags']), ','.join(club['tags']), label])

    return jsonify({"status": "ok"})


@app.route('/saved')
def saved():
    liked_clubs = [club for club in clubs if club['name'] in swipes['right']]
    return render_template('saved.html', clubs=liked_clubs)


if __name__ == '__main__':
    app.run(debug=True)
