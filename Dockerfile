FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY steam_project/ ./steam_project/

COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

WORKDIR /app/steam_project

EXPOSE 8501

# Lancer l'application
CMD ["/app/start.sh"]