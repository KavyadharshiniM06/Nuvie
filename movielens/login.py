from flask import Flask, request, render_template, redirect, url_for, session, flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for session management

# Database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="hemni"
)

@app.route("/")
def home():
    return render_template("home.html")



@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_signup WHERE email = %s AND password_hash = %s", (email, password))
    user = cursor.fetchone()
    cursor.close()

    if user and check_password_hash(user["password_hash"], password):
        session["user_id"] = user["id"]  # Store user ID in session
        flash("Login successful!", "success")
        return redirect(url_for("dashboard"))  # Redirect to main page after login
    else:
        flash("Invalid email or password", "error")
        return redirect(url_for("home"))  # Reload login page with error message

@app.route("/dashboard")
def dashboard():
    if "user_id" in session:
        return render_template("/templates/main.html")
    flash("Please log in first", "error")
    return redirect(url_for("home")) 

if __name__ == "__main__":
    app.run(debug=True)
