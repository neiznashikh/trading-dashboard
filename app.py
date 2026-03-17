import streamlit as st
import yfinance as yf

# Настройки страницы
st.set_page_config(page_title="Аналитический Центр", layout="wide")
st.title("📊 Панель управления (MVP версия)")

# 1. Боковая панель (Управление)
st.sidebar.header("Параметры анализа")
asset = st.sidebar.selectbox("Выберите актив:", ["BTC-USD", "SPY", "GC=F"])
days_ahead = st.sidebar.slider("Горизонт прогноза (дней):", 1, 7, 1)

st.sidebar.info("BTC-USD: Биткоин\n\nSPY: Индекс S&P 500\n\nGC=F: Золото")

# 2. Надежная загрузка данных
@st.cache_data
def load_data(ticker):
    # Используем более стабильный метод получения истории за 1 год
    stock = yf.Ticker(ticker)
    data = stock.history(period="1y")
    return data

data = load_data(asset)

# 3. Главный экран: График
st.subheader(f"📈 Исторический график: {asset} (Цена закрытия)")

# Защита от пустых данных: проверяем, что биржа отдала цифры
if data.empty:
    st.error("⚠️ Не удалось загрузить данные. Возможно, временный сбой соединения с биржей.")
else:
    st.line_chart(data['Close'])

# 4. Блок "Консилиум алгоритмов"
st.subheader("🤖 Консилиум алгоритмов (Демо-режим)")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="ARIMA (Статистика)", value="Рост", delta="+1.2%")
with col2:
    st.metric(label="XGBoost (Машинное обучение)", value="Боковик", delta="0.0%", delta_color="off")
with col3:
    st.metric(label="LSTM (Нейросеть)", value="Спад", delta="-0.5%", delta_color="inverse")

# 5. Итоговый сигнал
st.subheader("⚡ Сводный прогноз для демо-счета")
st.warning(f"Рейтинг доверия: 33%. Модели расходятся в прогнозе на {days_ahead} дн. Рекомендация: Воздержаться от сделки.")
