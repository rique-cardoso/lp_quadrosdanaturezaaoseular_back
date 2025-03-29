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

def send_whatsapp_message(phone, message, image_url=None, buttons=None):
    """
    Envia uma mensagem via Evolution API.
    Se houver imagem, ela será enviada junto.
    """
    payload = {
        "number": phone,
        "text": message
    }
    
    if image_url:
        payload["image"] = image_url
    
    if buttons:
        payload["buttons"] = buttons
    
    headers = {
        "apikey": API_KEY,
        "Content-Type": "application/json"
    }
    
    response = requests.post(EVOLUTION_API_URL, json=payload, headers=headers)
    return response.json()

@app.route('/send-message', methods=['POST'])
def send_message():
    try:
        data = request.get_json()
        
        if not data or 'phone' not in data or 'name' not in data:
            return jsonify({"error": "Número e nome são obrigatórios"}), 400

        phone = data['phone']
        name = data['name']
        product_image = data.get('productImage')  # Pode ser None

        if product_image:
            message = (f"Olá, {name}, tudo bem?\n\n"
                       "Seu cupom de 15% de desconto está garantido no produto selecionado! "
                       "Escolha abaixo o Tipo de Impressão e Acabamento que você deseja para o quadro:")
            buttons = [
                "Tela Canvas e Canaleta Flutuante",
                "Tela Canvas e Caixa sem Vidro",
                "Premium em Acrílico e Caixa sem Vidro",
                "Premium em Acrílico e Caixa com Vidro"
            ]
            response = send_whatsapp_message(phone, message, image_url=product_image, buttons=buttons)
        else:
            message = (f"Olá, {name}, tudo bem?\n\n"
                       "Seu cupom de 15% de desconto está garantido! Para utilizá-lo, basta enviar um print "
                       "ou uma foto do quadro que você deseja adquirir e escolher uma das opções de impressão abaixo:")
            response = send_whatsapp_message(phone, message)

        return jsonify({"status": "success", "evolution_api_response": response}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5000)))
