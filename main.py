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
    print(f"🚀 Aura Trade AI V4.0 (ATR Mode) Activo - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    for symbol in SYMBOLS:
        try:
            # Obtener datos (300 velas para SMA 200 y ATR)
            bars = exchange.fetch_ohlcv(symbol, timeframe='1h', limit=300)
            df = pd.DataFrame(bars, columns=['ts', 'open', 'high', 'low', 'close', 'volume'])
            df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']].astype(float)

            # --- CONSULTA IA (Ahora calcula el ATR internamente) ---
            modelo, features, confianza = preparar_ia(df)
            prediccion = modelo.predict(df[features].tail(1))[0]

            # --- CÁLCULOS TÉCNICOS ---
            precio_actual = df['close'].iloc[-1]
            sma_200 = df['close'].rolling(window=200).mean().iloc[-1]
            tendencia_alcista = precio_actual > sma_200
            
            # Recuperamos el valor del ATR calculado en ia_engine
            atr_actual = df['ATR'].iloc[-1]

            # --- GESTIÓN DE RIESGO DINÁMICA (ATR) ---
            # Stop Loss (SL): Precio actual menos 1.5 veces la volatilidad (ATR)
            # Esto evita que movimientos bruscos normales te saquen de la jugada.
            sl_sugerido = precio_actual - (atr_actual * 1.5)
            riesgo = precio_actual - sl_sugerido
            
            # Take Profit (TP): Ratio 2:1 basado en el riesgo real
            tp_sugerido = precio_actual + (riesgo * 2)

            # --- LÓGICA DE SEÑALES ---
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

                guardar_operacion({
                    'fecha': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'simbolo': symbol,
                    'precio': precio_actual,
                    'confianza': confianza,
                    'tp': tp_sugerido,
                    'sl': sl_sugerido
                })

            # Alerta extra si el precio rompe el SL dinámico
            if precio_actual <= sl_sugerido and tendencia_alcista:
                enviar_mensaje(f"🚨 *ALERTA:* {symbol} ha tocado nivel de STOP LOSS DINÁMICO (${sl_sugerido:,.2f})")

        except Exception as e:
            print(f"❌ Error en {symbol}: {e}")

if __name__ == "__main__":
    ejecutar_bot()
