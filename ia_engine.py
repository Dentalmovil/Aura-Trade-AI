import pandas_ta as ta
from sklearn.ensemble import RandomForestClassifier

def preparar_ia(df):
    """
    Cerebro Evolucionado de Aura Trade AI 🧠
    Añadimos Bandas de Bollinger para detectar sobreventa extrema.
    """
    # 1. Indicadores Técnicos Base
    df['RSI'] = ta.rsi(df['close'], length=14)
    df['EMA_20'] = ta.ema(df['close'], length=20)
    df['retorno'] = df['close'].pct_change()
    
    # 2. NUEVO: Bandas de Bollinger (Añade visión de volatilidad)
    bbands = ta.bbands(df['close'], length=20, std=2)
    df['BBL_20_2.0'] = bbands['BBL_20_2.0'] # Banda Inferior
    df['BBU_20_2.0'] = bbands['BBU_20_2.0'] # Banda Superior

    # 3. Definir el Target (¿El precio subió en la siguiente vela?)
    df['target'] = (df['close'].shift(-1) > df['close']).astype(int)
    
    # Limpieza de datos nulos para el entrenamiento
    df_limpio = df.dropna().copy()
    
    # 4. Selección de características (Features)
    # Ahora la IA mirará el RSI, la EMA, el volumen y las Bandas de Bollinger
    features = ['RSI', 'EMA_20', 'retorno', 'volume', 'BBL_20_2.0', 'BBU_20_2.0']
    X = df_limpio[features]
    y = df_limpio['target']
    
    # 5. Entrenamiento del Modelo RandomForest
    # Añadimos max_depth=5 para evitar que la IA "alucine" con patrones falsos
    modelo = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    modelo.fit(X, y)
    
    return modelo, features

