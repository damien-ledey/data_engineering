import os

import pandas as pd
import pymongo
import streamlit as st
from elasticsearch import Elasticsearch

st.set_page_config(page_title="Recherche", page_icon="https://store.steampowered.com/favicon.ico", layout="wide")

# MongoDB connexion
@st.cache_resource
def get_database():
    client = pymongo.MongoClient('mongodb://mongodb:27017/')
    return client['projet']['steam_games']

collection = get_database()

@st.cache_resource
def get_elasticsearch():
    es_host = os.getenv("ES_HOST", "elasticsearch")
    es_port = os.getenv("ES_PORT", "9200")
    return Elasticsearch(f"http://{es_host}:{es_port}")

es = get_elasticsearch()

st.title("Recherche")
query = st.text_input("Rechercher un jeu", placeholder="Ex: roguelike, sport, Hades")
limit = st.slider("Nombre de resultats", min_value=5, max_value=50, value=10, step=5)

if query:
    try:
        response = es.search(
            index="steam_games",
            size=limit,
            query={
                "multi_match": {
                    "query": query,
                    "fields": ["title^3", "tags", "review_text"],
                    "fuzziness": "AUTO"
                }
            },
        )
        hits = [hit.get("_source", {}) for hit in response.get("hits", {}).get("hits", [])]
        if hits:
            df = pd.DataFrame(hits)
            st.dataframe(df)
        else:
            st.info("Aucun resultat.")
    except Exception as exc:
        st.error(f"Elasticsearch indisponible: {exc}")
else:
    st.caption("Saisis un mot cle pour lancer la recherche.")