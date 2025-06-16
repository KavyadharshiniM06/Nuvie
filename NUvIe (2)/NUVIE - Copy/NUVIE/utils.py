import requests
import  pandas as pd
TMDB_API_KEY = "6cb34dee61156c0fd756471e19d70823"

poster_cache = {}
details_cache = {}

def get_movie_details(tmdb_id):
    if pd.isna(tmdb_id):
        return {}
    if tmdb_id in details_cache:
        return details_cache[tmdb_id]

    url = f"https://api.themoviedb.org/3/movie/{int(tmdb_id)}?api_key={TMDB_API_KEY}&language=en-US"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        details = {
            "rating": data.get("vote_average"),
            "overview": data.get("overview"),
            "release_date": data.get("release_date"),
            "genres": [g['name'] for g in data.get("genres", [])]
        }
        details_cache[tmdb_id] = details
        return details
    else:
        return {}

def get_poster_url(tmdb_id=None, imdb_id=None):
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
            poster_cache[tmdb_id or imdb_id] = poster_url
            return poster_url

    return None
