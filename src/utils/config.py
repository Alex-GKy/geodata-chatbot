"""Configuration utilities for the geodata chatbot."""

import streamlit as st


def is_mining_case_enabled() -> bool:
    """
    Check if mining case is enabled via secrets configuration.

    Returns:
        bool: True if MINING_CASE secret is set to "true" (case-insensitive),
              False otherwise.
    """
    try:
        mining_value = st.secrets.get("MINING_CASE", "false")
        return str(mining_value).lower() == "true"
    except Exception:
        # If secrets file doesn't exist or secret not found, return False
        return False