import ccxt
import pandas as pd
import os
from datetime import datetime
from ia_engine import preparar_ia
from telegram_util import enviar_mensaje

# 1. CONFIGURACIÓN DE SOLO ANÁLISIS (Segura)
exchange = ccxt.binance({
    'apiKey': os.environ.get('BINANCE_API_KEY'),
    'secret': os.environ.get('BINANCE_SECRET_KEY'),
    'enableRateLimit': True,
    'options': {
        'defaultType': 'spot',
        # Esto ayuda a evitar errores de sincronización de tiempo
        'adjustForTimeDifference': True 
    }
})

symbols = ['BTC/USDT', 'BNB/USDT', 'XRP/USDT', 'LTC/USDT']

def ejecutar_bot():
    print(f"🚀 Aura Trade AI Iniciando Análisis - {datetime.now()}")
    
    for symbol in symbols:
        try:
            # 2. Obtener datos de mercado
            bars = exchange.fetch_ohlcv(symbol, timeframe='1h', limit=100)
            df = pd.DataFrame(bars, columns=['ts', 'open', 'high', 'low', 'close', 'volume'])
            
            # Aseguramos que los datos sean numéricos para la IA
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
                
            precio_actual = df['close'].iloc[-1]
            
            # 3. Consultar a la IA
            modelo, features, confianza = preparar_ia(df)
            prediccion = modelo.predict(df[features].tail(1))[0]
            
            # 4. Reporte a Telegram
            emoji = "🟢" if confianza > 75 else "🟡" if confianza > 50 else "⚪"
            accion = "POTENCIAL COMPRA" if prediccion == 1 and confianza > 70 else "MERCADO NEUTRO"
            
            msj = (f"📊 *REPORTE:* {symbol}\n"
                   f"💵 Precio: ${precio_actual:,.2f}\n"
                   f"🧠 Confianza IA: {emoji} {confianza:.1f}%\n"
                   f"📝 Sugerencia: *{accion}*")
            
            enviar_mensaje(msj)

        except Exception as e:
            # Si el error es por ubicación, intentamos un método alternativo
            print(f"❌ Error en {symbol}: {e}")
            if "restricted location" in str(e).lower():
                print(f"Reintentando {symbol} sin llaves...")
                # Aquí podrías poner el código de emergencia que te pasé antes


