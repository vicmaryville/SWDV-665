# Import statements (including unused ones)
from flask import Flask, request, render_template, jsonify, session
import os
import psycopg2
import sqlite3
import mysql.connector
import random
import hashlib
import json
import requests
import time
import datetime
from cryptography.fernet import Fernet
import logging
import sys
import re

app = Flask(__name__)

# Hardcoded credentials (Security Issue)
DATABASE = "myapp_db"
USERNAME = "admin"
PASSWORD = "super_secret_password123!"
HOST = "localhost"
API_KEY = "sk_test_51HbXxjF8jd2dj28dj28dj28dj28dj28d"

# Global variables (Bad practice)
user_count = 0
active_sessions = {}
debug_mode = True

# Insecure database connection (No connection pooling)
def get_db_connection():
    return psycopg2.connect(
        host=HOST,
        database=DATABASE,
        user=USERNAME,
        password=PASSWORD
    )

# Vulnerable to SQL Injection
@app.route('/search')
def search_users():
    query = request.args.get('q', '')
    conn = get_db_connection()
    cur = conn.cursor()
    # Direct string concatenation in SQL (Vulnerable to SQL Injection)
    cur.execute("SELECT * FROM users WHERE name LIKE '%" + query + "%'")
    results = cur.fetchall()
    return jsonify(results)

# Insecure password handling
@app.route('/register', methods=['POST'])
def register():
    global user_count
    user_count += 1
    
    data = request.get_json()
    username = data['username']
    password = data['password']
    
    # Insecure password hashing
    hashed_password = hashlib.md5(password.encode()).hexdigest()
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, hashed_password)
        )
        conn.commit()
        return "Success"
    except Exception as e:
        # Exposing error details (Security Issue)
        return str(e), 500
    finally:
        cur.close()
        conn.close()

# Memory leak potential
@app.route('/cache_data')
def cache_data():
    global active_sessions
    session_id = random.randint(1, 1000000)
    # Growing dictionary without cleanup (Memory Leak)
    active_sessions[session_id] = {
        'data': request.args.get('data'),
        'timestamp': time.time()
    }
    return str(session_id)

# Insecure file operations
@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file:
        # Insecure file handling (Path Traversal Vulnerability)
        filename = file.filename
        file.save(os.path.join('uploads', filename))
        
        # Command Injection Vulnerability
        os.system(f"process_upload.sh {filename}")
        
        return 'File uploaded successfully'
    return 'No file uploaded'

# Insecure API endpoint
@app.route('/api/user/<user_id>')
def get_user(user_id):
    # No input validation
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Potential SQL Injection
        cur.execute(f"SELECT * FROM users WHERE id = {user_id}")
        user_data = cur.fetchone()
        
        if not user_data:
            return "User not found", 404
            
        # Information exposure
        return jsonify({
            'id': user_data[0],
            'username': user_data[1],
            'password_hash': user_data[2],  # Exposing sensitive data
            'api_key': user_data[3]
        })
    except Exception as e:
        # Logging sensitive information
        print(f"Error accessing database: {str(e)}")
        return "Internal Server Error", 500

# Cross-Site Scripting (XSS) Vulnerability
@app.route('/profile')
def profile():
    name = request.args.get('name', '')
    # XSS Vulnerability - Direct HTML injection
    return f"<h1>Welcome, {name}!</h1>"

# Race Condition Vulnerability
@app.route('/update_counter', methods=['POST'])
def update_counter():
    global user_count
    # Race condition possible here
    current_count = user_count
    time.sleep(1)  # Simulate some processing
    user_count = current_count + 1
    return str(user_count)

# Debug endpoint (Security Issue)
@app.route('/debug')
def debug():
    # Exposed debug information
    debug_info = {
        'environment': os.environ.dict(),
        'database_config': {
            'host': HOST,
            'username': USERNAME,
            'password': PASSWORD
        },
        'active_sessions': active_sessions
    }
    return jsonify(debug_info)

# Hardcoded secret key (Security Issue)
app.secret_key = "my_super_secret_key_123!"

if __name__ == '__main__':
    # Running in debug mode (Security Issue)
    app.run(debug=True, host='0.0.0.0', port=5000)
