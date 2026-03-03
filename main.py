import ccxt
import pandas as pd
import os
from datetime import datetime
from ia_engine import preparar_ia
from telegram_util import enviar_mensaje

# 1. USAMOS LA API PÚBLICA (Para evitar el bloqueo de ubicación de GitHub)
# No enviamos apiKey ni secret aquí para que Binance nos deje pasar
exchange = ccxt.binance({
    'enableRateLimit': True,
    'options': {'defaultType': 'spot'}
})

symbols = ['BTC/USDT', 'BNB/USDT', 'XRP/USDT', 'LTC/USDT']

def ejecutar_bot():
    print(f"🚀 Aura Trade AI Iniciando - {datetime.now()}")
    enviar_mensaje("📡 *Aura Trade AI:* Iniciando análisis con API Pública...")
    
    for symbol in symbols:
        try:
            # 2. Obtener datos (Las velas son públicas, no hay bloqueo aquí)
            bars = exchange.fetch_ohlcv(symbol, timeframe='1h', limit=100)
            df = pd.DataFrame(bars, columns=['ts', 'open', 'high', 'low', 'close', 'volume'])
            precio_actual = df['close'].iloc[-1]
            
            # 3. Consultar a la IA
            modelo, features, confianza = preparar_ia(df)
            prediccion = modelo.predict(df[features].tail(1))[0]
            
            # 4. Lógica de Mensajería
            emoji = "🟢" if confianza > 80 else "🟡" if confianza > 50 else "⚪"
            
            if prediccion == 1 and confianza > 55:
                tp = precio_actual * 1.02
                sl = precio_actual * 0.99
                msj = (f"🚀 *ALERTA DE COMPRA: {symbol}*\n"
                       f"💰 Precio: ${precio_actual}\n"
                       f"📊 Confianza IA: {emoji} {confianza:.1f}%\n"
                       f"🎯 TP: {tp:.2f} | 🛑 SL: {sl:.2f}")
                enviar_mensaje(msj)
            else:
                msj_rutina = (f"📊 *MONITOR:* {symbol}\n"
                             f"💵 Precio: ${precio_actual}\n"
                             f"🧠 Confianza: {emoji} {confianza:.1f}%\n"
                             f"📝 Estado: Analizando tendencia...")
                enviar_mensaje(msj_rutina)

        except Exception as e:
            print(f"❌ Error en {symbol}: {e}")
            enviar_mensaje(f"⚠️ Error técnico en {symbol}: {e}")

if __name__ == "__main__":
    ejecutar_bot()





