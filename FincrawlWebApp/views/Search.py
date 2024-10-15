import streamlit as st
import yfinance as yf
import streamlit.components.v1 as components

# Titel der Seite
st.title("Search Aktie")

# Eingabefeld für das Ticker-Symbol
ticker_symbol = st.text_input("Geben Sie ein Ticker Symbol ein", value="AAPL")
search_button = st.button("Absenden")

# Wenn der Button gedrückt wurde, lade die Daten
if search_button and ticker_symbol:

    # 1. TradingView Chart
    st.subheader(f"TradingView Chart für {ticker_symbol}")

    # TradingView-Widget einbetten
    tradingview_widget = f"""
    <div class="tradingview-widget-container">
      <div id="tradingview_chart"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget(
      {{
      "width": 800,
      "height": 500,
      "symbol": "{ticker_symbol}",
      "interval": "D",
      "timezone": "Etc/UTC",
      "theme": "dark",
      "style": "2",
      "locale": "en",
      "toolbar_bg": "#f1f3f6",
      "enable_publishing": false,
      "allow_symbol_change": true,
      "container_id": "tradingview_chart"
      }});
      </script>
    </div>
    """
    components.html(tradingview_widget, height=500)

    # 2. Abrufen der fundamentalen Daten
    st.subheader("Fundamentale Daten")

    try:
        ticker = yf.Ticker(ticker_symbol)

        # Firmenname und Branche
        info = ticker.info
        st.write(f"**Unternehmen:** {info.get('longName', 'Nicht verfügbar')}")
        st.write(f"**Branche:** {info.get('sector', 'Nicht verfügbar')}")

        # KGV und KUV
        pe_ratio = info.get('forwardPE', 'Nicht verfügbar')
        ps_ratio = info.get('priceToSalesTrailing12Months', 'Nicht verfügbar')

        st.write(f"**KGV (Price/Earnings Ratio):** {pe_ratio}")
        st.write(f"**KUV (Price/Sales Ratio):** {ps_ratio}")

        # 3. Dividendeninformationen
        st.subheader("Dividendeninformationen")
        dividend_yield = info.get('dividendYield', 0) * 100  # In Prozent umwandeln
        payout_ratio = info.get('payoutRatio', 0) * 100

        st.write(f"**Dividendenrendite:** {dividend_yield:.2f}%")
        st.write(f"**Payout Ratio:** {payout_ratio:.2f}%")

        # Weitere nützliche Daten
        st.write(f"**Marktkapitalisierung:** {info.get('marketCap', 'Nicht verfügbar'):,} USD")
        st.write(f"**Börsenwert pro Aktie (Forward):** {info.get('targetMeanPrice', 'Nicht verfügbar')} USD")

    except Exception as e:
        st.error(f"Fehler beim Laden der Daten: {str(e)}")