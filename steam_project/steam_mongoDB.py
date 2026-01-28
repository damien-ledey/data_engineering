import pandas as pd
import pymongo

client = pymongo.MongoClient()
database = client['projet']
collection = database['steam_games']

df_ks = pd.read_csv('./data/steam_search.csv')
print(df_ks.head(5))

#collection.delete_many({})
#collection.insert_many(df_ks.to_dict('records'))

print("Data inserted into MongoDB collection 'steam_games' in database 'projet'.")

# ============================================================================

print("\n*********** Question 0 ***********\n")
cur = collection.find().limit(5)
print(f"{'Jeu':^80} ---- {'Note':^20} ---- {'Lien':^44}")
print("-" * 154)
for games in cur:
    print(f"{games['title']:<80} ---- {f"{games['review_score']}% de {games['review_total']}":^20} ---- https://store.steampowered.com/app/{games['app_id']}")

# ============================================================================

print("\n*********** Question 1 ***********\n")
print("Top 5 des jeux avec la pire note :\n")

cur = collection.find({"review_score": {"$type": "number", "$ne": float("nan")}}).sort([('review_score', pymongo.ASCENDING)]).limit(5)

print(f"{'Jeu':^80} ---- {'Note':^20} ---- {'Lien':^44}")
print("-" * 154)
for games in cur:
    print(f"{games['title']:<80} ---- {f"{games['review_score']}% de {games['review_total']}":^20} ---- https://store.steampowered.com/app/{games['app_id']}")

# ============================================================================

print("\n*********** Question 2 ***********\n")
print("Nombre de jeux par catégorie :\n")

cur = collection.aggregate([
    { '$match':     { 'tags': { '$type': 'string' } } },
    { '$project':   { 'tags': { '$split': ["$tags", ","] } } },
    { '$unwind':    "$tags" },
    { '$group':     { '_id': "$tags" , 'count': { '$sum': 1 } } },
    { '$sort':      { 'count': -1 } },
    { '$limit':     10 }
])

print(f"{'Catégorie':^30} ---- {'Nombre de jeux':^15}")
print("-" * 50)
for doc in cur:
    print(f"{doc['_id']:<30} ---- {doc['count']:^15}")

# ============================================================================

mot = "sport"
print("\n*********** Question 3 ***********\n")
print(f"5 jeux avec le mot {mot} dans le titre :\n")

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
print("\nPas fait\n\n")


print("\n\n")