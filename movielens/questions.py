import time
import traceback
from flask import Flask, jsonify, request, render_template
import mysql.connector
from tabulate import tabulate
import requests
app = Flask(__name__, template_folder="templates")
TMDB_API_KEY = "8ac3dbbfa63384187f38a7c4cfb0286e"
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="hemni",
    connection_timeout=60,
    autocommit=True)
cursor = db.cursor(dictionary=True)

# **Genre ID to Name Mapping**
GENRE_MAP = {
    "10749": "Romance",
    "28": "Action",
    "12": "Adventure",
    "16": "Animation",
    "35": "Comedy",
    "80": "Crime",
    "18": "Drama",
    "14": "Fantasy",
    "27": "Horror",
    "9648": "Mystery",
    "878": "Sci-Fi",
    "53": "Thriller",
    "10402": "Music",
    "10751": "Family",
    "36": "History",
    "10752": "War",
    "37": "Western"
}

'''def get_movie_poster(title):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={title}"
    response = requests.get(url).json()

    if response.get("results"):
        poster_path = response["results"][0].get("poster_path")
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
    
    return None

def get_poster_url(tmdb_id=None, imdb_id=None):
    """Fetch movie poster using TMDb API (TMDb ID preferred, IMDb ID as fallback)."""
    
    if tmdb_id:  # Try TMDb ID first
        url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={TMDB_API_KEY}"
        response = requests.get(url).json()
        poster_path = response.get("poster_path")
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
    
    if imdb_id:  # If no TMDb poster, try IMDb ID
        url = f"https://api.themoviedb.org/3/find/tt{imdb_id}?api_key={TMDB_API_KEY}&external_source=imdb_id"
        response = requests.get(url).json()
        if response.get("movie_results"):
            poster_path = response["movie_results"][0].get("poster_path")
            if poster_path:
                return f"https://image.tmdb.org/t/p/w500{poster_path}"

    return None


@app.route('/')
def index():
    return render_template("questions.html")

@app.route('/submit', methods=['POST'])
def submit():
    try:
        print(request.form)

        genre_ids = request.form.getlist("genre")  # Get selected genre IDs
        rating = request.form.get("rating", type=float)  # Get minimum rating

        # **Convert genre IDs to Names**
        genre_names = [GENRE_MAP.get(genre_id) for genre_id in genre_ids if genre_id in GENRE_MAP]

        query = """
        SELECT 
        m.movie_id, 
        m.title, 
        m.genres,l.tmdb_id,l.imdb_id,
        YEAR(FROM_UNIXTIME(MAX(r.timestamp))) AS rating_year,  
        COALESCE(AVG(r.rating), 0) AS avg_rating
        FROM movies AS m
        LEFT JOIN Ratings AS r ON m.movie_id = r.movie_id
        LEFT JOIN Links AS l ON m.movie_id = l.movie_id  
        WHERE 1=1
        """
    
        params = []

        # **Filter by genre names**
        if genre_names:
            genre_conditions = " OR ".join(["m.genres LIKE %s" for _ in genre_names])
            query += f" AND ({genre_conditions})"
            params.extend([f"%{genre}%" for genre in genre_names])  # Match genre name in movie genres

        query += " GROUP BY m.movie_id"

        # **Filter by rating**
        if rating:
            query += " HAVING avg_rating >= %s"
            params.append(rating)

        query += " ORDER BY avg_rating DESC LIMIT 1000"

        print("\nGenerated SQL Query:\n", query)  # Print the SQL query
        print("Query Parameters:", params)

        # **Execute Query**
        cursor.execute(query, params)
        movies = cursor.fetchall()

        

        filtered_movies = []
        for movie in movies:
            poster_url = get_poster_url(movie["tmdb_id"], movie["imdb_id"])
        if poster_url:
            movie["poster_url"] = poster_url
            filtered_movies.append(movie)

        db.close()
        return render_template("result_table.html", movies=filtered_movies)
    
    except Exception as e:
        print("Error:", str(e))
        print(traceback.format_exc())  # Print full traceback
        return jsonify({"error": str(e)}), 500

@app.route('/test')
def test():
    return render_template("result_table.html", movies=[{"title": "Test Movie", "genres": "Romance", "rating_year": 2023, "avg_rating": 4.5}])


if __name__ == "__main__":
    app.run(debug=True)'''


poster_cache = {}

def get_poster_url(tmdb_id=None, imdb_id=None):
    """Fetch movie poster using TMDb API with caching."""
    if tmdb_id and tmdb_id in poster_cache:
        return poster_cache[tmdb_id]

    if imdb_id and imdb_id in poster_cache:
        return poster_cache[imdb_id]

    url = None
    if tmdb_id:
        url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={TMDB_API_KEY}"
    elif imdb_id:
        url = f"https://api.themoviedb.org/3/find/tt{imdb_id}?api_key={TMDB_API_KEY}&external_source=imdb_id"

    if url:
        response = requests.get(url).json()
        poster_path = response.get("poster_path") or (
            response.get("movie_results", [{}])[0].get("poster_path") if response.get("movie_results") else None
        )
        if poster_path:
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
            poster_cache[tmdb_id or imdb_id] = poster_url  # Cache result
            return poster_url

    return None

@app.route('/')
def index():
    return render_template("questions.html")

@app.route('/submit', methods=['POST'])
def submit():
    try:
        start_time = time.time()

        genre_ids = request.form.getlist("genre")
        rating = request.form.get("rating", type=float)

        genre_names = [GENRE_MAP.get(genre_id) for genre_id in genre_ids if genre_id in GENRE_MAP]

        query = """
        SELECT m.movie_id, m.title, m.genres, l.tmdb_id, l.imdb_id,
               YEAR(FROM_UNIXTIME(MAX(r.timestamp))) AS rating_year,  
               COALESCE(AVG(r.rating), 0) AS avg_rating
        FROM movies AS m
        LEFT JOIN Ratings AS r ON m.movie_id = r.movie_id
        LEFT JOIN Links AS l ON m.movie_id = l.movie_id  
        WHERE 1=1
        """

        params = []

        if genre_names:
            genre_conditions = " OR ".join(["m.genres LIKE %s" for _ in genre_names])
            query += f" AND ({genre_conditions})"
            params.extend([f"%{genre}%" for genre in genre_names])

        query += " GROUP BY m.movie_id"

        if rating:
            query += " HAVING avg_rating >= %s"
            params.append(rating)

        query += " ORDER BY avg_rating DESC LIMIT 50"  # Reduce limit for faster results

        cursor.execute(query, params)
        movies = cursor.fetchall()

        # **Optimized Loop with Bulk API Calls**
        for movie in movies:
            movie["poster_url"] = get_poster_url(movie["tmdb_id"], movie["imdb_id"])

        execution_time = time.time() - start_time
        print(f"✅ Query executed in {execution_time:.2f} seconds")

        return render_template("result_table.html", movies=movies)

    except Exception as e:
        print("❌ Error:", str(e))
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)

