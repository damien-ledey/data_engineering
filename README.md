# Steam Scraping
Projet de scraping et de mise en place d'une interface pour explorer les données obtenues de la page de recherche de [Steam](https://store.steampowered.com/search?term=&page=1&count=100)

# Pré-requis
Avoir Docker installé et lancé

# Lancer l'application

- Se placer dans le dossier data_engineering
- Puis exécuter cette commande dans un terminal :
```bash
docker-compose up -d --build
```
- Enfin aller sur le lien suivant : **http://localhost:8501**

Il peut exister un délai entre le lancement du conteneur Docker et l'actualisation de la page. Vous pouvez donc rafraîchir la page après avoir attendu un peu.

