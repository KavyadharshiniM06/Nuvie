from flask import Flask, request, render_template, jsonify
import traceback
import mysql.connector
import requests
from recommender import get_recommendations
from utils import get_poster_url
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

TMDB_API_KEY = "5b3ac94c5cb2bc8b5e010970c6f4fb61"
session_id = "faced90c23716af0d08504a519d209b7b1db06ee"###

GENRE_MAP = {
    "10749": "Romance", "28": "Action", "12": "Adventure", "16": "Animation",
    "35": "Comedy", "80": "Crime", "18": "Drama", "14": "Fantasy", "27": "Horror",
    "9648": "Mystery", "878": "Sci-Fi", "53": "Thriller", "10402": "Music",
    "10751": "Family", "36": "History", "10752": "War", "37": "Western"
}

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="hemni"
    )

def get_poster_url(tmdb_id, imdb_id=None):
    try:
        url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={TMDB_API_KEY}&session_id={session_id}"
        response = requests.get(url,timeout=5)
        data = response.json()

        poster_path = data.get("poster_path")
        vote_average = data.get("vote_average")
        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None

        return {
            "poster_url": poster_url,
            "tmdb_rating": vote_average
        }

    except Exception as e:
        print(f"Error fetching TMDb data for ID {tmdb_id}: {e}")
        return {
            "poster_url": None,
            "tmdb_rating": None
        }

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/questions')
def questions():
    return render_template("questions.html")
from contextlib import contextmanager

@contextmanager
def transactional_connection():
    db = get_db_connection()
    try:
        db.start_transaction()
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()


@app.route('/submit', methods=['POST'])
def submit():
    cursor = None
    try:
        with transactional_connection() as db:
            cursor = db.cursor(dictionary=True)

            genre_names = request.form.getlist("genre")
            rating = request.form.get("rating", type=float)
            year_range = request.form.get("year_range")
            tags = request.form.getlist("tag")

            insert_pref_query = """
                INSERT INTO user_preferences (genres, rating, year_range, tags)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert_pref_query, (
                ",".join(genre_names),
                rating,
                year_range,
                ",".join(tags)
            ))

            query = """
            SELECT m.movie_id, m.title, m.genres, l.tmdb_id, l.imdb_id,
            GROUP_CONCAT(DISTINCT t.tag) AS tags,
            SUBSTRING_INDEX(SUBSTRING_INDEX(m.title, '(', -1), ')', 1) AS release_year
            FROM movies AS m
            LEFT JOIN Links AS l ON m.movie_id = l.movie_id
            LEFT JOIN tags AS t ON m.movie_id = t.movie_id
            WHERE 1=1
            """
            params = []

            if genre_names:
                genre_conditions = " OR ".join(["m.genres LIKE %s" for _ in genre_names])
                query += f" AND ({genre_conditions})"
                params.extend([f"%{genre}%" for genre in genre_names])

            if tags:
                tag_placeholders = ", ".join(["%s"] * len(tags))
                query += f" AND t.tag IN ({tag_placeholders})"
                params.extend(tags)

            if year_range and year_range != "any":
                try:
                    start_year, end_year = map(int, year_range.split('-'))
                    query += " AND CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(m.title, '(', -1), ')', 1) AS UNSIGNED) BETWEEN %s AND %s"
                    params.extend([start_year, end_year])
                except ValueError:
                    pass

            query += " GROUP BY m.movie_id"

            cursor.execute(query, params)
            movies = cursor.fetchall()

        # Now outside transaction → run concurrent TMDb API fetches
        def enrich_movie(movie):
            tmdb_data = get_poster_url(movie["tmdb_id"], movie["imdb_id"])
            movie["poster_url"] = tmdb_data["poster_url"]
            movie["avg_rating"] = tmdb_data["tmdb_rating"]
            return movie

        with ThreadPoolExecutor(max_workers=5) as executor:
            enriched_movies = list(executor.map(enrich_movie, movies))

        filtered_movies = [
            m for m in enriched_movies
            if rating is None or (m["avg_rating"] and m["avg_rating"] >= rating)
        ]

        filtered_movies.sort(key=lambda x: x["avg_rating"] or 0, reverse=True)
        filtered_movies = filtered_movies[:50]

        return render_template("result_table.html", movies=filtered_movies)

    except Exception as e:
        print("Transaction failed or API error:", str(e))
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()


@app.route('/recommend', methods=['GET', 'POST'])
def recommend():
    
    recommended = []
    selected_movie = None

    if request.method == 'POST':
        selected_movie = request.form.get('movie')
        recommended_movies = get_recommendations(selected_movie)
        
        for rec in recommended_movies:
            tmdb_data = get_poster_url(tmdb_id=rec.get('tmdb_id'))
            rec['poster_url'] = tmdb_data["poster_url"]
            rec['avg_rating'] = round(tmdb_data["tmdb_rating"], 1) if tmdb_data["tmdb_rating"] is not None else None
            rec['tmdb_genres'] = rec.get('tmdb_genres', [])
        recommended = recommended_movies
        print(f"Recommended movies for {selected_movie}: {recommended}")
        
    return render_template('recommend.html', recommended=recommended, selected_movie=selected_movie)

@app.route('/test')
def test():
    return render_template("result_table.html", movies=[{
        "title": "Test Movie", "genre": "Romance", "release_year": 2023,
        "avg_rating": 4.5, "poster_url": "https://via.placeholder.com/300"
    }])



if __name__ == "__main__":
    app.run(debug=True)
