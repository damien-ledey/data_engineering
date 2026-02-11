import streamlit as st
import pymongo
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Steam Scraper", page_icon="https://store.steampowered.com/favicon.ico", layout="wide")

# Titre principal
col1, _, col2 = st.columns((3, 3, 1))
with col1:
    st.title("Steam Scraper")
with col2:
    st.image("https://store.akamai.steamstatic.com/public/shared/images/header/logo_steam.svg?t=962016", width=200)
st.markdown("---")

st.markdown("""
## Bienvenue dans l'application **Steam Scraper** !
Dans cette application, vous allez pouvoir explorer les données extraites du site [Steam](https://store.steampowered.com/) à l'aide de [Scrapy](https://www.scrapy.org/).
Ces données seront scrappées au démarrage de l'application, si le fichier csv n'existe pas déjà.
            
Le site possède 3 pages différentes :
            - **Interprétation des données** : une page de visualisation et d'analyse des données extraites
            - **Recherche** : une page de recherche avancée pour trouver les jeux qui vous intéressent
            - **Exemple d'utilisation** : une page qui montre comment utiliser les données extraites pour faire des requêtes et des analyses avec MongoDB
Toutes ces pages sont accessibles via la barre latérale à gauche.
            
## Credits
ZERROUG Meliana - LEDEY Damien 

[Lien du projet GitHub](https://github.com/meliana-zerroug/test_data_eng.git)
            """)

# MongoDB connexion 
@st.cache_resource
def get_database():
    client = pymongo.MongoClient('mongodb://mongodb:27017/')
    return client['projet']['steam_games']

# Récupérer toutes les données
@st.cache_data
def load_data():
    df = pd.read_csv('./steam_project/data/steam_search.csv')
    # Vérifier que la colonne price existe, sinon ajouter une valeur par défaut
    if 'price' not in df.columns:
        df['price'] = 'N/A'
    return df

st.sidebar.success("Sélectionnez une démo ci-dessus.")

data_load_state = st.text('Chargement des données...')

collection = get_database()
cur = collection.find({}, {'_id': 0})
data = pd.DataFrame(list(cur))

data_load_state.empty()

st.subheader('Données brutes extraites de Steam')
data_load_state = st.write(data.head(10))