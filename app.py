from flask import Flask, request, jsonify
import random
import requests
import tensorflow as tf
from tensorflow.keras.models import load_model
import numpy as np
import openai

url = "https://huggingface.co/ry3en/tweet_emotion_detection/resolve/main/model_text.h5"
response = requests.get(url)

with open("model_text.h5", "wb") as f:
    f.write(response.content)

url_img = "https://huggingface.co/ry3en/tweet_emotion_detection/resolve/main/model.h5"
response_img = requests.get(url)

with open("model.h5", "wb") as f:
    f.write(response_img.content)

# Configura tu clave de API de OpenAI
openai.api_key = "TU_CLAVE_API_AQUI"

# Cargar los modelos
model_text = load_model("model_text.h5")
model_image = load_model("model.h5")

# Definir emociones
EMOTIONS = ['Enojo', 'Disgusto', 'Miedo', 'Felicidad', 'Tristeza', 'Sorpresa', 'Neutral']

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Servidor de detección de emociones activo'

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Verificar que se envíen datos válidos
        if not request.json or 'text' not in request.json or 'image_data' not in request.json:
            return jsonify({'error': 'Se requiere texto y datos de imagen'}), 400
        
        text = request.json['text']
        image_data = request.json['image_data']  # Asume que es una cadena codificada en base64

        # Preprocesar texto e imagen (ajusta según los requisitos de tus modelos)
        text_input = np.array([text])  # Supongamos que el modelo puede procesar texto sin tokenización
        image_input = np.random.rand(1, 224, 224, 3)  # Sustituye con la decodificación de image_data

        # Obtener predicciones de los modelos
        probs_text = model_text.predict(text_input)[0]
        probs_image = model_image.predict(image_input)[0]

        # Seleccionar emociones con mayor probabilidad
        emotion_text = EMOTIONS[np.argmax(probs_text)]
        emotion_image = EMOTIONS[np.argmax(probs_image)]

        # Consultar ChatGPT para recomendaciones
        chatgpt_prompt = (
            f"Una persona está sintiendo {emotion_text} y {emotion_image}. "
            "¿Qué recomendación le darías para manejar estas emociones?"
        )

        chatgpt_response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=chatgpt_prompt,
            max_tokens=100
        )

        # Extraer respuesta generada
        recommendation = chatgpt_response.choices[0].text.strip()

        # Construir la respuesta
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
