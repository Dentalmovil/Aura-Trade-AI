import ccxt
import pandas as pd
import os
from ia_engine import preparar_ia
from telegram_util import enviar_mensaje

# Configuración
symbol = 'BTC/USDT'
exchange = ccxt.binance()

def ejecutar_bot():
    print(f"🛰️ Aura Trade AI analizando {symbol}...")
    try:
        # 1. Obtener datos
        bars = exchange.fetch_ohlcv(symbol, timeframe='1h', limit=100)
        df = pd.DataFrame(bars, columns=['ts', 'open', 'high', 'low', 'close', 'volume'])
        
        # 2. IA y Predicción
        modelo, features = preparar_ia(df)
        ultimo_dato = df[features].tail(1)
        prediccion = modelo.predict(ultimo_dato)[0]
        
        precio_actual = df['close'].iloc[-1]
        
        # 3. Lógica de envío
        if prediccion == 1:
            msg = f"🚀 *SEÑAL DE COMPRA*\n🪙 Par: {symbol}\n💰 Precio: ${precio_actual:,.2f}"
            enviar_mensaje(msg)
            print("✅ Señal enviada.")
        else:
            print("⌛ Mercado estable, sin señal.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    ejecutar_bot()
    # Al terminar ejecutar_bot(), el programa finaliza y GitHub se pone VERDE.

