import pandas_ta as ta
from sklearn.ensemble import RandomForestClassifier

def preparar_ia(df):
    df['RSI'] = ta.rsi(df['close'], length=14)
    df['EMA_20'] = ta.ema(df['close'], length=20)
    df['retorno'] = df['close'].pct_change()
    df['target'] = (df['close'].shift(-1) > df['close']).astype(int)
    df = df.dropna()
    features = ['RSI', 'EMA_20', 'retorno', 'volume']
    X = df[features]
    y = df['target']
    modelo = RandomForestClassifier(n_estimators=100, random_state=42)
    modelo.fit(X, y)
    return modelo, features
