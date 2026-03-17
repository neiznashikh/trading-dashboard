import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from models import get_arima_forecast, get_xgboost_forecast 

st.set_page_config(page_title="Аналитический Центр", layout="wide")
st.title("📊 Панель управления (Внутридневная аналитика)")

# 1. Боковая панель: Форма управления
st.sidebar.header("Параметры анализа")

# --- ЧТО Я ИЗМЕНИЛ: Создал Форму ---
# Все, что внутри 'with st.sidebar.form', не обновляет сайт до нажатия кнопки!
with st.sidebar.form(key='settings_form'):
    asset = st.selectbox("Выберите актив:", ["BTC-USD", "SPY", "GC=F"])
    timeframe_label = st.selectbox("Таймфрейм (размер свечи):", ["1 час", "1 день"])
    
    # Ползунок теперь безопасен, можно двигать сколько угодно
    forecast_steps = st.slider("Горизонт прогноза (шагов вперед):", 1, 10, 1)
    
    st.markdown("**Технические индикаторы**")
    show_sma20 = st.checkbox("Показать SMA 20 (Быстрый тренд)")
    show_sma50 = st.checkbox("Показать SMA 50 (Медленный тренд)")
    
    # ТА САМАЯ КНОПКА
    submit_button = st.form_submit_button(label='🚀 Сделать прогноз')

st.sidebar.info("BTC-USD: Биткоин\n\nSPY: Индекс S&P 500\n\nGC=F: Золото")

# Определяем интервалы для биржи на основе выбора
if timeframe_label == "1 час":
    interval = "1h"
    period = "6mo" 
    step_name = "часов"
else:
    interval = "1d"
    period = "1y" 
    step_name = "дней"

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
    st.error("⚠️ Не удалось загрузить данные. Возможно, биржа временно заблокировала запросы. Подождите 10 минут.")
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

arima_delta = 0.0
xgb_delta = 0.0

if not data.empty:
    with col1:
        arima_direction, arima_delta = get_arima_forecast(data, forecast_steps)
        st.metric(label="ARIMA (Статистика)", value=arima_direction, delta=f"{arima_delta}%")

    with col2:
        xgb_direction, xgb_delta = get_xgboost_forecast(data, forecast_steps)
        st.metric(label="XGBoost (Машинное обучение)", value=xgb_direction, delta=f"{xgb_delta}%")

with col3:
    st.metric(label="LSTM (Нейросеть)", value="Ожидает", delta="0.0%", delta_color="off")

# 5. График будущего
if not data.empty:
    st.subheader("🎯 График прогноза (Куда целятся алгоритмы)")
    
    last_price = data['Close'].iloc[-1]
    last_date = data.index[-1]
    
    if timeframe_label == "1 час":
        future_date = last_date + pd.Timedelta(hours=forecast_steps)
    else:
        future_date = last_date + pd.Timedelta(days=forecast_steps)
        
    arima_future_price = last_price * (1 + (arima_delta / 100))
    xgb_future_price = last_price * (1 + (xgb_delta / 100))
    
    plot_df = pd.DataFrame({'Реальная цена': data['Close'].tail(30)})
    plot_df.loc[future_date, 'Реальная цена'] = None 
    
    plot_df.loc[last_date, 'Прогноз ARIMA'] = last_price
    plot_df.loc[future_date, 'Прогноз ARIMA'] = arima_future_price
    
    plot_df.loc[last_date, 'Прогноз XGBoost'] = last_price
    plot_df.loc[future_date, 'Прогноз XGBoost'] = xgb_future_price
    
    st.line_chart(plot_df)
