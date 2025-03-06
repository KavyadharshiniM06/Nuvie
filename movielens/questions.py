from flask import Flask, request, render_template
import os;

app = Flask(__name__,template_folder="templates")

@app.route('/')
def index():
    return render_template("questions.html")  
@app.route('/submit', methods=['POST'])
def submit():
    print(request.form)
    genres = request.form.getlist("genre")
    moods = request.form.getlist("mood")
    popularity = request.form.get("popularity")
    rating = request.form.get("rating")

    user_preferences = {
        "Genres": genres,
        "Moods": moods,
        "Popularity": popularity,
        "Minimum IMDb Rating": rating
    }

    print(user_preferences)

    return f"Preferences saved successfully! {user_preferences}"

if __name__ == "__main__":
    app.run(debug=True)
