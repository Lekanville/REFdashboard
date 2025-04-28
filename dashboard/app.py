import streamlit as st
import pandas as pd
import numpy as np
import yaml
from code.authentication import *
from code.dashboard import render_dashboard

def initialize_session_state():
    if 'name' not in st.session_state:
        st.session_state['name'] = None
    if 'logout' not in st.session_state:
        st.session_state['logout'] = None
    if 'authentication_status' not in st.session_state:
        st.session_state['authentication_status'] = None
    if 'username' not in st.session_state:
        st.session_state['username'] = None

initialize_session_state()

# with open('../config.yaml', 'w') as file:
#     yaml.dump(config, file, default_flow_style=False)

# Dashboard
st.set_page_config(layout="wide")
st.title('FHLS REF2029 dashboard')
st.sidebar.header('Account details')

# Authentication
authenticator.login()

if st.session_state["authentication_status"]:
    render_dashboard(st.session_state, authenticator, st)
elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')