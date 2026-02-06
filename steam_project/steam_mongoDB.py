import os
import time

import pandas as pd
import pymongo
from elasticsearch import Elasticsearch, helpers

# ================== Connexion à la base de données MongoDB ==================
client = pymongo.MongoClient('mongodb://mongodb:27017/')
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
for i in range(30):
    print(f"Waiting for {es} to be available... (attempt {i+1}/30)")
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
