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

st.title("Interprétation des données Steam Scraper")

st.markdown("""
            ---
            Sur cette page, nous allons explorer les données que nous avons collectées à partir de Steam. 
            Nous allons examiner les tendances générales et les catégories de jeux les plus populaires que nous pouvons tirer de notre base de données.
            L'analyse sera d'abord générale, analysant les caractéristiques, puis nous essayerons d'identifier des liens entre les caractéristiques analysées.
            
            Dans un premier temps, nous verrons 3 parties :
            - Les catégories de jeux les plus populaires, pour comprendre les tendances du marché
            - Les prix des jeux, pour compredre quelles sont les fourchettes de prix les plus courantes 
            - Les notes des jeux, pour voir comment les jeux sont notés par les joueurs
            Puis nous analyserons les liens entre ces caractéristiques.
            ---
            """)

# ================== Analyse des catégories de jeux les plus populaires ==================
st.header("Catégories de jeux les plus populaires")

cur = collection.aggregate([
    { '$match':     { 'tags': { '$type': 'string' } } },            # On vérifie que le champ tags est bien une chaîne de caractères
    { '$project':   { 'tags': { '$split': ["$tags", ","] } } },     # On divise les tags en une liste
    { '$unwind':    "$tags" },                                      # On décompose la liste pour avoir un document par tag
    { '$group':     { '_id': "$tags" , 'count': { '$sum': 1 } } },  # On groupe par tag et on compte le nombre de jeux par tag
    { '$sort':      { 'count': -1 } },                              # On trie par nombre de jeux décroissant
    { '$limit':     25 }                                            # On limite à 25 résultats
])

df = pd.DataFrame(list(cur))
st.bar_chart(data=df, x='_id', y='count')

st.markdown("""
            Nous pouvons voir que les catégories les plus populaires sont jeu solo, action et aventure. 
            Ce sont des catégories très générales qui peuvent correspondre à plusieurs type de jeux, ce sont donc logiquement les catégories les plus populaires.

            Nous retrouvons aussi la catégorie indépendant, correspondant à des jeux créés par des petits studios voir des développeurs seuls.
            Nous pouvions nous attendre à cette catégorie puisque n'importe qui peut publier un jeu sur Steam, les jeux indépendants sont donc très nombreux.

            Des catégories plus précises comme RPG, simulation ou stratégies apparaissent dans le top 10, montrant bien leur présence sur le marché du jeu vidéo. 
            """)

st.markdown("---")

# ============================ Analyse des prix des jeux ==============================
st.header("Analyse des prix des jeux")

# On récupère le nombre de jeux par fourchette de prix

cur = collection.aggregate([
    { '$addFields': {
        'price_cleaned': {
            '$cond': {
                'if': { '$eq': ["$price", "Gratuit"] }, 
                'then': 0, 

                'else': {
                    '$toDouble': {
                        '$replaceOne': {
                            'input': {
                                '$replaceOne': { 
                                    'input': "$price", 
                                    'find': "€", 
                                    'replacement': "" 
                                }
                            },
                            'find': ",", 
                            'replacement': "." 
    }}}}}}},
    { '$match':     { 'price_cleaned': { '$type': 'number' } } },                                                                       # On vérifie que le champ price_cleaned est bien un nombre
    { '$bucket':    { 'groupBy': "$price_cleaned", 'boundaries': [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 1000], 'default': "others" } },   # On regroupe les prix par fourchette de 10€
])
df = pd.DataFrame(list(cur))

df.drop(df[df['_id'] == "others"].index, inplace=True)

st.bar_chart(data=df, x='_id', y='count')

st.markdown("""
            Nous pouvons voir que la grande majorité des jeux sont gratuits ou à moins de 10€. 
            Puis le nombre de jeux diminue au fur et à mesure que le prix augmente. Nos données représentent des jeux pour des prix allant de 0€ à +100€ même s'il sont moins d'une dizaine. 

            Les jeux autours de 50-60€ sont souvent des jeux AAA, c'est-à-dire des jeux qui ont bénéficié d'un gros budget et d'un gros studio de développement.
            C'est pour cela que l'on trouve moins de jeux à ce prix.

            A contrario, les jeux à moins de 10€ sont souvent indépendants. Et aujourd'hui, il en existe tellement que pour exister sur le marché, un prix faible est obligatoire.
            """)

st.markdown("---")

# ============================ Analyse des notes des jeux ==============================
st.header("Analyse des notes des jeux")

