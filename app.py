import os
import sqlite3
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
# Enable CORS
CORS(app)

DB_FILE = "submissions.db"

def init_db():
    """Initializes the SQLite database and creates the submissions table if it doesn't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            film_name TEXT NOT NULL,
            film_release_year TEXT NOT NULL,
            actor_name TEXT NOT NULL,
            film_language TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Initialize DB on startup
init_db()

@app.route('/')
def serve_form():
    """Serves the movie_form.html directly from the current directory."""
    return send_from_directory('.', 'movie_form.html')

@app.route('/admin')
def serve_admin():
    """Serves the admin dashboard page."""
    return send_from_directory('.', 'admin.html')

@app.route('/api/submit', methods=['POST'])
def submit_form():
    """
    Receives form data and saves it to the SQLite database.
    """
    data = request.json
    
    film_name = data.get('filmName', '')
    film_year = data.get('filmReleaseYear', '')
    actor_name = data.get('actorName', '')
    film_language = data.get('filmLanguage', '')

    if not all([film_name, film_year, actor_name, film_language]):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT INTO submissions (film_name, film_release_year, actor_name, film_language) VALUES (?, ?, ?, ?)',
            (film_name, film_year, actor_name, film_language)
        )
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Submission saved successfully'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/submissions', methods=['GET'])
def get_submissions():
    """
    Returns all submissions from the database.
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row  # This enables column access by name
        cursor = conn.cursor()
        
        # Get all records ordered by newest first
        cursor.execute('SELECT * FROM submissions ORDER BY created_at DESC')
        rows = cursor.fetchall()
        
        submissions = []
        for row in rows:
            submissions.append({
                'id': row['id'],
                'filmName': row['film_name'],
                'filmReleaseYear': row['film_release_year'],
                'actorName': row['actor_name'],
                'filmLanguage': row['film_language'],
                'createdAt': row['created_at']
            })
            
        conn.close()
        
        return jsonify({'success': True, 'data': submissions})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Flask server with SQLite Backend...")
    print("User Form: http://localhost:8080/")
    print("Admin Dashboard: http://localhost:8080/admin")
    app.run(debug=True, port=8080)
