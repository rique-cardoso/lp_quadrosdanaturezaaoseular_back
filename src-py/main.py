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

def send_whatsapp_message(phone, message, image_url=None):
    """
    Envia uma mensagem via Evolution API.
    Se houver imagem, ela será enviada junto.
    """
    payload = {
        "number": phone,
        "text": message
    }

    endpoint = ""
    
    if image_url:
        payload["media"] = image_url
        payload["mediatype"] = "image"
        payload["mimetype"] = "image/png"
        payload["fileName"] = "quadro_selecionado.png"
        payload["caption"] = (
            "Olá, Ana Luíza, tudo bem? Seu cupom de 15% de desconto está garantido no produto selecionado!\n\n"
            "Escolha abaixo o Tipo de Impressão e Acabamento que você deseja para o quadro:\n\n"
            "1. Tela Canvas e Canaleta Flutuante\n"
            "2. Tela Canvas e Caixa sem Vidro\n"
            "3. Premium em Acrílico e Caixa sem Vidro\n"
            "4. Premium em Acrílico e Caixa com Vidro\n\n"
            "Responda com o número correspondente à sua escolha."
        )
        endpoint = f"{EVOLUTION_API_URL}/message/sendMedia/quadrosdanaturezaaoseular"
    else:
        endpoint = f"{EVOLUTION_API_URL}/sendText/quadrosdanaturezaaoseular"
    
    headers = {
        "apikey": API_KEY,
        "Content-Type": "application/json"
    }
    
    response = requests.post(endpoint, json=payload, headers=headers)
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
            response = send_whatsapp_message(phone, message, image_url=product_image)
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
