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

# --- НОВЫЙ БЛОК МАШИННОГО ОБУЧЕНИЯ (XGBOOST) ---
def get_xgboost_forecast(data, steps):
    try:
        df = data.copy()
        
        # 1. Создаем "Фичи" (Features) - метрики для обучения алгоритма
        df['SMA_10'] = df['Close'].rolling(window=10).mean()
        df['SMA_30'] = df['Close'].rolling(window=30).mean()
        # Считаем процент изменения цены за прошлый день/час
        df['Returns'] = df['Close'].pct_change()
        
        # 2. Создаем "Таргет" (Target) - то, что алгоритм должен угадать (цену через 'steps' шагов)
        df['Target'] = df['Close'].shift(-steps)
        
        # Убираем строки с пустыми значениями
        df.dropna(inplace=True)
        
        # Если данных мало (например, биржа только открылась), алгоритм не сработает
        if len(df) < 50:
            return "Мало данных", 0.0
            
        # 3. Подготавливаем данные для обучения
        features = ['Close', 'Volume', 'SMA_10', 'SMA_30', 'Returns']
        X = df[features]
        y = df['Target']
        
        # 4. Создаем и обучаем модель (учим ее находить закономерности)
        model = XGBRegressor(objective='reg:squarederror', n_estimators=100, max_depth=3, learning_rate=0.1)
        model.fit(X, y)
        
        # 5. Делаем прогноз на основе САМЫХ ПОСЛЕДНИХ данных с биржи
        last_known_data = pd.DataFrame([data.iloc[-1][features].values], columns=features)
        
        # Защита от пустых метрик в последней строке (если SMA еще не рассчиталась)
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
