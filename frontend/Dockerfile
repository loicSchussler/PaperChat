# Dockerfile pour le frontend Angular (développement)
FROM node:18-alpine

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendances
COPY package*.json ./

# Installer les dépendances
RUN npm install

# Copier le reste des fichiers
COPY . .

# Exposer le port 4200
EXPOSE 4200

# Lancer le serveur de développement
CMD ["npm", "start", "--", "--host", "0.0.0.0", "--poll"]
