from flask import Flask, request, render_template
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

conn=mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="hemni"
    )
cursor=conn.cursor()

@app.route('/main')
def main():
    return render_template('main.html')

@app.route('/')
def index():
    return render_template("signup.html") 

@app.route('/submit', methods=['POST'])
def submit():
    print(request.form)
    email=request.form.get("email")
    username=request.form.get("username")
    password=request.form.get("password")
    hashed_password = generate_password_hash(password)

    '''user_cred={
        "Email":email,
        "Username":username,
        "Password":password
    
    }
    print(user_cred)
    return f"User details saved successfully! {user_cred}"'''

    
    insert_query="insert into user_signup(username, email, password_hash, created_at) VALUES (%s, %s, %s, NOW())"
    values=(username, email, hashed_password)

    cursor.execute(insert_query,values)

    conn.commit()
    return "User registered successfully!"



if __name__=="__main__":
    app.run(debug=True)