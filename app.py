from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
import os
import csv
from werkzeug.utils import secure_filename
import requests
from bs4 import BeautifulSoup
import wikipediaapi
from googletrans import Translator
import datetime
import geocoder
import pyttsx3
import logging
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
import sqlite3

import random

app = Flask(__name__)
app.secret_key = 'supersecretkey'


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

# Load responses dataset from CSV file
greetings_file = os.path.join(os.path.dirname(__file__), 'greetings.csv')
greetings_responses = {}
with open(greetings_file, 'r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        if 'greeting' in row and 'response' in row:
            greetings_responses[row["greeting"].lower()] = row["response"]

commands_file = os.path.join(os.path.dirname(__file__), 'questions.csv')
commands_dataset = []
with open(commands_file, 'r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        if 'question' in row and 'answer' in row:
            commands_dataset.append({
                "command": row["question"],
                "response": row["answer"]
            })

# Load emoji dataset from CSV file
emoji_file = os.path.join(os.path.dirname(__file__), 'emoji.csv')
emoji_responses = {}
with open(emoji_file, 'r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        if 'emoji' in row and 'response' in row:
            emoji_responses[row["emoji"]] = row["response"]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Wikipedia Function to fetch information
def get_wikipedia_info(query):
    wiki_wiki = wikipediaapi.Wikipedia(
        user_agent='MyApp/1.0 (your-email@example.com)',
        language='en'
    )
    page = wiki_wiki.page(query)
    if page.exists():
        return page.text[:2000]  # Fetching the first 2000 characters of the text
    else:
        return "No information found on Wikipedia."
    


def get_exchange_rate(base_currency, target_currency):
    base_url = f"https://open.er-api.com/v6/latest/{base_currency}"
    response = requests.get(base_url)
    if response.status_code == 200:
        rates = response.json().get('rates', {})
        if target_currency in rates:
            rate = rates[target_currency]
            return f"The exchange rate from {base_currency} to {target_currency} is {rate}."
        else:
            print(f"Target currency {target_currency} not found in rates.")
            return "Target currency not found."
    else:
        print("Exchange rate data could not be retrieved.")
        return "Exchange rate data could not be retrieved."

def get_random_joke():
    base_url = "https://official-joke-api.appspot.com/random_joke"
    response = requests.get(base_url)
    if response.status_code == 200:
        joke = response.json()
        return f"{joke['setup']} - {joke['punchline']}"
    else:
        return "Joke data could not be retrieved."

def get_random_quote():
    base_url = "https://api.quotable.io/random"
    response = requests.get(base_url)
    if response.status_code == 200:
        quote = response.json()
        return f"{quote['content']} - {quote['author']}"
    else:
        return "Quote data could not be retrieved."
    

from bs4 import BeautifulSoup


BeautifulSoup

#news fetching
translator = Translator()

def translate_to_english(text):
    try:
        translation = translator.translate(text, src='te', dest='en')
        return translation.text
    except Exception as e:
        return f"Translation error: {str(e)}"

def get_eenadu_news():
    url = "https://www.eenadu.net/telugu-news"
    response = requests.get(url)
    response.encoding = 'utf-8'  # Ensure proper encoding
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        headlines = soup.find_all('h2', limit=5)  # Ensure only the top 5 headlines
        news_items = []
        for headline in headlines:
            title = headline.text.strip()
            if title:
                summary = headline.find_next('p').text.strip() if headline.find_next('p') else "No summary available."
                translated_title = translate_to_english(title)
                translated_summary = translate_to_english(summary)
                news_items.append(f"{translated_title}\n{translated_summary}")
        return "Eenadu News:\n" + "\n\n".join(news_items)
    else:
        return "Eenadu news data could not be retrieved."

def get_sakshi_news():
    url = "https://www.sakshi.com/"
    response = requests.get(url)
    response.encoding = 'utf-8'  # Ensure proper encoding
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        headlines = soup.find_all('h2', limit=5)  # Ensure only the top 5 headlines
        news_items = []
        for headline in headlines:
            title = headline.text.strip()
            if title:
                summary = headline.find_next('p').text.strip() if headline.find_next('p') else "No summary available."
                translated_title = translate_to_english(title)
                translated_summary = translate_to_english(summary)
                news_items.append(f"{translated_title}\n{translated_summary}")
        return "Sakshi News:\n" + "\n\n".join(news_items)
    else:
        return "Sakshi news data could not be retrieved."

def get_andhra_jyothi_news():
    url = "https://www.andhrajyothy.com/"
    response = requests.get(url)
    response.encoding = 'utf-8'  # Ensure proper encoding
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        headlines = soup.find_all('h2', limit=5)  # Ensure only the top 5 headlines
        news_items = []
        for headline in headlines:
            title = headline.text.strip()
            if title:
                summary = headline.find_next('p').text.strip() if headline.find_next('p') else "No summary available."
                translated_title = translate_to_english(title)
                translated_summary = translate_to_english(summary)
                news_items.append(f"{translated_title}\n{translated_summary}")
        return "Andhra Jyothi News:\n" + "\n\n".join(news_items)
    else:
        return "Andhra Jyothi news data could not be retrieved."

def get_telugu_news():
    eenadu_news = get_eenadu_news()
    sakshi_news = get_sakshi_news()
    andhra_jyothi_news = get_andhra_jyothi_news()
    return f"{eenadu_news}\n\n{sakshi_news}\n\n{andhra_jyothi_news}"
# Function to translate text
from googletrans import Translator

def perform_translation(text, dest_lang='te'):
    try:
        translator = Translator()
        translated = translator.translate(text, dest=dest_lang)

        # Ensure we correctly extract the translated text
        if translated and hasattr(translated, 'text'):
            return translated.text
        else:
            return "Translation failed: Invalid response format."
    
    except Exception as e:
        return f"Translation failed: {str(e)}"

# Function to fetch images using Google Image search (scraping)
def fetch_image(query):
    search_url = f"https://www.google.com/search?hl=en&tbm=isch&q={query}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

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

                    if len(image_paths) >= 10:  # Stop after getting 10 images
                        break
                except Exception as e:
                    print(f"Error downloading image: {e}")

        return image_paths if image_paths else ["No valid image found."]
    else:
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
    global previous_query, previous_response
    
    command = request.json.get('command').lower()
    response = ""

    try:
        if session.get('child_mode', False):
            response = command
        elif command in emoji_responses:
            response = emoji_responses[command]
        elif command in greetings_responses:
            response = greetings_responses[command]
        elif "translate" in command:
            parts = command.rsplit(" to ", 1)
            if len(parts) == 2:
                text_to_translate = parts[0].replace("translate ", "").strip()
                target_lang = parts[1].strip()
                response = perform_translation(text_to_translate, target_lang)
        elif "time" in command:
            current_time = datetime.datetime.now().strftime('%H:%M:%S')
            response = f"The current time is {current_time}."
        elif "date" in command:
            current_date = datetime.datetime.now().strftime('%Y-%m-%d')
            response = f"Today's date is {current_date}."
        elif "day" in command:
            current_day = datetime.datetime.now().strftime('%A')
            response = f"Today is {current_day}."
        elif "location" in command:
            g = geocoder.ip('me')
            location = g.city if g.city else "Location not found"
            response = f"Your current location is {location}."
        elif command.startswith("image "):
            search_term = command[6:]
            image_paths = fetch_image(search_term)
            response = {"images": image_paths}
        elif command.startswith("exchange rate "):
            parts = command.split(" to ")
            if len(parts) == 2:
                base_currency = parts[0].replace("exchange rate ", "").strip()
                target_currency = parts[1].strip()
                response = get_exchange_rate(base_currency, target_currency)
            else:
                response = "Please provide a valid command in the format 'exchange rate USD to INR'."
        elif "joke" in command or "make me laugh" in command:
            response = get_random_joke()
        elif "quote" in command or "inspirational quote" in command:
            response = get_random_quote()
        elif "news" in command:
            response = get_telugu_news()
        elif command.startswith("weather"):
            parts = command.split()
            if len(parts) == 3:
                lat = float(parts[1])
                lon = float(parts[2])
                response = get_weather(lat, lon)
            else:
                response = "Please provide latitude and longitude in the format 'weather lat lon'."
        elif "more" in command or "continue" in command:
            response = previous_response
        else:
            query_response = next((item['response'] for item in commands_dataset if item['command'].lower() in command), None)
            if not query_response:
                query_response = get_wikipedia_info(command)
            if "No information found on Wikipedia" in query_response:
                response = "Command not recognized or could not be processed."
            else:
                response = query_response

        # Store the previous query and response
        previous_query = command
        previous_response = response

        # Ensure user is logged in
        username = session.get('username')
        if not username:
            return jsonify({'error': 'User not logged in'})

        # Get user ID from the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username=?", (username,))
        user = cursor.fetchone()

        if user:
            user_id = user['id']
            logging.debug(f"User ID: {user_id}")  # Log user ID for debugging

            # Insert into user history
            cursor.execute("INSERT INTO user_history (user_id, command, response) VALUES (?, ?, ?)", 
                           (user_id, command, response))
            conn.commit()
            logging.debug("History saved successfully")  # Log success
        else:
            logging.error("User not found")  # Log error if user not found

        conn.close()

        # Debugging: Log the command and response
        logging.debug(f"Command: {command}")
        logging.debug(f"Response: {response}")

        return jsonify({'response': response})

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return jsonify({'error': str(e)}), 500


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


if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
