import requests
import os

def enviar_mensaje(texto):
    """
    Envía notificaciones a tu celular usando los Secrets de GitHub.
    """
    # 1. Obtenemos las llaves de forma segura
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    # 2. Construimos la dirección de envío
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    # 3. Preparamos el paquete de datos
    payload = {
        "chat_id": chat_id,
        "text": texto,
        "parse_mode": "Markdown" # Esto permite usar negritas y emojis
    }
    
    try:
        # 4. Realizamos el envío real
        response = requests.post(url, data=payload)
        response.raise_for_status() # Si hay un error, lo detecta aquí
        return True
    except Exception as e:
        print(f"❌ Error enviando a Telegram: {e}")
        return False


