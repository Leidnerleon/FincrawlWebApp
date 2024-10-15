import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from auth import get_favorites
import requests
import pandas as pd

st.title("Analyse")

# Favoriten aus dem Session State abrufen
if 'username' in st.session_state:
    username = st.session_state['username']
    favorites = get_favorites(username)
    selected_stock = st.selectbox("Wählen Sie eine Aktie aus Ihren Favoriten:", favorites)

    # Daten abrufen, wenn eine Aktie ausgewählt wurde
    if selected_stock:
        st.write(f"Analysiere die Aktie: {selected_stock}")

        # Historische Daten abrufen
        stock_data = yf.Ticker(selected_stock)
        historical_data = stock_data.history(period="1mo")  # Letzte 30 Tage

        # Diagramm erstellen
        fig = go.Figure()

        # Preisdiagramm hinzufügen
        fig.add_trace(go.Scatter(x=historical_data.index, y=historical_data['Close'], mode='lines', name='Schlusskurs'))

        # Layout des Diagramms
        fig.update_layout(title=f'Aktienkurs von {selected_stock}',
                          xaxis_title='Datum',
                          yaxis_title='Preis in USD',
                          template='plotly_white')

        # Diagramm anzeigen
        st.plotly_chart(fig)
        fundamental_data, bewertung = st.tabs(['Fundamental Daten', 'Bewertung'])

        with fundamental_data:
            st.header('Fundamental Daten')
            st.subheader('Cash-Flow Statement')
            url = f'https://www.alphavantage.co/query?function=CASH_FLOW&symbol={selected_stock}&apikey=W116GS453P68TF25'
            r = requests.get(url)
            data = r.json()
            #st.write("API-Antwort:", data)
            if 'annualReports' in data:
                cashflow_data = data['annualReports']

                # Umwandeln in einen DataFrame
                df = pd.DataFrame(cashflow_data)

                # Datentypen anpassen (z.B. "fiscalDateEnding" als Datum)
                df['fiscalDateEnding'] = pd.to_datetime(df['fiscalDateEnding'])

                # Setze das Datum als Index und entferne die Spalte "currency"
                df.set_index('fiscalDateEnding', inplace=True)

                # Invertiere den DataFrame (transponiere ihn)
                df_inverted = df.T

                # Anzeigen der Daten
                st.dataframe(df_inverted)
            else:
                st.warning(f"Keine Cashflow-Daten für {selected_stock} gefunden.")

            st.subheader('Balance Sheet')
            url2 = f'https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol={selected_stock}&apikey=W116GS453P68TF25'
            r2 = requests.get(url2)
            data2 = r2.json()
            if 'annualReports' in data2:
                balance_data = data2['annualReports']

                # Umwandeln in einen DataFrame
                df2 = pd.DataFrame(balance_data)

                # Datentypen anpassen (z.B. "fiscalDateEnding" als Datum)
                df2['fiscalDateEnding'] = pd.to_datetime(df2['fiscalDateEnding'])

                # Setze das Datum als Index und entferne die Spalte "currency"
                df2.set_index('fiscalDateEnding', inplace=True)

                # Invertiere den DataFrame (transponiere ihn)
                df2_inverted = df2.T

                # Anzeigen der Daten
                st.dataframe(df2_inverted)
            else:
                st.warning(f"Keine Cashflow-Daten für {selected_stock} gefunden.")

        with bewertung:
            st.header('Bewertung')
else:
    st.warning("Sie haben noch keine Favoriten hinzugefügt.")