#!/bin/bash
# Attendre que MongoDB soit prêt
sleep 5
# Charger les données dans MongoDB
python steam_mongoDB.py
# Lancer l'application Streamlit
streamlit run Home.py --server.port=8501 --server.address=0.0.0.0
