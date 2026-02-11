# Steam Scraping
Projet de scraping et de mise en place d'une interface pour explorer les données obtenues de la page de recherche de [Steam](https://store.steampowered.com/search?term=&page=1&count=100)

---

# Pré-requis
Avoir [Docker Desktop](https://www.docker.com/products/docker-desktop/) installé et lancé 

---

# Lancer l'application

- Se placer dans le dossier data_engineering
- Puis exécuter cette commande dans un terminal :
```bash
docker-compose up -d --build
```
- Enfin aller sur le lien suivant : **http://localhost:8501**

Il peut exister un délai entre le lancement du conteneur Docker et l'actualisation de la page. Vous pouvez donc rafraîchir la page après avoir attendu un peu.

---

##  Commandes utiles

### Voir les logs en temps réel

```bash
docker-compose logs -f streamlit
```

### Arrêter l'application

```bash
docker-compose down
```

### Relancer l'application

```bash
docker-compose down
docker-compose up -d --build
```

### Accéder à MongoDB directement

```bash
docker exec -it steam_mongodb mongosh
# Puis dans MongoDB shell :
use projet
db.steam_games.find().limit(5)
```


---

##  Fonctionnement

1. Docker Compose démarre MongoDB + Streamlit
2. start.sh → Scrapy scrape Steam et enregistre le résultat dans un csv → Charge automatiquement CSV et met les données dans MongoDB et ElasticSearch
3. Home.py (Streamlit) → Lit MongoDB → Affiche dans le navigateur
4. Recherche.py utilise ElasticSearch pour faire des recherche facilement et rapidement

---

##  Choix techniques

Plutôt que d'utiliser une seule base de données pour tout faire, nous avons choisis d'utiliser tout d'abord MongoDB qui nous permet de stocker les données brutes des jeux Steam. Nous avons choisi cela car la structure des données Steam est flexible et le format de MongoDB est parfait pour stocker ces objets sans avoir trop de contraintes. 

Nous avons également utilisé Elasticsearch pour notre moteur de recherche car MongoDB est un moins performant pour la rechercher textuelle complexe (fautes de frappes, pertinence etc...).

Notre interface utilisateur a été réalisée avec Streamlit, cela nous permet de développer une interface Web interactive complètement en Python, on a pas besoin d'HTML/CSS. De plus on peut utiliser pandas pour tout ce qui est affichage des tableaux de données.

On utilise également Docker qui nous permet d'avoir le même environnement de travail, ça évite de perdre du temps avec des problèmes de compatibillité. Il nous suffit de faire un 'docker-compose up' et toute la stack démarre d'un coup. Cela permet de laisser nos machines propres et ça rend le projet plus facile à récupérer et à tester pour quelqu'un d'autre. 

---

## Résolution de problèmes

### L'application ne démarre pas

```bash
# Vérifier que Docker est bien lancé
docker --version

# Vérifier les conteneurs actifs
docker ps
```

### Les données ne s'affichent pas (Total de jeux = 0)

Les données sont normalement chargées automatiquement au démarrage. Si elles ne s'affichent pas :

- Vérifier la présence d'un fichier steam_project.csv dans le dossier data.
- S'il est vide, supprimez-le. 

```bash
# Reconstruire et relancer les conteneurs
docker-compose down
docker-compose up -d --build

# Attendre 10 secondes que MongoDB se lance et que les données soient chargées
# Puis vérifier les logs
docker logs steam_app
```

### MongoDB ne se connecte pas

```bash
# Redémarrer les conteneurs
docker-compose down
docker-compose up -d --build
```

### Port 8501 déjà utilisé

```bash

# Arrêter le conteneur existant
docker-compose down

# Ou changer le port dans docker-compose.yml
ports:
  - "8502:8501"  # Utiliser le port 8502 au lieu de 8501
```

---


### Ports utilisés

- **8501** : Application Streamlit
- **27017** : MongoDB
- **9200** : ElasticSearch


---