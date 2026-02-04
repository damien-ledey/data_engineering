import streamlit as st
import pymongo
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Exploration des données", page_icon="https://store.steampowered.com/favicon.ico", layout="wide")

# ================== Connexion à la base de données MongoDB ==================
@st.cache_resource
def get_database():
    client = pymongo.MongoClient('mongodb://mongodb:27017/')
    database = client['projet']
    collection = database['steam_games']
    return collection

collection = get_database()

