import ccxt
import pandas as pd
import threading
import time
from flask import Flask, render_template
from ia_engine import preparar_ia
from telegram_util import enviar_mensaje

# Configuración de la App Web
app = Flask(__name__)

# Variables globales para compartir datos entre el Bot y la Web
datos_vivos = {
    "precio": "Cargando...",
    "rsi": "Cargando...",
    "senal": "Analizando mercado...",
    "color_rsi": "white"
}

exchange = ccxt.binance()
symbol = 'BTC/USDT'

def ejecutar_bot():
    """Lógica principal del bot de trading"""
    global datos_vivos
    print("Aura Trade AI: Motor de IA y Bot Iniciados...")
    
    while True:
        try:
            # 1. Obtención de datos
            bars = exchange.fetch_ohlcv(symbol, timeframe='1h', limit=100)
            df = pd.DataFrame(bars, columns=['ts', 'open', 'high', 'low', 'close', 'volume'])
            
            # 2. Preparación de IA
            modelo, features = preparar_ia(df)
            ultimo_dato = df[features].tail(1)
            
            # 3. Predicción y RSI
            prediccion = modelo.predict(ultimo_dato)[0]
            precio_actual = df['close'].iloc[-1]
            rsi_actual = df['RSI'].iloc[-1]
            
            # Actualizar datos para la web
            datos_vivos["precio"] = f"{precio_actual:,.2f}"
            datos_vivos["rsi"] = f"{rsi_actual:.2f}"
            datos_vivos["color_rsi"] = "#3fb950" if rsi_actual < 70 else "#e94560"

            # 4. Lógica de envío de señales
            if prediccion == 1 and rsi_actual < 70:
                msg = (f"🚀 *Aura Trade AI: SEÑAL*\n\n"
                       f"✅ Sugerencia: COMPRA\n💰 Precio: ${precio_actual:,.2f}\n"
                       f"📊 RSI: {rsi_actual:.2f}")
                enviar_mensaje(msg)
                datos_vivos["senal"] = "COMPRA ENVIADA 🚀"
            else:
                datos_vivos["senal"] = "Sin señal clara (Neutral)"
                print(f"Sin señal clara. RSI: {rsi_actual:.2f}")

        except Exception as e:
            print(f"Error en el bot: {e}")
        
        # Espera 1 minuto antes de la siguiente revisión
        time.sleep(60)

@app.route('/')
def home():
    """Ruta para mostrar el Dashboard HTML"""
    return render_template('index.html', 
                           precio=datos_vivos["precio"], 
                           rsi=datos_vivos["rsi"], 
                           senal=datos_vivos["senal"],
                           color=datos_vivos["color_rsi"])

if __name__ == '__main__':
    # Hilo 1: Ejecuta el bot de trading en segundo plano
    threading.Thread(target=ejecutar_bot, daemon=True).start()
    
    # Hilo 2: Ejecuta el servidor web (Flask)
    # Si usas Replit o móvil, usa host='0.0.0.0'
    app.run(debug=True, host='0.0.0.0', port=5000)

