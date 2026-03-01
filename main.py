import ccxt
import pandas as pd
import threading
import time
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from ia_engine import preparar_ia
from telegram_util import enviar_mensaje

app = Flask(__name__)

# --- CONFIGURACIÓN Y ESTADO ---
config = {
    "symbol": "BTC/USDT",
    "rsi_limite": 70,
    "activo": True  # Controla si el bot está corriendo o en PAUSA
}

datos_vivos = {
    "precio": "0.00",
    "rsi": "0.00",
    "senal": "Sistema Iniciado",
    "alerta": False,
    "historial": []
}

exchange = ccxt.binance()

def ejecutar_bot():
    global datos_vivos
    while True:
        if config["activo"]:
            try:
                # Análisis de mercado
                bars = exchange.fetch_ohlcv(config["symbol"], timeframe='1h', limit=100)
                df = pd.DataFrame(bars, columns=['ts', 'open', 'high', 'low', 'close', 'volume'])
                
                modelo, features = preparar_ia(df)
                ultimo_dato = df[features].tail(1)
                prediccion = modelo.predict(ultimo_dato)[0]
                
                precio = df['close'].iloc[-1]
                rsi = df['RSI'].iloc[-1]
                
                datos_vivos["precio"] = f"{precio:,.2f}"
                datos_vivos["rsi"] = f"{rsi:.2f}"

                # Lógica de señales
                if prediccion == 1 and rsi < config["rsi_limite"]:
                    ahora = datetime.now().strftime("%H:%M:%S")
                    enviar_mensaje(f"🚀 COMPRA {config['symbol']} | ${precio}")
                    
                    datos_vivos["senal"] = "¡SEÑAL DE COMPRA!"
                    datos_vivos["alerta"] = True
                    
                    nueva_alerta = {"hora": ahora, "par": config["symbol"], "precio": precio}
                    datos_vivos["historial"].insert(0, nueva_alerta)
                    datos_vivos["historial"] = datos_vivos["historial"][:5]
                else:
                    datos_vivos["senal"] = f"Escaneando {config['symbol']}..."
                    datos_vivos["alerta"] = False

            except Exception as e:
                print(f"Error: {e}")
        else:
            datos_vivos["senal"] = "PAUSADO - BOT DETENIDO"
            datos_vivos["alerta"] = False
        
        time.sleep(30)

@app.route('/')
def home():
    return render_template('index.html', **datos_vivos, config=config)

@app.route('/update', methods=['POST'])
def update_config():
    config["symbol"] = request.form.get("symbol").upper()
    config["rsi_limite"] = float(request.form.get("rsi_limite"))
    return redirect(url_for('home'))

@app.route('/toggle')
def toggle_bot():
    # Cambia entre Activo y Pausado
    config["activo"] = not config["activo"]
    return redirect(url_for('home'))

if __name__ == '__main__':
    threading.Thread(target=ejecutar_bot, daemon=True).start()
    app.run(debug=True, host='0.0.0.0', port=5000)


