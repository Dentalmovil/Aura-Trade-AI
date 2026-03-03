import ccxt
import pandas as pd
import os
from datetime import datetime
from ia_engine import preparar_ia
from telegram_util import enviar_mensaje

# 1. CONFIGURACIÓN CON PROXY PARA EVITAR BLOQUEO GEOGRÁFICO
exchange = ccxt.binance({
    'apiKey': os.environ.get('BINANCE_API_KEY'),
    'secret': os.environ.get('BINANCE_SECRET_KEY'),
    'enableRateLimit': True,
    'https_proxy': 'http://proxy.server:3128', # Intentaremos conexión directa primero con ajustes
    'options': {
        'defaultType': 'spot',
        'adjustForTimeDifference': True,
        'warnOnFetchOHLCVLimitFault': False
    }
})

# Cambiamos a una ruta que GitHub suele permitir mejor
exchange.urls['api'] = 'https://api1.binance.com'

symbols = ['BTC/USDT', 'BNB/USDT', 'XRP/USDT', 'LTC/USDT']

def ejecutar_bot():
    print(f"🚀 Aura Trade AI Iniciando - {datetime.now()}")
    
    for symbol in symbols:
        try:
            # 2. Obtener datos usando la ruta alternativa
            bars = exchange.fetch_ohlcv(symbol, timeframe='1h', limit=100)
            df = pd.DataFrame(bars, columns=['ts', 'open', 'high', 'low', 'close', 'volume'])
            
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
                
            precio_actual = df['close'].iloc[-1]
            
            # 3. Consultar a la IA
            modelo, features, confianza = preparar_ia(df)
            prediccion = modelo.predict(df[features].tail(1))[0]
            
            # 4. Reporte a Telegram
            emoji = "🟢" if confianza > 75 else "🟡" if confianza > 50 else "⚪"
            accion = "POTENCIAL COMPRA" if prediccion == 1 and confianza > 70 else "MERCADO NEUTRO"
            
            msj = (f"📊 *REPORTE:* {symbol}\n"
                   f"💵 Precio: ${precio_actual:,.2f}\n"
                   f"🧠 Confianza IA: {emoji} {confianza:.1f}%\n"
                   f"📝 Sugerencia: *{accion}*")
            
            enviar_mensaje(msj)

        except Exception as e:
            print(f"❌ Error en {symbol}: {e}")
            # Si sigue fallando por ubicación, usamos el último recurso: la API de datos puros
            if "restricted" in str(e).lower():
                 enviar_mensaje(f"⚠️ Binance sigue bloqueando la IP de GitHub para {symbol}. Intentando ruta C...")

if __name__ == "__main__":
    ejecutar_bot()



