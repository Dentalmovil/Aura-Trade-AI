import ccxt
import pandas as pd
import os
from datetime import datetime
from ia_engine import preparar_ia
from telegram_util import enviar_mensaje

# 1. CONFIGURACIÓN ULTRA-LIGERA
# Forzamos a que no intente cargar nada de la cuenta privada
exchange = ccxt.binance({
    'enableRateLimit': True,
    'options': {
        'defaultType': 'spot'
    }
})

symbols = ['BTC/USDT', 'BNB/USDT', 'XRP/USDT', 'LTC/USDT']

def ejecutar_bot():
    print(f"🚀 Aura Trade AI Iniciando - {datetime.now()}")
    enviar_mensaje("📡 *Aura Trade AI:* Analizando precios actuales...")
    
    for symbol in symbols:
        try:
            # 2. Obtener solo los precios (esto rara vez se bloquea)
            bars = exchange.fetch_ohlcv(symbol, timeframe='1h', limit=100)
            df = pd.DataFrame(bars, columns=['ts', 'open', 'high', 'low', 'close', 'volume'])
            precio_actual = df['close'].iloc[-1]
            
            # 3. Consultar a la IA
            modelo, features, confianza = preparar_ia(df)
            prediccion = modelo.predict(df[features].tail(1))[0]
            
            # 4. Lógica de mensajes para monitoreo
            emoji = "🟢" if confianza > 75 else "🟡" if confianza > 50 else "⚪"
            
            # Siempre te mandará el reporte para que veas que funciona
            msj = (f"📊 *MONITOR:* {symbol}\n"
                   f"💵 Precio: ${precio_actual}\n"
                   f"🧠 Confianza IA: {emoji} {confianza:.1f}%\n"
                   f"📝 Acción: {'COMPRA' if prediccion == 1 and confianza > 70 else 'ESPERAR'}")
            
            enviar_mensaje(msj)

        except Exception as e:
            # Si hay un error de ubicación, lo saltamos y probamos la siguiente moneda
            print(f"❌ Error en {symbol}: {e}")
            if "restricted location" not in str(e).lower():
                enviar_mensaje(f"⚠️ Nota en {symbol}: {e}")

if __name__ == "__main__":
    ejecutar_bot()





