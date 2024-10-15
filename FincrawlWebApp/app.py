import streamlit as st
from auth import authenticate_user, register_user  # Funktion zum Authentifizieren des Benutzers

# --- Login-Seite ---

def show_authentication():
    # Auswahl zwischen Login und Registrierung
    auth_option = st.radio("Wählen Sie eine Option:", ("Login", "Registrieren"))

    if auth_option == "Login":
        show_login()
    elif auth_option == "Registrieren":
        show_registration()

def show_login():
    st.title("Login")

    # Eingabefelder für Benutzername und Passwort
    username = st.text_input("Benutzername")
    password = st.text_input("Passwort", type="password")

    # Login-Button
    if st.button("Einloggen"):
        if authenticate_user(username, password):
            st.session_state['username'] = username  # Benutzername speichern
            st.success(f"Willkommen, {username}!")  # Erfolgsmeldung
        else:
            st.error("Ungültiger Benutzername oder Passwort.")

def show_registration():
    st.title("Registrieren")

    # Eingabefelder für Registrierung
    new_username = st.text_input("Neuer Benutzername")
    new_password = st.text_input("Neues Passwort", type="password")

    # Registrieren-Button
    if st.button("Registrieren"):
        if register_user(new_username, new_password):
            st.success(f"Benutzer {new_username} erfolgreich registriert. Sie können sich jetzt einloggen.")
        else:
            st.error("Registrierung fehlgeschlagen. Möglicherweise ist der Benutzername bereits vergeben.")

def show_main_app():
    # --- Hauptinhalt der App, wenn der Benutzer eingeloggt ist ---
    st.title("Willkommen zu Fincrawl!")
    st.write(f"Eingeloggt als: {st.session_state['username']}")

    # Navigation und Inhalte hier einfügen
    dashboard_page = st.Page(
        page="views/Dashboard.py",
        title="Dashboard",
        icon=":material/account_circle:",
        default=True,
    )
    portfolio_page = st.Page(
        page="views/Portfolio.py",
        title="Portfolio",
        icon=":material/dashboard:",
    )

    analyse_page = st.Page(
        page="views/Analyse.py",
        title="Analyse",
        icon=":material/bar_chart:",
    )

    favoriten_page = st.Page(
        page="views/Favoriten.py",
        title="Favoriten",
        icon=":material/star:",
    )

    search_page = st.Page(
        page="views/Search.py",
        title="Suchen",
        icon=":material/search:",
    )

    ausloggen_page = st.Page(
        page="views/Ausloggen.py",
        title="Ausloggen",
    )

    pg = st.navigation(pages=[dashboard_page, portfolio_page, analyse_page, favoriten_page, search_page, ausloggen_page])

    # --- Run ---
    pg.run()

if 'username' not in st.session_state:
    show_authentication()  # Zeige die Login-Seite, wenn kein Benutzer eingeloggt ist
elif 'logged_out' in st.session_state and st.session_state['logged_out']:
    show_login()  # Zeige die Login-Seite, wenn der Benutzer sich ausgeloggt hat
else:
    show_main_app()  # Zeige die Hauptanwendung an
