from flask import Flask, request, jsonify
import random
import requests
import tensorflow as tf
import numpy as np
import openai  # Use the old import style
import os

app = Flask(__name__)

# Download and save models
url = "https://huggingface.co/ry3en/tweet_emotion_detection/resolve/main/model_text.h5"
url_img = "https://huggingface.co/ry3en/tweet_emotion_detection/resolve/main/model.h5"

response = requests.get(url)
response_img = requests.get(url_img)

with open("model_text.h5", "wb") as f:
    f.write(response.content)
    
with open("model.h5", "wb") as f:
    f.write(response_img.content)

# Load models
try:
    model_text = tf.keras.models.load_model("model_text.h5")
    model_image = tf.keras.models.load_model("model.h5")
except Exception as e:
    print(f"Error loading models: {e}")

# Configure OpenAI (old style)
openai.api_key = "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"

# Define emotions
EMOTIONS = ['Enojo', 'Disgusto', 'Miedo', 'Felicidad', 'Tristeza', 'Sorpresa', 'Neutral']

@app.route('/')
def hello_world():
    return 'Servidor de detección de emociones activo'

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Verify valid data
        if not request.json or 'text' not in request.json or 'image_data' not in request.json:
            return jsonify({'error': 'Se requiere texto y datos de imagen'}), 400

        text = request.json['text']
        image_data = request.json['image_data']

        # Preprocess inputs
        text_input = np.array([text])
        image_input = np.random.rand(1, 224, 224, 3)  # Replace with actual image processing

        # Get predictions
        probs_text = model_text.predict(text_input)[0]
        probs_image = model_image.predict(image_input)[0]

        # Select emotions
        emotion_text = EMOTIONS[np.argmax(probs_text)]
        emotion_image = EMOTIONS[np.argmax(probs_image)]

        # Get ChatGPT recommendation using old API style
        chatgpt_prompt = (
            f"Una persona está sintiendo {emotion_text} y {emotion_image}. "
            f"¿Qué recomendación le darías para manejar estas emociones?, esto escribio: {text_input}"
        )

        chatgpt_response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=chatgpt_prompt,
            max_tokens=100
        )

        recommendation = chatgpt_response.choices[0].text.strip()

        # Build response
        result = {
            'emotion_text': emotion_text,
            'emotion_image': emotion_image,
            'probabilities_text': {emotion: round(prob, 4) for emotion, prob in zip(EMOTIONS, probs_text)},
            'probabilities_image': {emotion: round(prob, 4) for emotion, prob in zip(EMOTIONS, probs_image)},
            'recommendation': recommendation
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
