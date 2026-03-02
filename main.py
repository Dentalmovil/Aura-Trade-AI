import ccxt
import pandas as pd
import os
from datetime import datetime
from ia_engine import preparar_ia
from telegram_util import enviar_mensaje

# CONFIGURACIÓN DE CONEXIÓN SEGURA
exchange = ccxt.binance({
    'apiKey': os.environ.get('BINANCE_API_KEY'),
    'secret': os.environ.get('BINANCE_SECRET_KEY'),
    'enableRateLimit': True,
    'options': {'defaultType': 'spot'}
})

symbols = ['BTC/USDT', 'BNB/USDT', 'XRP/USDT', 'LTC/USDT']

def ejecutar_bot():
    print(f"Iniciando Aura Trade AI - {datetime.now()}")
    
    for symbol in symbols:
        try:
            # 1. Obtener datos del mercado
            bars = exchange.fetch_ohlcv(symbol, timeframe='1h', limit=100)
            df = pd.DataFrame(bars, columns=['ts', 'open', 'high', 'low', 'close', 'volume'])
            
            precio_actual = df['close'].iloc[-1]
            
            # 2. Análisis de IA con Probabilidad
            modelo, features, confianza = preparar_ia(df) # Ajustado para recibir confianza
            prediccion = modelo.predict(df[features].tail(1))[0]
            
            # 3. Lógica de Inversión Automática
            if prediccion == 1 and confianza > 75:
                ejecutar_orden_segura(symbol, precio_actual, confianza)
            else:
                enviar_reporte_rutina(symbol, precio_actual, confianza)

        except Exception as e:
            print(f"Error en {symbol}: {e}")

def ejecutar_orden_segura(symbol, precio, confianza):
    # Ejemplo con 20 USDT de inversión
    try:
        cantidad_usdt = 20 
        order = exchange.create_market_buy_order(symbol, cantidad_usdt)
        
        tp = precio * 1.02 # Ganancia 2%
        sl = precio * 0.99 # Stop Loss 1%
        
        # Orden de protección OCO
        exchange.private_post_order_oco({
            'symbol': symbol.replace('/', ''),
            'side': 'SELL',
            'quantity': order['filled'],
            'price': f"{tp:.4f}",
            'stopPrice': f"{sl * 1.005:.4f}",
            'stopLimitPrice': f"{sl:.4f}",
        })
        
        enviar_mensaje(f"✅ COMPRA REALIZADA: {symbol}\nConfianza: {confianza:.1f}%\nTP: {tp:.2f} | SL: {sl:.2f}")
    except Exception as e:
        enviar_mensaje(f"⚠️ Error operando {symbol}: {e}")

def enviar_reporte_rutina(symbol, precio, confianza):
    emoji = "🟢" if confianza > 80 else "🟡"
    enviar_mensaje(f"📊 MONITOR: {symbol}\nPrecio: ${precio}\nIA Confianza: {emoji} {confianza:.1f}%")

if __name__ == "__main__":
    ejecutar_bot()

