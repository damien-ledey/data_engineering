#!/bin/bash
# Scraper les données de Steam et les enregistrer dans un fichier CSV seulement si les fichiers sont manquants
if [ -f "data/steam_search.csv" ]; then
    sleep 10
else
    scrapy crawl steam_search_spider -o data/steam_search.csv -t csv
fi
# Charger les données dans MongoDB
python steam_mongoDB.py
# Lancer l'application Streamlit
streamlit run Home.py --server.port=8501 --server.address=0.0.0.0