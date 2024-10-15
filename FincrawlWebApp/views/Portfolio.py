import requests
import streamlit as st
import sqlite3
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime

st.title("Portfolio")


# Funktion zum Erstellen der Transaktionstabelle
def create_transactions_table():
    conn = sqlite3.connect('users.db')  # Verbindung zur Datenbank
    cursor = conn.cursor()

    # Erstelle die Tabelle "transactions" falls sie nicht existiert
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            stock_symbol TEXT,
            quantity INTEGER,
            price_per_stock REAL,
            transaction_type TEXT,
            dollar_euro TEXT,
            date TEXT,
            FOREIGN KEY (username) REFERENCES users (username)
        )
    ''')
    conn.commit()
    conn.close()


# Funktion zum Hinzufügen einer Transaktion
def add_transaction(username, stock_symbol, quantity, price_per_stock, dollar_euro, transaction_type):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    date_now = datetime.now().strftime("%Y-%m-%d")
    cursor.execute('''
        INSERT INTO transactions (username, stock_symbol, quantity, price_per_stock, dollar_euro, transaction_type, date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (username, stock_symbol, quantity, price_per_stock, dollar_euro, transaction_type, date_now))

    conn.commit()
    conn.close()

def create_stock_groups_table():
    conn = sqlite3.connect('users.db')  # Verbindung zur Datenbank
    cursor = conn.cursor()

    # Erstelle die Tabelle "stock_groups" falls sie nicht existiert
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_groups (
            username TEXT,
            stock_symbol TEXT,
            group_name TEXT,
            FOREIGN KEY (username) REFERENCES users (username)
        )
    ''')
    conn.commit()
    conn.close()

# Funktion zum Abrufen des Portfolios
def get_portfolio(username):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Aggregiere alle Transaktionen und berechne den aktuellen Bestand
    cursor.execute('''
        SELECT t.stock_symbol,
               SUM(
                   CASE WHEN t.transaction_type = 'Kaufen' THEN t.quantity
                        WHEN t.transaction_type = 'Verkaufen' THEN -t.quantity
                   END
               ) as total_quantity,
               t.dollar_euro,
               sg.group_name
        FROM transactions t
        LEFT JOIN stock_groups sg ON t.username = sg.username AND t.stock_symbol = sg.stock_symbol
        WHERE t.username = ?
        GROUP BY t.stock_symbol
        HAVING total_quantity > 0
    ''', (username,))

    portfolio = cursor.fetchall()
    conn.close()

    return portfolio

def assign_stock_to_group(username, stock_symbol, group_name):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Überprüfen, ob die Zuordnung bereits existiert
    cursor.execute('''
        SELECT * FROM stock_groups WHERE username = ? AND stock_symbol = ? AND group_name = ?
    ''', (username, stock_symbol, group_name))
    if cursor.fetchone():
        st.warning(f"Aktie '{stock_symbol}' ist bereits in der Gruppe '{group_name}'.")
    else:
        cursor.execute('''
            INSERT INTO stock_groups (username, stock_symbol, group_name)
            VALUES (?, ?, ?)
        ''', (username, stock_symbol, group_name))
        conn.commit()
    conn.close()

def manage_groups():
    st.subheader("Gruppenverwaltung")

    # Formular zum Erstellen einer neuen Gruppe
    with st.expander("Neue Gruppe erstellen"):
        new_group = st.text_input("Gruppenname")
        create_group_button = st.button("Gruppe erstellen")
        if create_group_button and new_group:
            st.success(f"Gruppe '{new_group}' wurde erfolgreich erstellt!")

    # Formular zum Zuweisen einer Aktie zu einer Gruppe
    with st.expander("Aktie einer Gruppe zuweisen"):
        stock_symbol = st.text_input("Aktienkürzel", key="assign_stock_symbol")
        user_groups = get_user_groups(st.session_state['username'])
        group_name = st.selectbox("Gruppe auswählen", user_groups, key="assign_group_name")
        assign_button = st.button("Aktie zuweisen")
        if assign_button and stock_symbol and group_name:
            assign_stock_to_group(st.session_state['username'], stock_symbol, group_name)
            st.success(f"Aktie '{stock_symbol}' wurde der Gruppe '{group_name}' zugewiesen!")

    # Formular zum Entfernen einer Aktie aus einer Gruppe
    with st.expander("Aktie aus Gruppe entfernen"):
        stock_symbol = st.text_input("Aktienkürzel", key="remove_stock_symbol")
        user_groups = get_user_groups(st.session_state['username'])
        group_name = st.selectbox("Gruppe auswählen", user_groups, key="remove_group_name")
        remove_button = st.button("Aktie entfernen")
        if remove_button and stock_symbol and group_name:
            remove_stock_from_group(st.session_state['username'], stock_symbol, group_name)
            st.success(f"Aktie '{stock_symbol}' wurde aus der Gruppe '{group_name}' entfernt!")

def remove_stock_from_group(username, stock_symbol, group_name):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('''
        DELETE FROM stock_groups WHERE username = ? AND stock_symbol = ? AND group_name = ?
    ''', (username, stock_symbol, group_name))
    conn.commit()
    conn.close()

# Erstelle die Transaktionstabelle falls sie nicht existiert
create_transactions_table()
create_stock_groups_table()
def get_dollar_to_euro_rate():
    url = "https://api.exchangerate-api.com/v4/latest/USD"
    response = requests.get(url)
    data = response.json()
    return data["rates"]["EUR"]

def buy_sell_form():
    st.subheader("Portfolio Management")

    # Aktien kaufen Formular
    with st.expander("Aktien kaufen"):
        st.write("Füllen Sie die Informationen aus, um eine Aktie zu kaufen:")
        symbol = st.text_input("Aktienkürzel", key="buy_symbol")
        quantity = st.number_input("Anzahl", min_value=0.000001, key="buy_quantity")
        buy_price = st.number_input("Kaufpreis pro Aktie", min_value=0.01, format="%.2f", key="buy_price")
        dollar_euro = st.selectbox("In Euro oder Dollar?", ("Euro", "Dollar"))
        buy_button = st.button("Aktie kaufen")

        if buy_button and symbol and quantity > 0:
            add_transaction(st.session_state['username'], symbol, quantity, buy_price, dollar_euro, "Kaufen")
            st.success(f"{quantity} Aktien von {symbol} wurden erfolgreich gekauft!")

    # Aktien verkaufen Formular
    with st.expander("Aktien verkaufen"):
        st.write("Füllen Sie die Informationen aus, um eine Aktie zu verkaufen:")
        symbol = st.text_input("Aktienkürzel", key="sell_symbol")
        quantity = st.number_input("Anzahl", min_value=0.000001, key="sell_quantity")
        sell_price = st.number_input("Verkaufspreis pro Aktie", min_value=0.01, format="%.2f", key="sell_price")
        sell_button = st.button("Aktie verkaufen")

        if sell_button and symbol and quantity > 0:
            add_transaction(st.session_state['username'], symbol, quantity, sell_price, "Euro", "Verkaufen")
            st.success(f"{quantity} Aktien von {symbol} wurden erfolgreich verkauft!")

def get_user_groups(username):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT DISTINCT group_name FROM stock_groups WHERE username = ?
    ''', (username,))
    groups = [row[0] for row in cursor.fetchall() if row[0] is not None]
    conn.close()
    return groups

