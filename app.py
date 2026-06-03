from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuración de la API
API_KEY = os.getenv('API_GEMINI')  # Mantenemos tu variable actual

@app.route('/models')
def list_models():
    try:
        models_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
        response = requests.get(models_url)
        
        if response.status_code == 200:
            result = response.json()
            models = []
            if 'models' in result:
                for model in result['models']:
                    if 'generateContent' in model.get('supportedGenerationMethods', []):
                        models.append(model['name'])
            
            return jsonify({
                'available_models': models,
                'full_response': result
            })
        else:
            return jsonify({
                'error': f'Error getting models: {response.text}',
                'status_code': response.status_code
            })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/ascend')
def ascend():
    return send_from_directory('.', 'ascend.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        mensaje = data.get('message', '')
        
        if not mensaje:
            return jsonify({'error': 'No se proporcionó ningún mensaje'}), 400
        
        # Crear el mensaje con contexto de Laia
        mensaje_completo = f"{SYSTEM_PROMPT}\n\nUsuario: {mensaje}\nLaia:"
        
        # Payload para la API REST de Google
        payload = {
            "contents": [{
                "parts": [{
                    "text": mensaje_completo
                }]
            }]
        }
        
        # Usar el modelo que funciona: gemini-2.5-flash
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"
        
        response = requests.post(api_url, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                response_text = result['candidates'][0]['content']['parts'][0]['text']
                return jsonify({
                    'response': response_text,
                    'status': 'success'
                })
            else:
                return jsonify({
                    'error': 'No se recibió respuesta del modelo',
                    'status': 'error'
                }), 500
        else:
            return jsonify({
                'error': f'Error de API: {response.text}',
                'status': 'error'
            }), 500
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

# System prompt para Laia
SYSTEM_PROMPT = """Eres Laia, una experta vendedora de Ascend. 

Tu personalidad:
- Eres amable, profesional y muy conocedora de la plataforma Ascend
- Siempre te enfocas EXCLUSIVAMENTE en hablar sobre Ascend y sus características
- No hablas de otras plataformas, productos o temas fuera de Ascend
- Eres directa y honesta: si no sabes algo específico de Ascend, lo admites
- Tu objetivo es ayudar a los clientes a entender el valor de Ascend

Reglas estrictas:
- SOLO hablas sobre Ascend, su plataforma, características, beneficios y precios
- Si te preguntan sobre otros temas, redirige amablemente la conversación a Ascend
- No inventes características o funcionalidades que no existen
- Sé concisa pero informativa
- Mantén un tono profesional pero cercano

Recuerda: Eres Laia de Ascend, siempre enfocada en tu plataforma."""



if __name__ == '__main__':
    app.run(debug=True, port=5000)