# On récupère le nombre de jeux par fourchette de note
cur = collection.aggregate([
    { '$match':     { 'review_score': { '$type': 'number' } } },                                                           # On vérifie que le champ review_score est bien un nombre
    { '$bucket':    { 'groupBy': "$review_score", 'boundaries': [0, 20, 40, 60, 80, 90, 95, 100], 'default': "100+" } },   # On regroupe les notes par fourchette de 20%
])
df = pd.DataFrame(list(cur))

df.drop(df[df['_id'] == "100+"].index, inplace=True)

st.bar_chart(data=df, x='_id', y='count')

st.markdown("""
            Nous observons une homogénénéité, avec une gausienne, dans les notes autour de 80%. 
            Les jeux ont donc tendance à être plutôt bien notés. Des notes très faibles sont plus rares, car les éditeurs retire les jeux souvent pour ne pas se faire de mauvaise publicité.
            """)

st.markdown("---")

# ============================ Analyse des liens entre tags et notes ==============================
st.header("Analyse des liens entre les catégories et les notes")

cur = collection.aggregate([
    { '$match':     { 'tags': { '$type': 'string' } } },            # On vérifie que le champ tags est bien une chaîne de caractères
    { '$project':   { 'tags': { '$split': ["$tags", ","] }, 'review_score': { '$convert': { 'input': "$review_score", 'to': "int", 'onError': None, 'onNull': None } } } },     # On divise les tags en une liste et on conserve le score de review
    { '$unwind':    "$tags" },                                      # On décompose la liste pour avoir un document par tag
    { '$group':     { '_id': "$tags" , 'count': { '$sum': 1 }, 'average_review_score': { '$avg': "$review_score" } } },  # On groupe par tag et on compte le nombre de jeux par tag et on calcule la moyenne des notes
    { '$sort':      { 'average_review_score': -1 } }                # On trie par popularité moyenne décroissante
])

cur_list = list(cur)
df1 = pd.DataFrame(cur_list[:10])
df2 = pd.DataFrame(cur_list[-10:])

# On affiche les 10 catégories les mieux notées et les 10 catégories les moins bien notées dans deux colonnes différentes pour les comparer facilement
col1, col2 = st.columns(2)
with col1:
    st.subheader("Catégories les mieux notées")
    st.bar_chart(data=df1, x='_id', y='average_review_score')
with col2:
    st.subheader("Catégories les moins bien notées")
    st.bar_chart(data=df2, x='_id', y='average_review_score')

st.markdown("""
            Ces données nous permettent de voir quelles sont les catégories dans lesquelles les jeux recoivent les meilleures et les pires notes.
            Cela peut permettre aux développeurs de jeux de mieux cibler les catégories qu'il peuvent viser pour maximiser les chances d'avoir de bonnes notes, mais aussi celles à éviter.
            """)

st.markdown("---")

# ============================ Analyse des liens entre prix et notes ==============================
st.header("Analyse des liens entre les prix et les notes")

cur = collection.aggregate([
    { '$addFields': {
        'price_cleaned': {
            '$cond': {
                'if': { '$eq': ["$price", "Gratuit"] }, 
                'then': 0, 

                'else': {
                    '$toDouble': {
                        '$replaceOne': {
                            'input': {
                                '$replaceOne': { 
                                    'input': "$price", 
                                    'find': "€", 
                                    'replacement': "" 
                                }
                            },
                            'find': ",", 
                            'replacement': "." 
    }}}}}, 'review_score': { '$convert': { 'input': "$review_score", 'to': "int", 'onError': None, 'onNull': None } }
    }},
    { '$match':     { 'price_cleaned': { '$type': 'number' }, 'review_score': { '$type': 'number' } } },                                                                       # On vérifie que le champ price_cleaned est bien un nombre et que review_score est bien un entier
    { '$bucket':    { 'groupBy': "$price_cleaned", 'boundaries': [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 1000], 'default': "others",
                     'output': { 'average_review_score': { '$avg': "$review_score" }, 'count': { '$sum': 1 } } } },   # On regroupe les prix par fourchette de 10€
    { '$sort':      { 'average_review_score': -1 } }
])

df = pd.DataFrame(list(cur))
df.drop(df[df['_id'] == "others"].index, inplace=True)
st.bar_chart(data=df, x='_id', y='average_review_score')

st.markdown("""
            Nous voyons ques les jeux les mieux notés sont les jeux à 80-90€ et à 10-20€.
            """)