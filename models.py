import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import warnings

# Отключаем предупреждения математической библиотеки, чтобы они не засоряли лог
warnings.filterwarnings("ignore")

def get_arima_forecast(data, steps):
    try:
        # Берем только столбец с ценами закрытия и убираем пустые значения
        series = data['Close'].dropna()
        
        # Строим классическую модель ARIMA (настройки 1,1,1 - универсальная база)
        model = ARIMA(series, order=(1, 1, 1))
        fitted_model = model.fit()
        
        # Просим модель предсказать цену на 'steps' шагов вперед (часов или дней)
        forecast = fitted_model.forecast(steps=steps)
        
        # Сравниваем последнюю известную цену с прогнозируемой
        last_price = series.iloc[-1]
        predicted_price = forecast.iloc[-1]
        
        # Высчитываем процент изменения
        delta_pct = ((predicted_price - last_price) / last_price) * 100
        
        # Определяем направление текстом
        if delta_pct > 0.1:
            direction = "Рост"
        elif delta_pct < -0.1:
            direction = "Спад"
        else:
            direction = "Боковик"
            
        return direction, round(delta_pct, 2)
        
    except Exception as e:
        # Защита от сбоя: если график слишком короткий или модель не смогла сойтись
        return "Ошибка", 0.0
