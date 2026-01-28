# data_engineering
Projet de scraping et de mise en place d'une interface pour explorer les données obtenues

# Commandes pour l'exécution
cd .\steam_project\
scrapy crawl steam_search_spider -o data/steam_search.csv -t csv ### A faire seulement après avoir supprimé le fichier cible sinon la spider ajoute à la fin du document
python3 .\steam_mongoDB.py
