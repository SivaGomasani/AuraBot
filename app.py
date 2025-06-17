

# Load predefined data
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
import os
import csv
from werkzeug.utils import secure_filename
import requests
from bs4 import BeautifulSoup
import pyttsx3
import logging
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
import random
from io import BytesIO


import random

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# In-memory chat history (for session-based simulation)
chat_histories = {}

def get_db_connection():
    """Establish a connection with signupDB.db"""
    conn = sqlite3.connect('signupDB.db')
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn


UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def create_tables():
    """Create users and user_history tables if they don't exist"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            dob TEXT,
            address TEXT,
            city TEXT,
            zipcode TEXT,
            profile_image TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            command TEXT,
            response TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()

# Ensure tables are created at startup
create_tables()

# Load predefined data
# Load predefined data
greetings_responses = {}
emoji_responses = {}
commands_dataset = []
base_path = os.path.dirname(__file__)

def load_csv_to_dict(file_path, key_field, value_field):
    result = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if key_field in row and value_field in row:
                    result[row[key_field].lower()] = row[value_field]
    except:
        pass
    return result

def load_csv_to_list(file_path, fields):
    result = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if all(field in row for field in fields):
                    result.append({"command": row[fields[0]], "response": row[fields[1]]})
    except:
        pass
    return result

greetings_responses = load_csv_to_dict(os.path.join(base_path, 'greetings.csv'), 'greeting', 'response')
emoji_responses = load_csv_to_dict(os.path.join(base_path, 'emoji.csv'), 'emoji', 'response')
commands_dataset = load_csv_to_list(os.path.join(base_path, 'questions.csv'), ['question', 'answer'])


def get_session_history(username):
    return chat_histories.setdefault(username, [])


from dotenv import load_dotenv
load_dotenv()
import os

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


def query_openai_assistant(prompt, username=None):
    messages = get_session_history(username)
    messages.append({"role": "user", "content": prompt})

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "http://localhost:5000",  # or your app URL
        "Content-Type": "application/json"
    }

    data = {
        "model": "mistralai/mistral-7b-instruct:free",
        "messages": messages,
        "max_tokens": 1024,
        "temperature": 0.7
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        if response.status_code == 200:
            text = response.json()["choices"][0]["message"]["content"]
            messages.append({"role": "assistant", "content": text})
            return text
        else:
            return f"[HTTP {response.status_code}] {response.text}"
    except Exception as e:
        return f"[Error] {str(e)}"

    
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    
def get_wikipedia_info(query):
    return query_openai_assistant(f"Explain briefly: {query}")
    

def get_exchange_rate(base_currency, target_currency):
    return query_openai_assistant(f"What is the exchange rate from {base_currency} to {target_currency}?")

def get_random_joke():
    return query_openai_assistant("Tell me a short and funny joke.")


def get_random_quote():
    return query_openai_assistant("Give me one short inspirational quote with author name.")


def get_random_joke():
    return query_openai_assistant("Tell me a short and funny joke.")


def get_random_quote():
    return query_openai_assistant("Give me one short inspirational quote with author name.")


def translate_to_english(text):
    return query_openai_assistant(f"Translate to English: {text}")


def perform_translation(text, dest_lang='en'):
    return query_openai_assistant(f"Translate this to {dest_lang}: {text}")


def fetch_image(query):
    search_url = f"https://www.google.com/search?hl=en&tbm=isch&q={query}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(search_url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find_all('img')
        image_paths = []
        for idx, img in enumerate(images):
            img_url = img.get('src')
            if img_url and img_url.startswith('http'):
                try:
                    img_data = requests.get(img_url).content
                    filename = f"image_{idx}.jpg"
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    with open(filepath, "wb") as f:
                        f.write(img_data)
                    image_paths.append(f"/static/uploads/{filename}")
                    if len(image_paths) >= 10:
                        break
                except Exception as e:
                    print(f"Image download error: {e}")
        return image_paths if image_paths else ["No valid image found."]
    return ["Error fetching image."]


@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session['username'] = username
            return redirect(url_for('start'))
        else:
            return "Invalid credentials. Please try again."

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            password = request.form.get('password')
            email = request.form.get('email')
            phone = request.form.get('phone')
            dob = request.form.get('dob')
            address = request.form.get('address')
            city = request.form.get('city')
            zipcode = request.form.get('zipcode')
            profile_image = request.files.get('profile_image')

            print(f"Received Data: {username}, {password}, {email}, {phone}, {dob}, {address}, {city}, {zipcode}, {profile_image}")

            # Hash the password
            hashed_password = generate_password_hash(password)

            conn = get_db_connection()
            cursor = conn.cursor()

            # Check if username already exists
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            existing_user = cursor.fetchone()
            if existing_user:
                conn.close()
                print("❌ Username already exists")
                return "Username already exists. Please choose a different one."

            filename = None
            if profile_image and allowed_file(profile_image.filename):
                filename = secure_filename(profile_image.filename)
                profile_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Insert user details into `users` table
            query = """ 
                INSERT INTO users (username, password, email, phone, dob, address, city, zipcode, profile_image)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            values = (username, hashed_password, email, phone, dob, address, city, zipcode, filename)

            cursor.execute(query, values)
            conn.commit()
            conn.close()

            print("✅ Data inserted successfully!")
            return redirect(url_for('login'))

        except sqlite3.Error as err:
            print("❌ Database error:", err)
            return f"Database error: {err}"
        except Exception as e:
            print("❌ Unexpected error:", e)
            return f"Unexpected error: {e}"

    return render_template('signup.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return 'File successfully uploaded'
    
    return 'File type not allowed'

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()

    if request.method == 'POST':
        email = request.form['email']
        phone = request.form['phone']
        dob = request.form['dob']
        address = request.form['address']
        city = request.form['city']
        zipcode = request.form['zipcode']
        profile_image = request.files.get('profile_image')

        if profile_image and allowed_file(profile_image.filename):
            filename = secure_filename(profile_image.filename)
            profile_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            cursor.execute("UPDATE users SET profile_image=? WHERE username=?", (filename, username))

        cursor.execute(""" 
            UPDATE users 
            SET email=?, phone=?, dob=?, address=?, city=?, zipcode=? 
            WHERE username=?
        """, (email, phone, dob, address, city, zipcode, username))

        conn.commit()
        conn.close()
        return redirect(url_for('profile'))

    conn.close()
    return render_template('profile.html', user=user)

@app.route('/profile_image/<username>')
def profile_image(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT profile_image FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and user["profile_image"]:  
        return send_file(BytesIO(user["profile_image"]), mimetype='image/jpeg')  # Serve image as file
    else:
        return send_file("static/default-profile.png", mimetype='image/png')  # Fallback image

@app.route('/update_profile', methods=['POST'])
def update_profile():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))

    email = request.form['email']
    phone = request.form['phone']
    dob = request.form['dob']
    address = request.form['address']
    city = request.form['city']
    zipcode = request.form['zipcode']
    profile_image = request.files.get('profile_image')

    conn = get_db_connection()
    cursor = conn.cursor()

    if profile_image and profile_image.filename != '':
        image_data = profile_image.read()  # Read file as binary
        cursor.execute("UPDATE users SET profile_image=? WHERE username=?", (sqlite3.Binary(image_data), username))

    cursor.execute("""
        UPDATE users SET email=?, phone=?, dob=?, address=?, city=?, zipcode=? 
        WHERE username=?
    """, (email, phone, dob, address, city, zipcode, username))
    
    conn.commit()
    conn.close()
    return redirect(url_for('profile'))


