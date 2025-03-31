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
INSTANCE_NAME = os.getenv("INSTANCE_NAME")
SHEETS_URL = os.getenv("SHEETS_URL")

def send_whatsapp_message(phone, message, image_url=None):
    """
    Envia uma mensagem via Evolution API.
    Se houver imagem, ela será enviada junto.
    """
    """ payload = {
        "number": phone,
        "text": message
    } """
    payload = {}
    endpoint = ""
    
    if image_url:
        """ payload["media"] = image_url
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
        ) """

        payload["number"] = phone
        payload["mediatype"] = "image"
        payload["mimetype"] = "image/png"
        payload["caption"] = message
        payload["media"] = image_url
        payload["fileName"] = "quadro_selecionado.png"

        endpoint = f"{EVOLUTION_API_URL}/message/sendMedia/{INSTANCE_NAME}"
    else:
        payload["number"] = phone
        payload["text"] = message
        endpoint = f"{EVOLUTION_API_URL}/message/sendText/{INSTANCE_NAME}"
    
    headers = {
        "apikey": API_KEY,
        "Content-Type": "application/json"
    }
    
    response = requests.post(endpoint, json=payload, headers=headers)
    return response.json()

@app.route('/register-lead', methods=['POST'])
def register_lead():
    try:
        data = request.get_json()
        
        if not data or 'phone' not in data or 'name' not in data:
            return jsonify({"error": "Número e nome são obrigatórios"}), 400
        
        phone = data['phone']
        name = data['name']
        product_image = data.get('productImage', '') # Usa valor padrão vazio se não houver productImage

        payload = {
            "phone": phone,
            "name": name,
            "productImage": product_image
        }

        response = requests.post(SHEETS_URL, json=payload) # Envia os dados para o Google Apps Script

        # Verificar se a requisição foi bem-sucedida
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get('status') == 'success':
                return jsonify({"status": "success", "message": "Lead registrado no Google Sheets"}), 200
            else:
                return jsonify({"error": "Erro ao registrar no Google Sheets"}), 500
        else:
            return jsonify({"error": f"Erro na requisição ao Google Sheets: {response.status_code}"}), 500
    
    except Exception as e:

        return jsonify({"error": f"Erro interno: {str(e)}"}), 500







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
                       "Seu cupom de 15% de desconto está garantido no produto selecionado!\n\n"
                       "Escolha abaixo o Tipo de Impressão e Acabamento que você deseja para o quadro:\n\n"
                       "1. Tela Canvas e Canaleta Flutuante\n"
                        "2. Tela Canvas e Caixa sem Vidro\n"
                        "3. Premium em Acrílico e Caixa sem Vidro\n"
                        "4. Premium em Acrílico e Caixa com Vidro\n\n"
                        "Responda com o número correspondente à sua escolha.")
            response = send_whatsapp_message(phone, message, image_url=product_image)
        else:
            message = (f"Olá, {name}, tudo bem?\n\n"
                       "Seu cupom de 15% de desconto está garantido! Para utilizá-lo, basta enviar um print "
                       "ou uma foto do quadro que você deseja adquirir e escolher uma das opções de impressão abaixo:\n\n"
                       "1. Tela Canvas e Canaleta Flutuante\n"
                        "2. Tela Canvas e Caixa sem Vidro\n"
                        "3. Premium em Acrílico e Caixa sem Vidro\n"
                        "4. Premium em Acrílico e Caixa com Vidro\n\n"
                        "Responda com o número correspondente à sua escolha.")
            response = send_whatsapp_message(phone, message)

        return jsonify({"status": "success", "evolution_api_response": response}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5000)))
