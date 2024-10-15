import streamlit as st

if st.button("Klicken zum Ausloggen!"):
            # Entferne den Benutzernamen aus dem Session State
            del st.session_state['username']
            st.success("Sie wurden erfolgreich ausgeloggt.")