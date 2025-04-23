import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
import joblib

# Load training data
df = pd.read_csv('training_data.csv', header=None, names=['user_tags', 'club_tags', 'label'])

# Combine both columns into a single string input
X_raw = df['user_tags'] + ' ' + df['club_tags']
y = df['label']

# Build pipeline: vectorize -> logistic regression
pipeline = make_pipeline(CountVectorizer(), LogisticRegression())
pipeline.fit(X_raw, y)

# Save model
joblib.dump(pipeline, 'club_model.pkl')
print("Model trained and saved!")
