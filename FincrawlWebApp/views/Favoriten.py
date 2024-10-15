import streamlit as st
from auth import get_favorites, save_favorite, remove_favorite  # Importiere die Funktionen für die Favoritenverwaltung

st.title("Favoriten")

# Überprüfen, ob der Benutzer eingeloggt ist
if 'username' in st.session_state:
    username = st.session_state['username']

    # Abrufen der Favoritenliste aus der Datenbank
    favorites = get_favorites(username)

    # Eingabefeld für das Hinzufügen von Aktienkürzeln
    new_favorite = st.text_input("Fügen Sie ein Aktienkürzel zu Ihren Favoriten hinzu:", value="AAPL")
    import requests

    # replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
    url = f'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={new_favorite}&apikey=W116GS453P68TF25'
    r = requests.get(url)
    data = r.json()
    st.write(data)

    # Wenn der Button gedrückt wird, wird das Aktienkürzel zur Favoritenliste hinzugefügt
    if st.button("Zu Favoriten hinzufügen"):
        if new_favorite:
            # Verhindern, dass leere oder doppelte Kürzel hinzugefügt werden
            if new_favorite not in favorites:
                save_favorite(username, new_favorite)  # In der Datenbank speichern
                favorites.append(new_favorite)  # Auch im Session State aktualisieren
        else:
            st.warning("Bitte geben Sie ein gültiges Aktienkürzel ein.")

    # Favoritenliste anzeigen
    if favorites:
        st.subheader("Ihre Favoriten:")
        for favorite in favorites:
            st.write(f"- {favorite}")

        # Möglichkeit, Favoriten zu entfernen
        remove_favorite_symbol = st.selectbox("Favoriten entfernen:", favorites)
        if st.button("Favoriten entfernen"):
            remove_favorite(username, remove_favorite_symbol)  # Aus der Datenbank entfernen
            favorites.remove(remove_favorite_symbol)  # Auch im Session State aktualisieren
    else:
        st.write("Sie haben noch keine Favoriten hinzugefügt.")
else:
    st.warning("Bitte loggen Sie sich ein, um Ihre Favoriten anzuzeigen.")