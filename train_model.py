import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import make_pipeline
import joblib

# Load training data
df = pd.read_csv('training_data.csv', header=None, names=['user_tags', 'club_tags', 'label'])

# Drop any rows where user_tags or club_tags is missing
df = df.dropna(subset=['user_tags', 'club_tags'])

# Combine user_tags and club_tags into one string input
X = df['user_tags'] + ' ' + df['club_tags']
y = df['label']

# Build and train the pipeline
model = make_pipeline(CountVectorizer(), LogisticRegression())
model.fit(X, y)

# Save the trained model
joblib.dump(model, 'club_model.pkl')
print("Model trained and saved!")
