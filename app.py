import openai
from flask import Flask, request, jsonify
import tensorflow as tf
import numpy as np
import cv2

openai.api_key = "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"
app = Flask(__name__)
# Configura CORS para permitir todas las rutas y métodos desde localhost:3000

# Cargar modelo de TensorFlow
try:
    model_img = tf.keras.models.load_model('model.h5')
    mode_text = tf.keras.models.load_model('model.h5')
except Exception as e:
    print(f"Error al cargar el modelo: {e}")
    model = None


# Configurar clave de API de OpenAI
def preprocess_image(image_bytes):
    """
    Preprocesa la imagen usando OpenCV para que coincida con el formato esperado por el modelo.
    """
    # Convertir bytes a numpy array
    nparr = np.frombuffer(image_bytes, np.uint8)

    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (48, 48))  # Ajusta estas dimensiones según tu modelo
    normalized = resized / 255.0

    # Añadir dimensiones para batch y canales
    processed = np.expand_dims(normalized, axis=0)
    processed = np.expand_dims(processed, axis=-1)

    return processed


@app.route('/')
def hello_world():
    return 'Servidor de detección de emociones activo'


@app.route('/predict_dummy', methods=['POST'])
def predict_dummy():
    try:
        # Simular predicciones con datos ficticios
        # No necesitamos procesar la imagen ni el texto realmente
        dummy_emotions = ['Enojo', 'Disgusto', 'Miedo', 'Felicidad', 'Tristeza', 'Sorpresa', 'Neutral']

        # Generar probabilidades aleatorias que sumen 1
        def generate_probabilities():
            probs = np.random.random(7)
            return probs / probs.sum()

        # Generar predicciones aleatorias
        probs_img = generate_probabilities()
        probs_txt = generate_probabilities()

        probabilities_img = {
            emotion: float(prob)
            for emotion, prob in zip(dummy_emotions, probs_img)
        }

        probabilities_txt = {
            emotion: float(prob)
            for emotion, prob in zip(dummy_emotions, probs_txt)
        }

        # Seleccionar la emoción con mayor probabilidad
        predicted_img = dummy_emotions[np.argmax(probs_img)]
        predicted_txt = dummy_emotions[np.argmax(probs_txt)]

        # Obtener recomendación de ChatGPT
        chatgpt_response = interact_with_chatgpt(predicted_img, predicted_txt, probabilities_img, probabilities_txt)

        # Construir la respuesta
        result = {
            'emotion_img': predicted_img,
            'emotion_txt': predicted_txt,
            'probabilities_img': probabilities_img,
            'probabilities_txt': probabilities_txt,
            'recommendation': chatgpt_response
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/predict', methods=['POST'])
def predict_request():
    if model_img is None:
        return jsonify({'error': 'Modelos no cargado correctamente'}), 500
    if 'image' not in request.files:
        return jsonify({'error': 'No se encontró imagen en la petición'}), 400

    if 'post' not in request.files:
        return jsonify({'error': 'No se encontró imagen en la petición'}), 400

    try:
        # Obtener la imagen del request
        image_file = request.files['image'].read()
        post = request.files['post'].read()

        # Preprocesar la imagen
        processed_image = preprocess_image(image_file)

        # Realizar la predicción
        prediction_img = model_img.predict(processed_image)
        prediction_txt = mode_text.predict(post)

        # Mapear las emociones (ajusta según las clases de tu modelo)
        emotions = ['Enojo', 'Disgusto', 'Miedo', 'Felicidad', 'Tristeza', 'Sorpresa', 'Neutral']
        predicted_img = emotions[np.argmax(prediction_img[0])]
        predicted_txt = emotions[np.argmax(prediction_txt[0])]


        probabilities_img = {
            emotion: float(prob)
            for emotion, prob in zip(emotions, prediction_img[0])
        }
        probabilities_txt = {
            emotion: float(prob)
            for emotion, prob in zip(emotions, prediction_txt[0])
        }

        # Crear un mensaje para enviar a ChatGPT
        chatgpt_response = interact_with_chatgpt(predicted_img, predicted_txt, probabilities_img, probabilities_txt)

        # Responder con la emoción, probabilidades y recomendación de ChatGPT
        result = {
            'emotion_img': predicted_img,
            'emotion_txt': predicted_txt,
            'recommendation': chatgpt_response
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def interact_with_chatgpt(emotion_img, emotion_txt, probabilities_img, probabilities_txt):
    """
    Interactúa con ChatGPT para generar una recomendación basada en la emoción detectada.
    """
    try:
        # Crear el prompt para ChatGPT
        prompt = (
            f"La emoción detectada de la imagen es'{emotion_img}'. "
            f"Las probabilidades de cada emoción de la img son: {probabilities_img}. "
            f"La emoción detectada del texto es'{emotion_img}'. "
            f"Las probabilidades de cada emoción del txt son: {probabilities_img}. "
            "¿Puedes sugerir una recomendación para alguien que siente estas emociónes?"
        )

        # Llamar a la API de OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "Eres un asistente que proporciona recomendaciones basadas en emociones."},
                {"role": "user", "content": prompt}
            ]
        )

        # Obtener la respuesta de ChatGPT
        recommendation = response['choices'][0]['message']['content']
        return recommendation

    except Exception as e:
        return f"Error al interactuar con ChatGPT: {str(e)}"


if __name__ == "__main__":
    app.run(debug=True)
