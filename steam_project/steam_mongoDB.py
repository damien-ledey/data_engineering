import os
import time

import pandas as pd
import pymongo
from elasticsearch import Elasticsearch, helpers

# ================== Connexion à la base de données MongoDB ==================
client = pymongo.MongoClient('mongodb')
database = client['projet']
collection = database['steam_games']

# ================== Vérification que les données existent ===================
df_ks = pd.read_csv('./data/steam_search.csv')
print(df_ks.head(5))

collection.delete_many({})
records = df_ks.to_dict('records')
collection.insert_many(records)

print("Data inserted into MongoDB collection 'steam_games' in database 'projet'.")

# ================== Indexation dans Elasticsearch ==========================
es_host = os.getenv("ES_HOST", "elasticsearch")
es_port = int(os.getenv("ES_PORT", "9200"))
es = Elasticsearch(f"http://{es_host}:{es_port}")

# Attendre qu'Elasticsearch reponde
for _ in range(30):
    try:
        if es.ping():
            break
    except Exception:
        pass
    time.sleep(1)

index_name = "steam_games"
if not es.indices.exists(index=index_name):
    es.indices.create(index=index_name)
else:
    es.indices.delete(index=index_name)
    es.indices.create(index=index_name)

actions = []
for record in records:
    source = dict(record)
    source.pop("_id", None)
    actions.append({"_index": index_name, "_id": source.get("app_id"), "_source": source})
helpers.bulk(es, actions)
print(f"Data indexed into Elasticsearch index '{index_name}'.")


# Exemple d'utilisation des requêtes MongoDB
"""
# ============================================================================

print("\n*********** Question 0 ***********\n")

# Afficher 5 jeux quelconques
cur = collection.find().limit(5)
print(f"{'Jeu':^80} ---- {'Note':^20} ---- {'Lien':^44}")
print("-" * 154)
for games in cur:
    print(f"{games['title']:<80} ---- {f"{games['review_score']}% de {games['review_total']}":^20} ---- https://store.steampowered.com/app/{games['app_id']}")

# ============================================================================

print("\n*********** Question 1 ***********\n")
print("Top 5 des jeux avec la pire note :\n")

# Triage des jeux par note croissante et affichage des 5 premiers (les pires)
cur = collection.find({"review_score": {"$type": "number", "$ne": float("nan")}}).sort([('review_score', pymongo.ASCENDING)]).limit(5)

print(f"{'Jeu':^80} ---- {'Note':^20} ---- {'Lien':^44}")
print("-" * 154)
for games in cur:
    print(f"{games['title']:<80} ---- {f"{games['review_score']}% de {games['review_total']}":^20} ---- https://store.steampowered.com/app/{games['app_id']}")

# ============================================================================

print("\n*********** Question 2 ***********\n")
print("Nombre de jeux par catégorie :\n")

cur = collection.aggregate([
    { '$match':     { 'tags': { '$type': 'string' } } },            # On vérifie que le champ tags est bien une chaîne de caractères
    { '$project':   { 'tags': { '$split': ["$tags", ","] } } },     # On divise les tags en une liste
    { '$unwind':    "$tags" },                                      # On décompose la liste pour avoir un document par tag
    { '$group':     { '_id': "$tags" , 'count': { '$sum': 1 } } },  # On groupe par tag et on compte le nombre de jeux par tag
    { '$sort':      { 'count': -1 } },                              # On trie par nombre de jeux décroissant
    { '$limit':     10 }                                            # On limite à 10 résultats
])

print(f"{'Catégorie':^30} ---- {'Nombre de jeux':^15}")
print("-" * 50)
for doc in cur:
    print(f"{doc['_id']:<30} ---- {doc['count']:^15}")

# ============================================================================

mot = "sport"
print("\n*********** Question 3 ***********\n")
print(f"5 jeux avec le mot {mot} dans le titre :\n")

# Recherche de jeux avec le mot de la variable mot dans le titre
cur = collection.find( { "title": { "$regex": mot} } ).limit(5)

print(f"{'Jeu':^80} ---- {'Lien':^44}")
print("-" * 130)
for games in cur:
    print(f"{games['title']:<80} ---- https://store.steampowered.com/app/{games['app_id']}")

# ============================================================================

print("\n*********** Question 4 ***********\n")
print("Top 5 des développeurs avec le plus de jeux :\n")

print(f"{'Développeur':^40} ---- {'Nombre de jeux':^15}")
print("-" * 60)

# Il faut d'abord ajouter les développeurs dans la base de données
print("\nPas fait\n\n")


print("\n\n")
"""