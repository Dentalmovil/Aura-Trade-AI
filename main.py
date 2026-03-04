import ccxt
import pandas as pd
import os
import csv
from datetime import datetime
from ia_engine import preparar_ia
from telegram_util import enviar_mensaje

# --- 1. CONFIGURACIÓN DEL EXCHANGE ---
exchange = ccxt.binance({
    'apiKey': os.environ.get('BINANCE_API_KEY'),
    'secret': os.environ.get('BINANCE_SECRET_KEY'),
    'enableRateLimit': True,
    'options': {'defaultType': 'spot', 'adjustForTimeDifference': True}
})
exchange.urls['api'] = 'https://api1.binance.com'

# --- 2. CONFIGURACIÓN DEL BOT ---
SYMBOLS = [
    'BTC/USDT', 'BNB/USDT', 'XRP/USDT', 'LTC/USDT', 
    'SOL/USDT', 'ADA/USDT', 'DOT/USDT', 'MATIC/USDT'
]
LOG_FILE = 'historial_operaciones.csv'

def guardar_operacion(datos):
    """Guarda la señal en un CSV para el resumen semanal."""
    archivo_existe = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, mode='a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['fecha', 'simbolo', 'precio', 'confianza', 'tp', 'sl'])
        if not archivo_existe: writer.writeheader()
        writer.writerow(datos)

def ejecutar_bot():
    print(f"🚀 Aura Trade AI V3.5 Activo - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    for symbol in SYMBOLS:
        try:
            # Obtener datos (300 velas para SMA 200)
            bars = exchange.fetch_ohlcv(symbol, timeframe='1h', limit=300)
            df = pd.DataFrame(bars, columns=['ts', 'open', 'high', 'low', 'close', 'volume'])
            df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']].astype(float)

            # --- CÁLCULOS TÉCNICOS ---
            precio_actual = df['close'].iloc[-1]
            sma_200 = df['close'].rolling(window=200).mean().iloc[-1]
            tendencia_alcista = precio_actual > sma_200

            # --- GESTIÓN DE RIESGO ---
            # Stop Loss (SL): 0.5% bajo el mínimo de las últimas 5h
            # Take Profit (TP): Ratio 2:1 basado en el riesgo
            sl_sugerido = df['low'].tail(5).min() * 0.995
            riesgo = precio_actual - sl_sugerido
            tp_sugerido = precio_actual + (riesgo * 2)

            # --- CONSULTA IA ---
            modelo, features, confianza = preparar_ia(df)
            prediccion = modelo.predict(df[features].tail(1))[0]

            # --- LÓGICA DE SEÑALES ---
            # Umbral de confianza: 80% + Tendencia Alcista obligatoria para "Fuerte"
            enviar_alerta = False
            
            if prediccion == 1 and confianza > 80 and tendencia_alcista:
                emoji, accion = "🔥", "🚀 COMPRA FUERTE (Tendencia OK)"
                enviar_alerta = True
            elif prediccion == 1 and confianza > 65:
                nota = "📈" if tendencia_alcista else "⚠️ BAJO MEDIA 200"
                emoji, accion = "🟢", f"✅ COMPRA MODERADA ({nota})"
                enviar_alerta = True
            else:
                emoji, accion = "⚪", "⏳ ESPERAR / NEUTRO"

            # --- ALERTAS Y REGISTRO ---
            if enviar_alerta:
                msj = (f"📊 *REPORTE:* {symbol}\n"
                       f"💵 Precio: ${precio_actual:,.2f}\n"
                       f"🧠 IA: {emoji} {confianza:.1f}%\n"
                       f"📝 *Sugerencia:* {accion}\n"
                       f"--------------------------\n"
                       f"🎯 TP: ${tp_sugerido:,.2f}\n"
                       f"🛑 SL: ${sl_sugerido:,.2f}")
                
                enviar_mensaje(msj)
                
                # Guardar para el resumen semanal
                guardar_operacion({
                    'fecha': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'simbolo': symbol,
                    'precio': precio_actual,
                    'confianza': confianza,
                    'tp': tp_sugerido,
                    'sl': sl_sugerido
                })

            # Alerta extra si el precio está rompiendo el SL calculado
            if precio_actual <= sl_sugerido and tendencia_alcista:
                enviar_mensaje(f"🚨 *ALERTA:* {symbol} ha tocado nivel de STOP LOSS (${sl_sugerido:,.2f})")

        except Exception as e:
            print(f"❌ Error en {symbol}: {e}")

if __name__ == "__main__":
    ejecutar_bot()




