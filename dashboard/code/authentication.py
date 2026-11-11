from pathlib import Path

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

CONFIG_PATH = Path(__file__).resolve().parents[2] / "dashboard" / "config.yaml"

with CONFIG_PATH.open() as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
)


def reset_password(st):
    if st.session_state["authentication_status"]:
        try:
            if authenticator.reset_password(st.session_state["username"]):
                st.warning(
                    "Password updates are disabled in this build. Keep auth secrets outside the repository."
                )
                st.success('Password modified successfully')
        except Exception as e:
            st.error(e)
