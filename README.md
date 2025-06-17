# 🧠 Aurabot: Interactive Voice & Chat Assistant

Aurabot is a full-stack **Flask web application** that enables intelligent, voice-supported and chat-based interaction. It supports **user authentication**, **file/image uploads**, **news, translation, weather**, **Wikipedia search**, and more.

---

## 🚀 Live Demo

🌐 [Aurabot is Live Here](https://aurabot-wdp2.onrender.com)

---

## 📸 Features

- 🔐 **User Sign Up & Login** with profile picture
- 💬 **Smart Chat Assistant** with:
  - Greetings, emojis, and common Q&A
  - Wikipedia integration
  - Voice output (TTS – local only)
- 🌐 **Translation** via LibreTranslate
- 📰 **Live Telugu News** from Eenadu, Sakshi, AndhraJyothi
- 🏙️ **Location detection**
- 🌦️ **Weather info** (by latitude/longitude)
- 😂 **Random Jokes**, 📜 Quotes
- 🖼️ **Image Search** via Google
- 🧠 **Chat history per user**
- 👶 **Child Mode Toggle** for safe interaction

---

## ⚙️ Technologies Used

- **Backend**: Python Flask, SQLite
- **Frontend**: HTML, CSS, Jinja2 Templates
- **APIs**:
  - Wikipedia API
  - LibreTranslate (via `requests`)
  - Geocoder (IP-based location)
  - Public news scraping (via `BeautifulSoup`)
  - Exchange Rate API
  - Joke & Quote APIs

---

## 📁 Project Structure

aurabot/
├── app.py
├── requirements.txt
├── runtime.txt
├── render.yaml
├── templates/
│ ├── login.html
│ ├── signup.html
│ └── index.html
├── static/
│ └── uploads/
├── emoji.csv
├── greetings.csv
├── questions.csv
└── signupDB.db (auto-created)

yaml
Copy code

---

## 🛠️ Local Development Setup

1. Clone the repo:
   ```bash
   git clone https://github.com/yourusername/aurabot.git
   cd aurabot
Create and activate virtual environment:

bash
Copy code
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies:

bash
Copy code
pip install -r requirements.txt
Run the app:

bash
Copy code
python app.py
Visit http://127.0.0.1:5000/ in your browser

🌍 Deployment on Render
Push code to GitHub

Make sure these files are included:

requirements.txt

runtime.txt with python-3.11.8

(optional) render.yaml

On Render.com:

New Web Service → Connect GitHub

Set Start Command: python app.py

Click Manual Deploy → Clear Build Cache → Deploy

⚠️ Known Limitations
pyttsx3 (text-to-speech) only works on local machines, not in Render/cloud

Free-tier Render services sleep after ~15 mins of inactivity

📜 License
This project is licensed under the MIT License.

