import time
import traceback
from flask import Flask, jsonify, request, render_template
import mysql.connector
from tabulate import tabulate
import requests
from recommender import get_recommendations

app = Flask(__name__, template_folder="templates")  

@app.route('/recommend', methods=['POST'])
def recommend():
    movie_title = request.form.get('movie_title')
    recommendations = get_recommendations(movie_title)
    return render_template('results.html', movies=recommendations)

TMDB_API_KEY = "8ac3dbbfa63384187f38a7c4cfb0286e"
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="hemni",
        connection_timeout=60,
        autocommit=True
    )



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
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        start_time = time.time()

        genre_ids = request.form.getlist("genre")  # Get selected genre IDs
        print(f"Genre IDs selected: {genre_ids}")
        rating = request.form.get("rating", type=float)
        tags=request.form.getlist("tag")

        # Debug prints
        print(f"Genres selected: {genre_ids}")
        print(f"Rating filter: {rating}")

        query = """
        SELECT m.movie_id, m.title, m.genres, l.tmdb_id, l.imdb_id,GROUP_CONCAT(DISTINCT t.tag) AS tags,
               YEAR(FROM_UNIXTIME(MAX(r.timestamp))) AS rating_year,  
               COALESCE(AVG(r.rating), 0) AS avg_rating,
               SUBSTRING_INDEX(SUBSTRING_INDEX(m.title, '(', -1), ')', 1) AS release_year
        FROM movies AS m
        LEFT JOIN Ratings AS r ON m.movie_id = r.movie_id
        LEFT JOIN Links AS l ON m.movie_id = l.movie_id
        LEFT JOIN tags AS t ON m.movie_id = t.movie_id
        
        WHERE 1=1
        """

        params = []

        if genre_ids:
            genre_filters = []
            for genre in genre_ids:
                genre_filters.append(f"m.genres LIKE %s")
                params.append(f"%{genre}%")  # Adding the genre in the format '%genre%'
    
            # Join all the genre filters with 'OR' to allow matching any of the genres
            query += " AND (" + " OR ".join(genre_filters) + ")"

        if tags:
            tag_placeholders = ", ".join(["%s"] * len(tags))
            query += f" AND t.tag IN ({tag_placeholders})"
            params.extend(tags)
            print(tag_placeholders)
            print("Tags:", tags) 

        query += " GROUP BY m.movie_id, m.title, m.genres, l.tmdb_id, l.imdb_id "  # You can adjust the order here if needed

        # Add rating filter if provided
        if rating:
            query += " HAVING avg_rating >= %s"
            params.append(rating)

        query += " ORDER BY avg_rating DESC, rating_year DESC"  # Order by rating and year
        # Print the query for debugging
        print(f"Executing query: {query}")
        cursor.execute(query, params)
        movies = cursor.fetchall()

        # Debug print if movies were fetched
        print(f"Movies fetched: {len(movies)}")
        #movies attirbutes
        for movie in movies:
            movie["genres"] = [GENRE_MAP.get(genre_id, genre_id) for genre_id in movie["genres"].split(",")]
            movie["tags"] = movie["tags"].split(",") if movie["tags"] else []  # Split tags into a list
            movie["release_year"] = movie["release_year"] if movie["release_year"] else "Unknown"
            movie["avg_rating"] = round(movie["avg_rating"], 2) if movie["avg_rating"] else 0.0  # Round to 2 decimal places
            

        # **Optimized Loop with Bulk API Calls**
        for movie in movies:
            poster_url = get_poster_url(movie["tmdb_id"], movie["imdb_id"])
            if poster_url:
                movie["poster_url"] = poster_url  # Ensure poster is added only if valid

        execution_time = time.time() - start_time
        print(f"Query executed in {execution_time:.2f} seconds")

        return render_template("result_table.html", movies=movies)

    except Exception as e:
        print("Error:", str(e))
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
