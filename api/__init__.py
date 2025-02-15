from flask import Flask
from api.chat import chat_bp

def create_app():
    app = Flask(__name__)
    
    # Register blueprints
    app.register_blueprint(chat_bp, url_prefix='/api')
    
    # Additional configuration can go here

    return app
