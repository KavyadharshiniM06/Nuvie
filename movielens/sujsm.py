from flask import Flask, request, render_template
import requests

app = Flask(__name__, template_folder="templates")

TMDB_API_KEY = "8ac3dbbfa63384187f38a7c4cfb0286e"
TMDB_URL = "https://api.themoviedb.org/3/discover/movie"

def get_movies_by_preferences(genres, min_rating):
    """Fetches movies based on selected genres and minimum rating from TMDb API."""
    genre_ids = ",".join(genres) if genres else None  

    params = {
        "api_key": TMDB_API_KEY,
        "with_genres": genre_ids,
        "vote_average.gte": str(min_rating),
        "sort_by": "popularity.desc",
        "language": "en-US",
        "page": 1
    }

    response = requests.get(TMDB_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        return data.get("results", [])[:6]
    else:
        print(f"TMDb API Error: {response.text}")  
        return []

@app.route('/')
def index():
    return render_template("questions.html")

@app.route('/submit', methods=['POST'])
def submit():
    genres = request.form.getlist("genre")  
    rating = request.form.get("rating")  

    min_rating = int(rating.strip("+")) if rating else 6  

    movies = get_movies_by_preferences(genres, min_rating)
    print("Movies data being passed:", movies)  

    if not movies:
        return "No movies found. Check API response or try different filters.", 500
    
    return render_template("results.html", movies=movies)

if __name__ == "__main__":
    app.run(debug=True)
