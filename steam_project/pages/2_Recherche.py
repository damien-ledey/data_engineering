import streamlit as st
import pymongo
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Recherche", page_icon="https://store.steampowered.com/favicon.ico", layout="wide")

# MongoDB connexion 
@st.cache_resource
def get_database():
    client = pymongo.MongoClient('mongodb://mongodb:27017/')
    return client['projet']['steam_games']

collection = get_database()


# A faire avec Elasticsearch plus tard