from urllib import response
from flask import Flask, request, render_template
import requests

app = Flask(__name__, template_folder="templates")

TMDB_API_KEY = "8ac3dbbfa63384187f38a7c4cfb0286e"  # Correct API Key
TMDB_URL = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}"  # Correct API URL

def get_movies_by_preferences(genres, min_rating):
    """Fetches movies based on selected genres and minimum rating from TMDb API."""
    genre_ids = ",".join(genres) if genres else None  # Default to Action if empty

    params = {
        "api_key": TMDB_API_KEY,
        "with_genres": genre_ids,
        "vote_average.gte": str(min_rating),  # Minimum IMDb rating
        "sort_by": "popularity.desc",
        "language": "en-US",
        "page": 1
    }

    response = requests.get(TMDB_URL, params=params)  # Use correct URL
    if response.status_code == 200:
        data = response.json()
        print("Full API Response:", data)  # ✅ Debug API response
        return data.get("results", [])[:6]
    else:
        print(f"TMDb API Error: {response.text}")  # Debug API error
        return []

@app.route('/')
def index():
    return render_template("questions.html")

@app.route('/submit', methods=['POST'])
def submit():
    genres = request.form.getlist("genre")  # Get selected genres (list)
    rating = request.form.get("rating")  # Get selected rating (e.g., "6+", "7+")

    min_rating = int(rating.strip("+")) if rating else 6  # Default to 6+

    movies = get_movies_by_preferences(genres, min_rating)
    BASE_IMAGE_URL = "https://image.tmdb.org/t/p/w500"
    for movie in movies:
        if not movie.get("poster_path"):
            movie["poster_path"] = "https://via.placeholder.com/150"
        else:
            movie["poster_path"] = BASE_IMAGE_URL + movie["poster_path"]
    return render_template("results.html", movies=movies)

#print("API Response:", response.json())  # Debugging API response
response = requests.get(TMDB_URL)
data = response.json()

print("data:",data)

if __name__ == "__main__":
    app.run(debug=True)