@app.route('/start')
def start():
    username = session.get('username')
    if username:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cursor.fetchone()
        conn.close()
        return render_template('index.html', user=user)
    else:
        return redirect(url_for('login'))



@app.route('/api/chat', methods=['POST'])
def api_chat():
    command = request.json.get('command')
    username = session.get('username')

    if not username:
        return jsonify({'error': 'User not logged in'})

    try:
        response = query_openai_assistant(command, username)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username=?", (username,))
        user = cursor.fetchone()
        if user:
            user_id = user['id']
            cursor.execute("INSERT INTO user_history (user_id, command, response) VALUES (?, ?, ?)",
                           (user_id, command, response))
            conn.commit()
        conn.close()
        return jsonify({'response': response})
    except Exception as e:
        logging.error(f"Chat error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/translate', methods=['POST'])
def api_translate():
    data = request.json
    text = data.get('text')
    target_language = data.get('targetLanguage', 'en')
    username = session.get('username')

    try:
        translation_prompt = f"Translate this to {target_language}: {text}"
        translated = query_openai_assistant(translation_prompt, username)
        return jsonify({"translatedText": translated})
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/logout')
def logout():
    username = session.get('username')
    if username:
        logging.info(f"User '{username}' logged out.")
    else:
        logging.warning("Logout attempted with no user logged in.")
    
    session.pop('username', None)  # Remove username from session
    return redirect(url_for('login'))

@app.route('/api/set_voice_gender', methods=['POST'])
def set_voice_gender():
    try:
        data = request.json
        selected_gender = data.get('gender', 'male')
        logging.debug(f"Setting voice gender to: {selected_gender}")
        session['voice_gender'] = selected_gender
        return jsonify({'gender': selected_gender})
    except Exception as e:
        logging.error(f"Error setting voice gender: {e}")
        return jsonify({'error': str(e)}), 500

def set_voice(engine, gender):
    voices = engine.getProperty('voices')
    selected_voice = None

    # Set specific voice IDs based on your system's available voices
    male_voice_id = 'com.apple.speech.synthesis.voice.Alex'  # Replace with actual male voice ID
    female_voice_id = 'com.apple.speech.synthesis.voice.Victoria'  # Replace with actual female voice ID

    logging.debug(f"Available voices: {[voice.id for voice in voices]}")
    
    if gender == 'male':
        engine.setProperty('voice', male_voice_id)
        logging.debug(f"Set voice to male: {male_voice_id}")
    elif gender == 'female':
        engine.setProperty('voice', female_voice_id)
        logging.debug(f"Set voice to female: {female_voice_id}")

@app.route('/api/speak', methods=['POST'])
def speak_endpoint():
    try:
        data = request.json
        text = data.get('text', '')
        gender = session.get('voice_gender', 'male')
        
        engine = pyttsx3.init()
        set_voice(engine, gender)
        
        # Log the current voice settings
        current_voice = engine.getProperty('voice')
        logging.debug(f"Current voice set to: {current_voice}")
        
        engine.say(text)
        engine.runAndWait()

        return jsonify({'status': 'success', 'message': 'Text spoken successfully.'})
    except Exception as e:
        logging.error(f"Error speaking text: {e}")
        return jsonify({'error': str(e)}), 500
    
@app.route('/policy')
def policy():
    return render_template('policy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/api/toggle_child_mode', methods=['POST'])
def toggle_child_mode():
    current_status = session.get('child_mode', False)
    session['child_mode'] = not current_status
    return jsonify({'child_mode': session['child_mode']})

@app.route('/translate', methods=['POST'])
def translate():
    data = request.json
    text = data.get('text')
    target_language = data.get('targetLanguage', 'en')

    try:
        translator = Translator()
        translated = translator.translate(text, dest=target_language)
        translated_text = translated.text
        
        # Speak the translated text
        speak(translated_text)
        return jsonify({"translatedText": translated.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/history')
def history():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE username=?", (username,))
    user = cursor.fetchone()

    if user:
        user_id = user['id']
        cursor.execute("SELECT command, response, timestamp FROM user_history WHERE user_id=? ORDER BY timestamp DESC", (user_id,))
        history = cursor.fetchall()
        conn.close()
        return render_template('history.html', history=history, random=random.random)
    else:
        conn.close()
        return redirect(url_for('login'))

import os

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
        
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)


 