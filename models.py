import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
import warnings

warnings.filterwarnings("ignore")

def get_arima_forecast(data, steps):
    try:
        series = data['Close'].dropna()
        model = ARIMA(series, order=(1, 1, 1))
        fitted_model = model.fit()
        forecast = fitted_model.forecast(steps=steps)
        
        last_price = series.iloc[-1]
        predicted_price = forecast.iloc[-1]
        delta_pct = ((predicted_price - last_price) / last_price) * 100
        
        if delta_pct > 0.1: direction = "Рост"
        elif delta_pct < -0.1: direction = "Спад"
        else: direction = "Боковик"
            
        return direction, round(delta_pct, 2)
    except Exception as e:
        return "Ошибка", 0.0

def get_xgboost_forecast(data, steps):
    try:
        df = data.copy()
        
        df['SMA_10'] = df['Close'].rolling(window=10).mean()
        df['SMA_30'] = df['Close'].rolling(window=30).mean()
        df['Returns'] = df['Close'].pct_change()
        
        df['Target'] = df['Close'].shift(-steps)
        
        df.dropna(inplace=True)
        
        if len(df) < 50:
            return "Мало данных", 0.0
            
        features = ['Close', 'Volume', 'SMA_10', 'SMA_30', 'Returns']
        X = df[features]
        y = df['Target']
        
        model = XGBRegressor(objective='reg:squarederror', n_estimators=100, max_depth=3, learning_rate=0.1)
        model.fit(X, y)
        
        last_known_data = pd.DataFrame([data.iloc[-1][features].values], columns=features)
        
        if last_known_data.isnull().values.any():
            return "Ошибка", 0.0
            
        predicted_price = model.predict(last_known_data)[0]
        last_price = data['Close'].iloc[-1]
        
        delta_pct = ((predicted_price - last_price) / last_price) * 100
        
        if delta_pct > 0.1: direction = "Рост"
        elif delta_pct < -0.1: direction = "Спад"
        else: direction = "Боковик"
            
        return direction, round(delta_pct, 2)
        
    except Exception as e:
        return "Ошибка", 0.0
