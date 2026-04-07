import pickle

import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

print("Loading dataset...")
movies = pd.read_csv("tmdb_5000_movies.csv")

print("Selecting required columns...")
movies = movies[["id", "title", "overview", "vote_average", "release_date"]]

print("Cleaning missing values...")
movies.dropna(inplace=True)
movies["id"] = movies["id"].astype(int)
movies["title"] = movies["title"].astype(str)
movies["overview"] = movies["overview"].astype(str)
movies["release_date"] = movies["release_date"].astype(str)

print("Vectorizing text...")
cv = CountVectorizer(max_features=5000, stop_words="english")
vectors = cv.fit_transform(movies["overview"]).toarray()

print("Calculating similarity...")
similarity = cosine_similarity(vectors)

print("Saving model...")
pickle.dump(movies, open("movies.pkl", "wb"))
pickle.dump(similarity, open("similarity.pkl", "wb"))

print("Model files created successfully!")
