from flask import Blueprint, request, jsonify
from api.model import predict_response

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('query')
    response = predict_response(user_input)
    return jsonify({'response': response})
