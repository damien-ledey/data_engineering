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
    price_filter = st.radio("Prix", ["Tous", "Gratuit", "Payant"])
    
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

if query or price_filter != "Tous" or selected_tags:
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

        
        if price_filter == "Gratuit":
            search_query["bool"]["filter"].append({"term": {"price.keyword": "Gratuit"}})
        elif price_filter == "Payant":
            search_query["bool"]["must_not"].append({"term": {"price.keyword": "Gratuit"}})

        # On gère les tags sélectionnés
        for tag in selected_tags:
            search_query["bool"]["filter"].append({"match": {"tags": tag}})


        response = es.search(
            index="steam_games",
            size=limit,
            query=search_query, 
        )
        
        hits = [hit.get("_source", {}) for hit in response.get("hits", {}).get("hits", [])]
        
        if hits:
            df = pd.DataFrame(hits)
            
            df["lien_steam"] = "https://store.steampowered.com/app/" + df["app_id"].astype(str)

            st.write(f"{len(hits)} résultats trouvés.")
            
           
            st.dataframe(
                df,
                
                column_order=["thumbnail_link", "title", "review_score", "review_total", "price", "lien_steam"],
                hide_index=True,
                
                column_config={
                    "thumbnail_link": st.column_config.ImageColumn("Image"),
                    
                    "title": st.column_config.TextColumn("Titre", width="medium"),
                    
                    "review_score": st.column_config.NumberColumn(
                        "Note",
                        format="%d%%",  
                        help="Pourcentage d'évaluations positives"
                    ),
                    
                    "review_total": st.column_config.TextColumn("Nb Avis"), 
                    
                    "price": st.column_config.TextColumn("Prix"),
                    
                    # lien plus propre qu'url 
                    "lien_steam": st.column_config.LinkColumn(
                        "Lien Steam", 
                        display_text=" Voir la page" 
                    )
                },
                use_container_width=True,
            )
        else:
            st.info("Aucun résultat.")
            
    except Exception as exc:
        st.error(f"Elasticsearch indisponible: {exc}")
else:
    st.caption("Saisir un mot clé ou utiliser les filtres pour lancer la recherche.")