# Portfolio anzeigen
portfolio, portfolio_management = st.tabs(['Portfolio', 'Portfolio Management'])
portfolio_data = get_portfolio(st.session_state['username'])

with portfolio_management:
    buy_sell_form()
    manage_groups()

portfolio_data = get_portfolio(st.session_state['username'])

with portfolio:
    portfolio_df = pd.DataFrame(portfolio_data, columns=["Aktien Symbol", "Anzahl der Aktien", "Dollar/Euro", "Gruppe"])

    user_groups = get_user_groups(st.session_state['username'])
    selected_group = st.selectbox("Gruppe auswählen", ["Alle"] + user_groups)

    # Wenn eine Gruppe ausgewählt ist, filtere den DataFrame
    if selected_group != "Alle":
        portfolio_df = portfolio_df[portfolio_df["Gruppe"] == selected_group]

    # Liste mit aktuellen Preisen und Wert des Bestands initialisieren
    current_prices = []
    total_values = []

    dollar_to_euro_rate = get_dollar_to_euro_rate()

    for index, row in portfolio_df.iterrows():
        symbol = row["Aktien Symbol"]
        quantity = row["Anzahl der Aktien"]
        dollar_euro = row["Dollar/Euro"]

        # Abrufen des aktuellen Preises
        ticker = yf.Ticker(symbol)
        current_price = ticker.history(period="1d")["Close"].iloc[-1]

        # Überprüfen, ob die Währung Dollar ist und gegebenenfalls umrechnen
        if dollar_euro == "Dollar":
            current_price *= dollar_to_euro_rate  # Umrechnung in Euro

        current_prices.append(current_price)

        # Berechnung des Bestandswertes
        value_of_holding = current_price * quantity
        total_values.append(value_of_holding)

    # Füge aktuelle Preise und Wert des Bestands zum DataFrame hinzu
    portfolio_df["Aktueller Preis"] = current_prices
    portfolio_df["Wert des Bestands"] = total_values
    portfolio_df["Aktueller Preis"] = portfolio_df["Aktueller Preis"].round(2)
    portfolio_df["Wert des Bestands"] = portfolio_df["Wert des Bestands"].round(2)
    total_portfolio_value = portfolio_df["Wert des Bestands"].sum()
    portfolio_df = portfolio_df.drop(columns="Dollar/Euro")
    portfolio_df = portfolio_df.sort_values(by=['Wert des Bestands'], ascending=False)

    st.subheader(f"Gesamtwert des Portfolios: €{total_portfolio_value:.2f}")

    # Ausgabe des aktualisierten DataFrames
    st.dataframe(portfolio_df)

    # Erstellen des Pie Charts für die Aktienverteilung basierend auf dem Wert des Bestands
    fig = px.pie(portfolio_df, values="Wert des Bestands", names="Aktien Symbol",
                 title="Aktuelle Aktienverteilung im Portfolio")

    # Chart anzeigen
    st.plotly_chart(fig)