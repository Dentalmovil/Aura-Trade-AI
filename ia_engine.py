import pandas_ta as ta
from sklearn.ensemble import RandomForestClassifier

def preparar_ia(df):
    # Añadimos indicadores técnicos
    df['RSI'] = ta.rsi(df['close'], length=14)
    df['EMA'] = ta.ema(df['close'], length=20)
    df.dropna(inplace=True)
    
    features = ['RSI', 'EMA']
    # Objetivo: ¿El precio subió en la siguiente vela?
    df['target'] = (df['close'].shift(-1) > df['close']).astype(int)
    
    X = df[features][:-1]
    y = df['target'][:-1]
    
    modelo = RandomForestClassifier(n_estimators=100)
    modelo.fit(X, y)
    
    # Calculamos la probabilidad del último dato
    probabilidades = modelo.predict_proba(df[features].tail(1))[0]
    confianza = max(probabilidades) * 100
    
    return modelo, features, confianza


