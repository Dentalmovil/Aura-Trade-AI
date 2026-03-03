import requests
import pandas as pd
import os
from datetime import datetime
from ia_engine import preparar_ia
from telegram_util import enviar_mensaje

symbols = ['BTCUSDT', 'BNBUSDT', 'XRPUSDT', 'LTCUSDT']

def obtener_datos_directos(symbol):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1h&limit=100"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Creamos el DataFrame con los nombres de columnas que espera tu ia_engine
            df = pd.DataFrame(data, columns=['ts', 'open', 'high', 'low', 'close', 'volume', 'close_ts', 'qav', 'num_trades', 'taker_base', 'taker_quote', 'ignore'])
            
            # CONVERSIÓN CRÍTICA: Convertimos texto a números para la IA
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
            
            return df
    except Exception as e:
        print(f"Error de red en {symbol}: {e}")
    return None

def ejecutar_bot():
    print(f"🚀 Aura Trade AI Iniciando - {datetime.now()}")
    # Ya no enviamos el mensaje de inicio cada vez para no saturar si hay errores
    
    for symbol in symbols:
        try:
            df = obtener_datos_directos(symbol)
            if df is not None:
                precio_actual = df['close'].iloc[-1]
                
                # Llamada a tu archivo ia_engine.py
                modelo, features, confianza = preparar_ia(df)
                
                # Predicción con el último dato disponible
                input_ia = df[features].tail(1)
                prediccion = modelo.predict(input_ia)[0]
                
                emoji = "🟢" if confianza > 75 else "🟡" if confianza > 50 else "⚪"
                accion = "COMPRA" if prediccion == 1 and confianza > 70 else "ESPERAR"
                
                msj = (f"📊 *MONITOR:* {symbol}\n"
                       f"💵 Precio: ${precio_actual:,.2f}\n"
                       f"🧠 Confianza IA: {emoji} {confianza:.1f}%\n"
                       f"📝 Acción: *{accion}*")
                enviar_mensaje(msj)
            else:
                enviar_mensaje(f"⚠️ No pude obtener datos de {symbol}")
        except Exception as e:
            print(f"❌ Error en {symbol}: {e}")
            # Si hay un error dentro de la IA, te avisará aquí
            enviar_mensaje(f"🧠 Error en IA ({symbol}): Ver logs en GitHub")

if __name__ == "__main__":
    ejecutar_bot()


