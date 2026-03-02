import ccxt
import pandas as pd
import os
from datetime import datetime
from ia_engine import preparar_ia
from telegram_util import enviar_mensaje

# 1. CONEXIÓN SEGURA A BINANCE
exchange = ccxt.binance({
    'apiKey': os.environ.get('BINANCE_API_KEY'),
    'secret': os.environ.get('BINANCE_SECRET_KEY'),
    'enableRateLimit': True,
    'options': {'defaultType': 'spot'}
})

symbols = ['BTC/USDT', 'BNB/USDT', 'XRP/USDT', 'LTC/USDT']

def ejecutar_bot():
    print(f"🚀 Aura Trade AI Iniciando - {datetime.now()}")
    # Notificación de inicio para confirmar que el bot despertó
    enviar_mensaje("📡 *Aura Trade AI:* Iniciando análisis de mercado...")
    
    for symbol in symbols:
        try:
            # 2. Obtener datos
            bars = exchange.fetch_ohlcv(symbol, timeframe='1h', limit=100)
            df = pd.DataFrame(bars, columns=['ts', 'open', 'high', 'low', 'close', 'volume'])
            precio_actual = df['close'].iloc[-1]
            
            # 3. Consultar a la IA
            modelo, features, confianza = preparar_ia(df)
            prediccion = modelo.predict(df[features].tail(1))[0]
            
            # 4. Decisión y Envío a Telegram
            emoji = "🟢" if confianza > 80 else "🟡" if confianza > 60 else "⚪"
            
            if prediccion == 1 and confianza > 75:
                tp = precio_actual * 1.02
                sl = precio_actual * 0.99
                msj = (f"🚀 *SEÑAL DE COMPRA: {symbol}*\n"
                       f"💰 Precio: ${precio_actual}\n"
                       f"📊 Confianza: {emoji} {confianza:.1f}%\n"
                       f"🎯 TP: {tp:.2f} | 🛑 SL: {sl:.2f}")
                enviar_mensaje(msj)
            else:
                msj_rutina = (f"📊 MONITOR: {symbol}\n"
                             f"💵 Precio: ${precio_actual}\n"
                             f"🧠 Confianza IA: {emoji} {confianza:.1f}%")
                enviar_mensaje(msj_rutina)

        except Exception as e:
            print(f"❌ Error en {symbol}: {e}")

# BLOQUE DE ARRANQUE (Sin errores de espacio)
if __name__ == "__main__":
    ejecutar_bot()



