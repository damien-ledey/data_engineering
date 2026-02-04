import pandas as pd
import pymongo
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Example d'utilisation", page_icon="https://store.steampowered.com/favicon.ico", layout="wide")

# ================== Connexion à la base de données MongoDB ==================
@st.cache_resource
def get_database():
    client = pymongo.MongoClient('mongodb://mongodb:27017/')
    database = client['projet']
    collection = database['steam_games']
    return collection

collection = get_database()

# ================== Vérification que les données existent ===================
#df_ks = pd.read_csv('./data/steam_search.csv')
#print(df_ks.head(5))

#collection.delete_many({})
#collection.insert_many(df_ks.to_dict('records'))

#print("Data inserted into MongoDB collection 'steam_games' in database 'projet'.")

# ============================================================================

def format_data(cur):
    # Putting the result in a dataframe for better display
    df = pd.DataFrame(list(cur))
    df = df[['thumbnail_link', 'title', 'release', 'price', 'review_score', 'review_total', 'app_id']]

    # Transforming df
    df['app_id'] = df['app_id'].apply(lambda x: f"https://store.steampowered.com/app/{x}")
    df['review_score'] = df['review_score'].apply(lambda x: f"{x}%")

    st.data_editor(
        df,
        column_config={
            "thumbnail_link": st.column_config.ImageColumn(
                "Miniature", help="Miniatures des jeux", width=200
            ),
            "title": "Titre du jeu",
            "release": "Date de sortie",
            "price": "Prix",
            "review_score": "Note",
            "review_total": "Nombre d'avis",
            "app_id": st.column_config.LinkColumn(
                "Lien Steam", help="Lien vers la page Steam du jeu",
            ),
        },    
        hide_index=True,
    )

# ============================================================================

st.title("Exemple d'utilisation de la base de données Steam Scraper")
st.markdown("""
            ---

            Les exemples suivant ont été réalisés en utilisant des requêtes MongoDB directement sur la base de données.
            Celle-ci à été formée en scrampant la page de recherche de Steam avec Scrapy et en insérant les données dans MongoDB à l'aide de DataFrames pandas. \n
            Les données scrappées représentent les 10000 jeux de la page de recherche Steam au 31/01/2025. 

            ---
            """)

# ============================================================================

st.markdown("""
            ### Exemple 1 : Afficher 5 jeux quelconques aléatoires 
            """)

# Afficher 5 jeux quelconques
cur = collection.aggregate([{'$sample': {'size': 5}}])

format_data(cur)
    
st.markdown("---")

# ============================================================================

st.markdown("""
            ### Exemple 2 : Afficher les 5 jeux avec la pire note            
            """)

# Triage des jeux par note croissante et affichage des 5 premiers (les pires)
cur = collection.find({"review_score": {"$type": "number", "$ne": float("nan")}}).sort([('review_score', pymongo.ASCENDING)]).limit(5)

format_data(cur)

st.markdown("---")

# ============================================================================

st.markdown("""
            ### Exemple 3 : Afficher les 10 catégories avec le plus de jeux
            """)

cur = collection.aggregate([
    { '$match':     { 'tags': { '$type': 'string' } } },            # On vérifie que le champ tags est bien une chaîne de caractères
    { '$project':   { 'tags': { '$split': ["$tags", ","] } } },     # On divise les tags en une liste
    { '$unwind':    "$tags" },                                      # On décompose la liste pour avoir un document par tag
    { '$group':     { '_id': "$tags" , 'count': { '$sum': 1 } } },  # On groupe par tag et on compte le nombre de jeux par tag
    { '$sort':      { 'count': -1 } },                              # On trie par nombre de jeux décroissant
    { '$limit':     10 }                                            # On limite à 10 résultats
])

df = pd.DataFrame(list(cur))
st.bar_chart(data=df, x='_id', y='count')

st.markdown("---")

# ============================================================================

def affichage_jeux_mot(mot="Sport"):

    st.markdown(f"""
                ### Exemple 4 : Afficher les jeux (maximum 10) avec '{mot}' dans le titre
                """)
    # Recherche de jeux avec le mot de la variable mot dans le titre
    cur = collection.find( { "title": { "$regex": mot} } ).limit(10)
    if len(list(cur)) == 0:
        st.write("Aucun jeu trouvé avec ce mot dans le titre.")
    else:
        cur = collection.find( { "title": { "$regex": mot, "$options": "i"} } ).limit(10)
        format_data(cur)

mot = st.text_input("Mot à rechercher dans le titre des jeux", "sport")

affichage_jeux_mot(mot)

st.markdown("---")

# ============================================================================

st.markdown("""
            ### Exemple 5 : Afficher les 5 développeurs avec le plus de jeux

            __Not implemented yet.__
            """)


