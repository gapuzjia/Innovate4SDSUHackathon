from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

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
        "rock climbing", "martial arts", "fencing", "equestrian", "cheerleading"],
    "Gender": [
        "women-led", "LGBTQ+", "gender equality", "feminism", "men's health", 
        "queer support", "non-binary", "women in stem", "gender inclusivity"]
}


swipes = {
    "right": [],
    "left": [],
    "tag_scores": {}
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
