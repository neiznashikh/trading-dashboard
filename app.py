import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
# Подключаем ТЕПЕРЬ ДВЕ модели из нашего математического файла!
from models import get_arima_forecast, get_xgboost_forecast 

# Настройки страницы
st.set_page_config(page_title="Аналитический Центр", layout="wide")
st.title("📊 Панель управления (Внутридневная аналитика)")

# 1. Боковая панель (Управление)
st.sidebar.header("Параметры анализа")
asset = st.sidebar.selectbox("Выберите актив:", ["BTC-USD", "SPY", "GC=F"])

timeframe_label = st.sidebar.selectbox("Таймфрейм (размер свечи):", ["1 час", "1 день"])

if timeframe_label == "1 час":
    interval = "1h"
    period = "6mo" 
    step_name = "часов"
else:
    interval = "1d"
    period = "1y" 
    step_name = "дней"

# Тот самый ползунок, который теперь будет управлять графиком будущего
forecast_steps = st.sidebar.slider(f"Горизонт прогноза (вперед на X {step_name}):", 1, 10, 1)

st.sidebar.subheader("Технические индикаторы")
show_sma20 = st.sidebar.checkbox("Показать SMA 20 (Быстрый тренд)")
show_sma50 = st.sidebar.checkbox("Показать SMA 50 (Медленный тренд)")

# 2. Надежная загрузка данных
@st.cache_data
def load_data(ticker, time_interval, data_period):
    stock = yf.Ticker(ticker)
    data = stock.history(period=data_period, interval=time_interval)
    return data

data = load_data(asset, interval, period)

# 3. Главный экран: График истории
st.subheader(f"📈 Исторический график: {asset} (Интервал: {timeframe_label})")

if data.empty:
    st.error("⚠️ Не удалось загрузить данные.")
else:
    chart_data = pd.DataFrame()
    chart_data['Цена'] = data['Close']
    
    if show_sma20:
        chart_data['SMA 20'] = data['Close'].rolling(window=20).mean()
    if show_sma50:
        chart_data['SMA 50'] = data['Close'].rolling(window=50).mean()

    st.line_chart(chart_data)

# 4. Блок "Консилиум алгоритмов"
st.subheader("🤖 Консилиум алгоритмов")
col1, col2, col3 = st.columns(3)

# Переменные для графика будущего
arima_delta = 0.0
xgb_delta = 0.0

with col1:
    if not data.empty:
        arima_direction, arima_delta = get_arima_forecast(data, forecast_steps)
        st.metric(label="ARIMA (Статистика)", value=arima_direction, delta=f"{arima_delta}%")

with col2:
    if not data.empty:
        xgb_direction, xgb_delta = get_xgboost_forecast(data, forecast_steps)
        st.metric(label="XGBoost (Машинное обучение)", value=xgb_direction, delta=f"{xgb_delta}%")

with col3:
    st.metric(label="LSTM (Нейросеть)", value="Ожидает", delta="0.0%", delta_color="off")

# --- НОВЫЙ БЛОК: ГРАФИК БУДУЩЕГО ---
if not data.empty:
    st.subheader("🎯 График прогноза (Куда целятся алгоритмы)")
    
    last_price = data['Close'].iloc[-1]
    last_date = data.index[-1]
    
    # Вычисляем дату/время в будущем на основе вашего ползунка
    if timeframe_label == "1 час":
        future_date = last_date + pd.Timedelta(hours=forecast_steps)
    else:
        future_date = last_date + pd.Timedelta(days=forecast_steps)
        
    # Высчитываем будущую цену в долларах
    arima_future_price = last_price * (1 + (arima_delta / 100))
    xgb_future_price = last_price * (1 + (xgb_delta / 100))
    
    # Берем последние 30 точек истории, чтобы график был крупным и понятным
    plot_df = pd.DataFrame({'Реальная цена': data['Close'].tail(30)})
    
    # Добавляем точку будущего в таблицу
    plot_df.loc[future_date, 'Реальная цена'] = None 
    
    # Рисуем линию ARIMA от сегодня в будущее
    plot_df.loc[last_date, 'Прогноз ARIMA'] = last_price
    plot_df.loc[future_date, 'Прогноз ARIMA'] = arima_future_price
    
    # Рисуем линию XGBoost от сегодня в будущее
    plot_df.loc[last_date, 'Прогноз XGBoost'] = last_price
    plot_df.loc[future_date, 'Прогноз XGBoost'] = xgb_future_price
    
    # Выводим красивый график с тремя линиями
    st.line_chart(plot_df)
