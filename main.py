import ccxt
import pandas as pd
import os
from datetime import datetime
from ia_engine import preparar_ia
from telegram_util import enviar_mensaje

# 1. CONFIGURACIÓN DE SOLO LECTURA
# Eliminamos cualquier rastro de llaves privadas para que Binance no bloquee
exchange = ccxt.binance({
    'enableRateLimit': True,
    'options': {
        'defaultType': 'spot',
        'adjustForTimeDifference': True
    }
})

symbols = ['BTC/USDT', 'BNB/USDT', 'XRP/USDT', 'LTC/USDT']

def ejecutar_bot():
    print(f"🚀 Aura Trade AI Iniciando - {datetime.now()}")
    enviar_mensaje("📡 *Aura Trade AI:* Iniciando análisis de mercado...")
    
    for symbol in symbols:
        try:
            # 2. Obtener solo velas (esto es público y no requiere cuenta)
            bars = exchange.fetch_ohlcv(symbol, timeframe='1h', limit=100)
            df = pd.DataFrame(bars, columns=['ts', 'open', 'high', 'low', 'close', 'volume'])
            precio_actual = df['close'].iloc[-1]
            
            # 3. Consultar a la IA (tu ia_engine.py actual)
            modelo, features, confianza = preparar_ia(df)
            
            # Realizar predicción
            input_data = df[features].tail(1)
            prediccion = modelo.predict(input_data)[0]
            
            # 4. Lógica de mensajes
            emoji = "🟢" if confianza > 80 else "🟡" if confianza > 55 else "⚪"
            
            if prediccion == 1 and confianza > 60:
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
                             f"📝 Estado: Esperando señal clara.")
                enviar_mensaje(msj_rutina)

        except Exception as e:
            # Si hay error, lo imprimimos pero que no detenga el bot
            print(f"❌ Error en {symbol}: {e}")
            # Solo mandamos error a Telegram si es algo distinto al bloqueo de ubicación
            if "restricted location" not in str(e):
                enviar_mensaje(f"⚠️ Aviso en {symbol}: {e}")

if __name__ == "__main__":
    ejecutar_bot()





