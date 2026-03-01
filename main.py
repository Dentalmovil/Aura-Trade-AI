import ccxt
import pandas as pd
import threading
import time
import plotly.graph_objects as go
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from ia_engine import preparar_ia
from telegram_util import enviar_mensaje

app = Flask(__name__)

config = {"symbol": "BTC/USDT", "rsi_limite": 70, "activo": True}
datos_vivos = {"precio": "0.00", "rsi": "0.00", "senal": "Iniciando...", "alerta": False, "historial": [], "graph_html": ""}

exchange = ccxt.binance()

def generar_grafico(df):
    """Crea el gráfico con Bandas de Bollinger para la web"""
    fig = go.Figure()
    # Precio y Velas
    fig.add_trace(go.Scatter(x=df.index, y=df['close'], name='Precio', line=dict(color='#58a6ff')))
    # Bandas de Bollinger
    fig.add_trace(go.Scatter(x=df.index, y=df['BBU_20_2.0'], name='Banda Sup', line=dict(dash='dash', color='rgba(255,255,255,0.2)')))
    fig.add_trace(go.Scatter(x=df.index, y=df['BBL_20_2.0'], name='Banda Inf', line=dict(dash='dash', color='rgba(255,255,255,0.2)'), fill='tonexty'))
    
    fig.update_layout(template="plotly_dark", height=300, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    return fig.to_html(full_html=False, include_plotlyjs='cdn')

def ejecutar_bot():
    global datos_vivos
    while True:
        if config["activo"]:
            try:
                bars = exchange.fetch_ohlcv(config["symbol"], timeframe='1h', limit=100)
                df = pd.DataFrame(bars, columns=['ts', 'open', 'high', 'low', 'close', 'volume'])
                df['ts'] = pd.to_datetime(df['ts'], unit='ms')
                df.set_index('ts', inplace=True)

                modelo, features = preparar_ia(df) # Usa el nuevo cerebro con BBands
                
                ultimo_dato = df[features].tail(1)
                prediccion = modelo.predict(ultimo_dato)[0]
                
                precio = df['close'].iloc[-1]
                rsi = df['RSI'].iloc[-1]
                
                datos_vivos["precio"] = f"{precio:,.2f}"
                datos_vivos["rsi"] = f"{rsi:.2f}"
                datos_vivos["graph_html"] = generar_grafico(df)

                if prediccion == 1 and rsi < config["rsi_limite"]:
                    ahora = datetime.now().strftime("%H:%M:%S")
                    enviar_mensaje(f"🚀 COMPRA {config['symbol']} | ${precio}")
                    datos_vivos["senal"] = "¡SEÑAL DE COMPRA!"
                    datos_vivos["alerta"] = True
                    datos_vivos["historial"].insert(0, {"hora": ahora, "par": config["symbol"], "precio": precio})
                    datos_vivos["historial"] = datos_vivos["historial"][:5]
                else:
                    datos_vivos["senal"] = f"Escaneando {config['symbol']}..."
                    datos_vivos["alerta"] = False
            except Exception as e: print(f"Error: {e}")
        time.sleep(30)

@app.route('/')
def home(): return render_template('index.html', **datos_vivos, config=config)

@app.route('/update', methods=['POST'])
def update_config():
    config["symbol"] = request.form.get("symbol").upper()
    config["rsi_limite"] = float(request.form.get("rsi_limite"))
    return redirect(url_for('home'))

@app.route('/toggle')
def toggle_bot():
    config["activo"] = not config["activo"]
    return redirect(url_for('home'))

if __name__ == '__main__':
    threading.Thread(target=ejecutar_bot, daemon=True).start()
    app.run(debug=True, host='0.0.0.0', port=5000)

