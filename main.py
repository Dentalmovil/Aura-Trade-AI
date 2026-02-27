import ccxt
import pandas as pd
from ia_engine import preparar_ia
from telegram_util import enviar_mensaje

exchange = ccxt.binance()
symbol = 'BTC/USDT'

def ejecutar_bot():
    print("Aura Trade AI analizando...")
    try:
        bars = exchange.fetch_ohlcv(symbol, timeframe='1h', limit=100)
        df = pd.DataFrame(bars, columns=['ts', 'open', 'high', 'low', 'close', 'volume'])
        modelo, features = preparar_ia(df)
        ultimo_dato = df[features].tail(1)
        prediccion = modelo.predict(ultimo_dato)[0]
        precio_actual = df['close'].iloc[-1]
        rsi_actual = df['RSI'].iloc[-1]
        
        if prediccion == 1 and rsi_actual < 70:
            msg = f"🚀 *Aura Trade AI: SEÑAL*\n\n✅ Sugerencia: COMPRA\n💰 Precio: ${precio_actual:,.2f}\n📊 RSI: {rsi_actual:.2f}"
            enviar_mensaje(msg)
        else:
            print(f"Sin señal clara. RSI: {rsi_actual:.2f}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    ejecutar_bot()
