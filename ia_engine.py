import pandas_ta as ta
from sklearn.ensemble import RandomForestClassifier

def preparar_ia(df):
    # Indicadores actuales
    df['RSI'] = ta.rsi(df['close'], length=14)
    df['EMA'] = ta.ema(df['close'], length=20)
    
    # --- NUEVO: Añadimos Volatilidad (ATR) ---
    # El ATR mide qué tan grandes son las velas actuales
    df['ATR'] = ta.atr(df['high'], df['low'], df['close'], length=14)
    
    df.dropna(inplace=True)

    # Añadimos ATR a las características que estudia la IA
    features = ['RSI', 'EMA', 'ATR']
    
    # Objetivo: ¿El precio subió en la siguiente vela?
    df['target'] = (df['close'].shift(-1) > df['close']).astype(int)

    X = df[features][:-1]
    y = df['target'][:-1]

    modelo = RandomForestClassifier(n_estimators=100)
    modelo.fit(X, y)

    # Calculamos la probabilidad con los nuevos datos
    probabilidades = modelo.predict_proba(df[features].tail(1))[0]
    confianza = max(probabilidades) * 100

    return modelo, features, confianza



