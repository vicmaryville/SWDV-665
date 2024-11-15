from flask import Flask, request, render_template
import os
import psycopg2

app = Flask(__name__)

# Load database credentials from environment variables
DB_HOST = os.environ.get("DB_HOST")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")

# Connect to the database
conn = psycopg2.connect(
    host=DB_HOST,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASS
)
cur = conn.cursor()

@app.route('/')
def index():
    # Fetch some data from the database
    cur.execute("SELECT * FROM users LIMIT 10")
    users = cur.fetchall()
    return render_template('index.html', users=users)

@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        email = request.form['email']
        
        # Insert the new user into the database
        cur.execute("INSERT INTO users (name, email) VALUES (%s, %s)", (name, email))
        conn.commit()
        return "User created successfully"
    return render_template('create_user.html')

if __name__ == '__main__':
    app.run(debug=True)
