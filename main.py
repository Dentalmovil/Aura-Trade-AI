import ccxt
import pandas as pd
from datetime import datetime
from ia_engine import preparar_ia
from telegram_util import enviar_mensaje

# Monedas a vigilar (BNB, XRP, LTC y BTC como base)
symbols = ['BTC/USDT', 'BNB/USDT', 'XRP/USDT', 'LTC/USDT']
exchange = ccxt.binance()

def ejecutar_bot():
    hora_actual = datetime.now().hour
    # Modo nocturno: de 11 PM a 7 AM (UTC)
    es_noche = hora_actual >= 23 or hora_actual <= 7
    
    resumen = "🤖 *REPORTAJE DE ACTIVIDAD AURA AI*\n\n"
    total_retorno_24h = 0
    enviar_reporte_rutina = not es_noche 

    for symbol in symbols:
        try:
            bars = exchange.fetch_ohlcv(symbol, timeframe='1h', limit=24)
            df = pd.DataFrame(bars, columns=['ts', 'open', 'high', 'low', 'close', 'volume'])
            
            precio_actual = df['close'].iloc[-1]
            precio_hace_1h = df['close'].iloc[-2]
            
            # 1. Alerta de Emergencia (Si cae más del 5% en 1h)
            cambio_1h = ((precio_actual - precio_hace_1h) / precio_hace_1h) * 100
            if cambio_1h <= -5.0:
                enviar_mensaje(f"🚨 *MODO EMERGENCIA: {symbol}*\n📉 Caída crítica del {cambio_1h:.2f}% en la última hora.")

            # 2. Análisis de IA
            modelo, features = preparar_ia(df)
            prediccion = modelo.predict(df[features].tail(1))[0]
            
            # 3. Cálculo de Ganancia 24h
            retorno_24h = ((precio_actual - df['close'].iloc[0]) / df['close'].iloc[0]) * 100
            total_retorno_24h += retorno_24h
            
            if prediccion == 1:
                enviar_mensaje(f"🚀 *SEÑAL DE COMPRA: {symbol}*\n💰 Precio: ${precio_actual:,.4f}\n📊 Rendimiento 24h: {retorno_24h:+.2f}%")
            
            resumen += f"✅ {symbol}: ${precio_actual:,.2f} ({retorno_24h:+.2f}%)\n"
            
        except Exception as e:
            print(f"Error en {symbol}: {e}")

    # Enviar reporte solo si es de día
    if enviar_reporte_rutina:
        promedio = total_retorno_24h / len(symbols)
        resumen += f"\n💰 *Rendimiento Portafolio 24h:* {promedio:+.2f}%"
        enviar_mensaje(resumen)
    else:
        print("🌙 Modo Nocturno: Solo se enviarán señales de compra o emergencias.")

if __name__ == "__main__":
    ejecutar_bot()
