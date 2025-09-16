"""Authentication module for the geodata chatbot."""

import streamlit as st


def check_password():
    """Returns `True` if the user had the correct password or if DEBUG mode is enabled."""

    # Check if DEBUG mode is enabled (bypasses password in local development)
    try:
        if st.secrets.get("DEBUG", "false").lower() == "true":
            return True
    except Exception:
        # If secrets.toml doesn't exist or can't be read, continue with password check
        pass

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😞 Password incorrect")
        return False
    else:
        # Password correct.
        return True