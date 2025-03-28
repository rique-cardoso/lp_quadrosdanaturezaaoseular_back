from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from dotenv import load_dotenv
import os

app = Flask(__name__)
CORS(app, resources={r"/send-message": {"origins": "https://nexxomi.github.io"}})

load_dotenv()

# Configuração da Evolution API
EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL")
API_KEY = os.getenv("API_KEY")

@app.route('/send-message', methods=['POST'])
def send_message():
    try:
        # Recebe os dados do front-end
        data = request.get_json()
        
        # Valida os dados recebidos
        if not data or 'phone' not in data:
            return jsonify({"error": "Número e texto são obrigatórios"}), 400
        
        # Prepara o payload para a Evolution API
        payload = {
            "number": data['phone'],
            "text": f"Olá, {data['name']}!\nSeu cupom de 15% de desconto está garantido! Para utilizá-lo, basta enviar um print do quadro que você deseja adquirir, e nós providenciaremos o envio do seu quadro com o desconto exclusivo. Aproveite e transforme seu ambiente com um toque especial!"
        }
        
        headers = {
            "apikey": API_KEY,
            "Content-Type": "application/json"
        }
        
        # Envia para a Evolution API
        response = requests.post(EVOLUTION_API_URL, json=payload, headers=headers)
        
        # Retorna a resposta para o front-end
        return jsonify({
            "status": "success",
            "evolution_api_response": response.json()
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5000)))