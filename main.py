import ccxt
import pandas as pd
import threading
import time
from flask import Flask, render_template
from ia_engine import preparar_ia
from telegram_util import enviar_mensaje

# --- CONFIGURACIÓN WEB ---
app = Flask(__name__)

# Datos globales que se mostrarán en el HTML
datos_web = {
    "profit_hoy": 0.0,
    "ops_activas": 0,
    "precio_actual": "Cargando...",
    "rsi_actual": "Cargando..."
}

# --- LÓGICA DEL BOT (Basada en tus capturas) ---
exchange = ccxt.binance()
symbol = 'BTC/USDT'

def ejecutar_bot():
    global datos_web
    print("Aura Trade AI analizando...")
    
    while True:
        try:
            # Obtención de datos
            bars = exchange.fetch_ohlcv(symbol, timeframe='1h', limit=100)
            df = pd.DataFrame(bars, columns=['ts', 'open', 'high', 'low', 'close', 'volume'])
            
            # Preparación de IA
            modelo, features = preparar_ia(df)
            ultimo_dato = df[features].tail(1)
            
            # Predicción y cálculos
            prediccion = modelo.predict(ultimo_dato)[0]
            precio = df['close'].iloc[-1]
            rsi = df['RSI'].iloc[-1]
            
            # Actualizamos datos para el HTML
            datos_web["precio_actual"] = precio
            datos_web["rsi_actual"] = rsi

            # Lógica de señales
            if prediccion == 1 and rsi < 70:
                msg = (f"🚀 *Aura Trade AI: SEÑAL*\n\n"
                       f"✅ Sugerencia: COMPRA\n💰 Precio: ${precio:,.2f}\n"
                       f"📊 RSI: {rsi:.2f}")
                enviar_mensaje(msg)
                datos_web["ops_activas"] += 1
            else:
                print(f"Sin señal clara. RSI: {rsi:.2f}")

        except Exception as e:
            print(f"Error: {e}")
        
        # Pausa para no saturar la API
        time.sleep(60)

# --- RUTAS DE FLASK ---
@app.route('/')
def index():
    # Enviamos las variables al archivo index.html
    return render_template('index.html', 
                           profit_hoy=datos_web["profit_hoy"], 
                           ops_activas=datos_web["ops_activas"])

if __name__ == "__main__":
    # 1. Iniciar el bot en segundo plano (Thread)
    threading.Thread(target=ejecutar_bot, daemon=True).start()
    
    # 2. Iniciar el servidor web
    # host='0.0.0.0' permite que lo veas desde tu celular en la misma red
    app.run(debug=True, host='0.0.0.0', port=5000)

