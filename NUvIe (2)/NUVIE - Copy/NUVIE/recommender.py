from flask import app, render_template, request
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils import get_poster_url, get_movie_details
import os
# Load movies and links
base_path = os.path.dirname(os.path.abspath(__file__))  # This gives ...\NUVIE\NUVIE
static_path = os.path.join(base_path, "static")

# Construct full paths to the files
links_path = os.path.join(static_path, "links.csv")
movies_path = os.path.join(static_path, "movies.csv")

links = pd.read_csv(links_path)
movies = pd.read_csv(movies_path)
# Fill missing genres
movies['genre'] = movies['genre'].fillna('')

# Merge movies with links (optional, but only if you're using tmdb_id/imdb_id)
movies = pd.merge(movies, links[['movie_id', 'tmdb_id', 'imdb_id']], on='movie_id', how='left',validate='one_to_one' )

# TF-IDF + Cosine similarity
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(movies['genre'])
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

# Reset index
movies = movies.reset_index()
def get_recommendations(title, top_n=10):
    title = title.lower()
    indices = movies[movies['title'].str.lower().str.contains(title)].index

    if indices.empty:
        return []

    idx = indices[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:top_n+1]
    movie_indices = [i[0] for i in sim_scores]

    recs = movies.loc[movie_indices][['title', 'genre', 'tmdb_id', 'imdb_id']].to_dict(orient='records')

    for movie in recs:
        movie['poster_url'] = get_poster_url(movie.get('tmdb_id'), movie.get('imdb_id'))
        details = get_movie_details(movie.get('tmdb_id'))
        rating = details.get('rating')
        movie['rating'] = f"{rating:.1f}" if rating is not None else "N/A"
        movie['tmdb_genres'] = details.get('genre')  # this is used in the template

    return recs



def get_movie_list():
    return movies['title'].tolist()
get_recommendations("avatar")