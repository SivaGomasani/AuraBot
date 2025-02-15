import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
import json

# Load model and tokenizer
model = tf.keras.models.load_model('model/chatbot_model.h5')
with open('model/tokenizer.json', 'r') as f:
    tokenizer_data = json.load(f)
    tokenizer = tf.keras.preprocessing.text.tokenizer_from_json(tokenizer_data)

responses = ["The current time is 3 PM.", "Why don’t scientists trust atoms? Because they make up everything!", "It's sunny with a temperature of 25°C."]

def predict_response(user_input):
    seq = tokenizer.texts_to_sequences([user_input])
    padded_seq = pad_sequences(seq, maxlen=10)
    pred = model.predict(padded_seq)
    response_index = pred.argmax(axis=-1)[0]
    return responses[response_index]
