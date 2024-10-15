import sqlite3
import hashlib
import streamlit as st


# SQLite-Datenbankverbindung
def create_connection():
    conn = sqlite3.connect('users.db')
    return conn


# Benutzerregistrierung
def register_user(username, password):
    conn = create_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        st.success("Benutzer erfolgreich registriert!")
    except sqlite3.IntegrityError:
        st.error("Benutzername bereits vergeben.")
    finally:
        conn.close()


# Benutzeranmeldung
def login_user(username, password):
    conn = create_connection()
    cursor = conn.cursor()

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed_password))

    user = cursor.fetchone()
    conn.close()

    return user


# Datenbank und Tabellen erstellen (einmalig ausführen)
def create_tables():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        username TEXT UNIQUE,
                        password TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS favorites (
                        id INTEGER PRIMARY KEY,
                        username TEXT,
                        favorite TEXT)''')

    conn.commit()
    conn.close()


# Initialisiere die Datenbank
create_tables()


# Favoriten abrufen
def get_favorites(username):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT favorite FROM favorites WHERE username=?", (username,))
    favorites = [row[0] for row in cursor.fetchall()]

    conn.close()
    return favorites


# Favoriten speichern
def save_favorite(username, favorite):
    conn = create_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO favorites (username, favorite) VALUES (?, ?)", (username, favorite))
        conn.commit()
        st.success(f"{favorite} zu den Favoriten hinzugefügt!")
    except sqlite3.IntegrityError:
        st.warning(f"{favorite} ist bereits in deinen Favoriten.")
    finally:
        conn.close()

def remove_favorite(username, favorite):
    # Verbindung zur Datenbank herstellen
    conn = create_connection()
    cursor = conn.cursor()

    try:
        # Entferne das Aktienkürzel aus der Favoritenliste des Benutzers
        cursor.execute("DELETE FROM favorites WHERE username = ? AND favorite = ?", (username, favorite))
        conn.commit()  # Änderungen speichern
        st.success(f"{favorite} aus den Favoriten entfernt!")
        # Optional: Rückmeldung zur Anzahl der betroffenen Zeilen
        if cursor.rowcount == 0:
            print(f"Favorit {favorite} für Benutzer {username} nicht gefunden.")
        else:
            print(f"Favorit {favorite} erfolgreich entfernt.")
    except Exception as e:
        print(f"Fehler beim Entfernen des Favoriten: {e}")
    finally:
        cursor.close()
        conn.close()  # Verbindung zur Datenbank schließen


def authenticate_user(username, password):
    # Hier kommt dein Code zur Authentifizierung, z.B. durch Abgleich mit der Datenbank
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return user is not None  # Gibt True zurück, wenn der Benutzer gefunden wurde