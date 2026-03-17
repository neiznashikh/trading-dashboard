import streamlit as st
import yfinance as yf
import pandas as pd
from models import get_arima_forecast

# Настройки страницы
st.set_page_config(page_title="Аналитический Центр", layout="wide")
st.title("Панель управления (Внутридневная аналитика)")

# 1. Боковая панель (Управление)
st.sidebar.header("Параметры анализа")
asset = st.sidebar.selectbox("Выберите актив:", ["BTC-USD", "SPY", "GC=F"])

# Выбор таймфрейма
timeframe_label = st.sidebar.selectbox("Таймфрейм (размер свечи):", ["1 час", "1 день"])

# Умная настройка для запроса к бирже
if timeframe_label == "1 час":
    interval = "1h"
    period = "6mo" # Для часов берем полгода данных
    step_name = "часов"
else:
    interval = "1d"
    period = "1y" # Для дней берем историю за год
    step_name = "дней"

# Умный ползунок прогноза
forecast_steps = st.sidebar.slider(f"Горизонт прогноза (вперед на X {step_name}):", 1, 10, 1)

st.sidebar.subheader("Технические индикаторы")
show_sma20 = st.sidebar.checkbox("Показать SMA 20 (Быстрый тренд)")
show_sma50 = st.sidebar.checkbox("Показать SMA 50 (Медленный тренд)")

st.sidebar.info("BTC-USD: Биткоин\n\nSPY: Индекс S&P 500\n\nGC=F: Золото")

# 2. Надежная загрузка данных с учетом нового таймфрейма
@st.cache_data
def load_data(ticker, time_interval, data_period):
    stock = yf.Ticker(ticker)
    data = stock.history(period=data_period, interval=time_interval)
    return data

data = load_data(asset, interval, period)

# 3. Главный экран: График
st.subheader(f"Исторический график: {asset} (Интервал: {timeframe_label})")

if data.empty:
    st.error("Не удалось загрузить данные. Возможно, биржа закрыта или актив не поддерживает этот таймфрейм.")
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

with col1:
    # Запускаем расчет ARIMA в реальном времени!
    if not data.empty:
        arima_direction, arima_delta = get_arima_forecast(data, forecast_steps)
        st.metric(label="ARIMA (Статистика)", value=arima_direction, delta=f"{arima_delta}%")
    else:
        st.metric(label="ARIMA (Статистика)", value="Нет данных", delta="0%")

with col2:
    st.metric(label="XGBoost (Машинное обучение)", value="Ожидает", delta="0.0%", delta_color="off")
with col3:
    st.metric(label="LSTM (Нейросеть)", value="Ожидает", delta="0.0%", delta_color="off")

# 5. Итоговый сигнал
st.subheader("Сводный прогноз для демо-счета")
st.warning(f"Рейтинг доверия: 33%. Включена только статистика. Прогноз на {forecast_steps} {step_name} вперед. Рекомендация: Ожидаем данных от всех алгоритмов.")
