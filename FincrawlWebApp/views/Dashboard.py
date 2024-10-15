import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf
from auth import get_favorites  # Stelle sicher, dass du die auth.py importierst

st.title("Dashboard")
st.header("Aktienpreise der Favoriten")

# Überprüfen, ob der Benutzer eingeloggt ist
if 'username' in st.session_state:
    username = st.session_state['username']
    # Abrufen der Favoritenliste aus der Datenbank
    favorites = get_favorites(username)

    # Leeres DataFrame für die Ergebnisse
    stock_data = pd.DataFrame(columns=['Name', 'Aktueller Preis in €', 'KGV'])

    # Abrufen der Daten für jedes Favorit
    for symbol in favorites:
        aktie = yf.Ticker(symbol)

        try:
            # Daten abfragen
            info = aktie.info
            current_price = info.get('currentPrice', None)  # Aktuellen Preis abrufen
            stock_name = info.get('longName', symbol)  # Name der Aktie abrufen, falls verfügbar
            kgv = info.get('trailingPE', None)  # KGV abrufen

            # Abrufen des Wechselkurses USD zu EUR
            usd_to_eur = yf.Ticker('USDEUR=X').info['regularMarketPreviousClose']

            # Wenn der aktuelle Preis nicht None ist, zum DataFrame hinzufügen
            if current_price is not None and usd_to_eur is not None:
                stock_data = stock_data.append({
                    'Name': stock_name,
                    'Aktueller Preis in €': round(current_price * usd_to_eur, 2),
                    'KGV': kgv
                }, ignore_index=True)
            else:
                st.warning(f"Preis für {symbol} konnte nicht abgerufen werden.")

        except Exception as e:
            st.error(f"Fehler beim Abrufen von {symbol}: {e}")
    # Ergebnisse anzeigen
    if not stock_data.empty:
        stock_data = stock_data.round(2)
        st.dataframe(stock_data.head(), use_container_width=True)
else:
    st.warning("Bitte loggen Sie sich ein, um Ihre Favoriten anzuzeigen.")
