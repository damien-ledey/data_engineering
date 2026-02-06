import os
import re

import pandas as pd
import pymongo
import streamlit as st
from elasticsearch import Elasticsearch

def clean_price(price_str):
    if price_str is None:
        return 0.0
    if isinstance(price_str, (int, float)):
        return float(price_str)
    if not isinstance(price_str, str):
        return 0.0
    lower_price = price_str.lower()
    if "gratuit" in lower_price or "free" in lower_price:
        return 0.0
    match = re.findall(r"[0-9]+(?:[.,][0-9]+)?", price_str)
    if not match:
        return 0.0
    clean = match[0].replace(",", ".")
    try:
        return float(clean)
    except ValueError:
        return 0.0



st.set_page_config(page_title="Recherche", page_icon="https://store.steampowered.com/favicon.ico", layout="wide")

DEFAULT_MAX_PRICE = 60

# MongoDB connexion
@st.cache_resource
def get_database():
    client = pymongo.MongoClient('mongodb://mongodb:27017/')
    return client['projet']['steam_games']

collection = get_database()


@st.cache_data
# On définit une fonction qui filtre les catégories pour garder que les catégories les + pertinentes (sinon il y en a trop) et on nettoie 
def get_tags_list():
    WHITELIST = [ #catégories récupérées sur steam 
 
        "Action", "Aventure", "RPG", "Stratégie", "Simulation", 
        "Sport", "Course", "Casse-tête", "Combat", "Plateforme",
        "FPS", "Tir", "Moba", "Battle Royale", "Metroidvania", 
        "Roguelike", "Roguelite", "Hack 'n' Slash", "Point & Click", 
        "Horreur", "Horreur psychologique", "Survie", "Infiltration", 
        "Rythme", "Visual Novel", "Beat Them All", "Tower Defense",
        "Science-fiction", "Cyberpunk", "Fantasy", "Médiéval", 
        "Postapocalyptique", "Espace", "Zombies", "Guerre", 
        "Historique", "Western", "Monde ouvert", "Bac à sable",
        "Multijoueur", "Coop", "Coop en ligne", "MMORPG", 
        "JcJ", "JcE", "2D", "3D", "Pixel Art", "Rétro", "Anime", "VR",
        "Gestion", "Construction", "Tour par tour", "Stratégie en temps réel",
        "Jeu de cartes", "Construction de decks", "Physique"
    ]
    
    try:
        raw_tags = collection.distinct("tags")
    except Exception:
        return sorted(WHITELIST)
    
    existing_clean_tags = set()
    
    for item in raw_tags:
        if isinstance(item, list):
            for t in item:
                if isinstance(t, str):
                    clean_t = t.strip() # On enlève les espaces 
                    if clean_t in WHITELIST:
                        existing_clean_tags.add(clean_t)
                        
        elif isinstance(item, str):
            # On découpe à chaque virgule
            splitted = item.split(',')
            for t in splitted:
                clean_t = t.strip() # On enlève les espaces 
                if clean_t in WHITELIST:
                    existing_clean_tags.add(clean_t)
    
    if not existing_clean_tags:
        return sorted(WHITELIST)
        
    return sorted(list(existing_clean_tags))


@st.cache_resource
def get_elasticsearch():
    es_host = os.getenv("ES_HOST", "elasticsearch")
    es_port = os.getenv("ES_PORT", "9200")
    return Elasticsearch(f"http://{es_host}:{es_port}")

es = get_elasticsearch()

with st.sidebar:
    st.header("Filtres")
    # Filtre Prix
    st.divider()
    st.subheader("Budget")
    
  
    max_price = st.slider("Prix maximum", 0, 100, DEFAULT_MAX_PRICE, step=5, format="%d€")
    
    include_free = st.checkbox("Inclure les jeux Gratuits", value=True)    
    st.divider()
    
    # filtre catégories
    try:
        tags_list = get_tags_list()
    except Exception:
        tags_list = []
    selected_tags = st.multiselect("Catégories", tags_list)

st.title("Recherche")
query = st.text_input("Rechercher un jeu", placeholder="Ex: minecraft, sport...")

col1, col2 = st.columns([3, 1])

with col1:
    limit_val = st.slider("Nombre de résultats", 10, 200, 50)

with col2:
    show_all = st.checkbox("Voir TOUT")

if show_all:
    limit = 10000
else:
    limit = limit_val

if query or max_price != DEFAULT_MAX_PRICE or selected_tags or show_all:
    try:
        search_query = {
            "bool": {
                "must": [],
                "filter": [],
                "must_not": []
            }
        }

        # Si l'utilisateur a écrit quelque chose on gère le texte : 
        if query:
            search_query["bool"]["must"].append({
                "multi_match": {
                    "query": query,
                    "fields": ["title^3", "tags", "review_text"],
                    "fuzziness": "AUTO"
                }
            })
        else:
            # Si pas de mot clé mais des filtres alors on prend tout 
            search_query["bool"]["must"].append({"match_all": {}})

        
        # On gère les tags sélectionnés
        for tag in selected_tags:
            search_query["bool"]["filter"].append({"match": {"tags": tag}})


        # On recupere plus de resultats pour que le filtrage prix ne reduise pas trop notre affichage
        fetch_size = limit if show_all else min(limit * 5, 1000)

        response = es.search(
            index="steam_games",
            size=fetch_size,
            query=search_query,
        )
        
        hits = [hit.get("_source", {}) for hit in response.get("hits", {}).get("hits", [])]
        
        if hits:
            df = pd.DataFrame(hits)
            
            df["lien_steam"] = "https://store.steampowered.com/app/" + df["app_id"].astype(str)
            
            
            df["price_val"] = df["price"].apply(clean_price)
            
           
            if include_free:

                df = df[ (df["price_val"] <= max_price) ]
            else:
                df = df[ (df["price_val"] <= max_price) & (df["price_val"] > 0) ]

            nb_restants = len(df)
            
            if nb_restants > 0:
                # On limite l'affichage au nombre demande par l'utilisateur
                df = df.head(limit)
                st.write(f"{len(df)} résultats affichés (après filtres).")
                
                st.dataframe(
                    df,
                    column_order=["thumbnail_link", "title", "review_score", "review_total", "price", "lien_steam"],
                    hide_index=True,
                    column_config={
                        "thumbnail_link": st.column_config.ImageColumn("Image"),
                        "title": st.column_config.TextColumn("Titre", width="medium"),
                        "review_score": st.column_config.NumberColumn("Note", format="%d%%"),
                        "review_total": st.column_config.TextColumn("Nb Avis"), 
                        "price": st.column_config.TextColumn("Prix"),
                        "lien_steam": st.column_config.LinkColumn("Lien Steam", display_text="Voir la page")
                    },
                    use_container_width=True
                )
            else:
                st.warning(f"Aucun jeu trouvé en dessous de {max_price}€ avec ces critères.")
        else:
            st.info("Aucun résultat.")
            
    except Exception as exc:
        st.error(f"Elasticsearch indisponible: {exc}")
else:
    st.caption("Saisir un mot clé ou utiliser les filtres pour lancer la recherche.")