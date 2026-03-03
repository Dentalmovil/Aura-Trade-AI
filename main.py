import requests
import pandas as pd
import os
from datetime import datetime
from ia_engine import preparar_ia
from telegram_util import enviar_mensaje

symbols = ['BTCUSDT', 'BNBUSDT', 'XRPUSDT', 'LTCUSDT']

def obtener_datos_directos(symbol):
    # Usamos la URL directa de la API de Binance (más difícil de bloquear)
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1h&limit=100"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data, columns=['ts', 'open', 'high', 'low', 'close', 'volume', 'close_ts', 'qav', 'num_trades', 'taker_base', 'taker_quote', 'ignore'])
        df['close'] = df['close'].astype(float)
        # Necesitamos estas para los indicadores de tu ia_engine
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        return df
    return None

def ejecutar_bot():
    print(f"🚀 Aura Trade AI Iniciando - {datetime.now()}")
    enviar_mensaje("📡 *Aura Trade AI:* Conexión directa establecida. Analizando...")
    
    for symbol in symbols:
        try:
            df = obtener_datos_directos(symbol)
            if df is not None:
                precio_actual = df['close'].iloc[-1]
                
                # Llamamos a tu IA (ia_engine.py)
                modelo, features, confianza = preparar_ia(df)
                prediccion = modelo.predict(df[features].tail(1))[0]
                
                emoji = "🟢" if confianza > 75 else "🟡" if confianza > 50 else "⚪"
                accion = "COMPRA" if prediccion == 1 and confianza > 70 else "ESPERAR"
                
                msj = (f"📊 *MONITOR:* {symbol}\n"
                       f"💵 Precio: ${precio_actual:,.2f}\n"
                       f"🧠 Confianza IA: {emoji} {confianza:.1f}%\n"
                       f"📝 Acción: *{accion}*")
                enviar_mensaje(msj)
            else:
                print(f"No se pudo obtener datos de {symbol}")
        except Exception as e:
            print(f"❌ Error en {symbol}: {e}")

if __name__ == "__main__":
    ejecutar_bot()






