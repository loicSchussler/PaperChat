# PaperChat RAG

Assistant IA pour analyser, indexer et interroger des articles scientifiques en utilisant la technique RAG (Retrieval-Augmented Generation).

## 🎯 Objectif

Créer un système capable de :
- Uploader et analyser des articles scientifiques (PDF)
- Extraire automatiquement les métadonnées (titre, auteurs, année, abstract)
- Découper intelligemment les documents en chunks
- Indexer les chunks avec des embeddings dans PostgreSQL + pgvector
- Répondre à des questions en langage naturel avec citations des sources

## 🏗️ Architecture

- **Backend**: FastAPI (Python 3.11+)
- **Base de données**: PostgreSQL avec extension pgvector
- **Frontend**: Angular 18 avec Angular Material
- **LLM**: Mammouth AI (API compatible OpenAI - GPT-4o-mini pour génération, text-embedding-3-small pour embeddings)
- **RAG**: LangChain pour le chunking et le pipeline

## 📋 Prérequis

- Docker & Docker Compose
- Node.js 18+ et npm (pour le frontend)
- Python 3.11+ (pour développement local)
- Clé API Mammouth AI (déjà configurée)

## 🚀 Installation et Démarrage

### 1. Cloner et configurer

```bash
cd PaperChat
```

### 2. Configurer les variables d'environnement

Copier le fichier `.env.example` vers `.env` :

```bash
cp .env.example .env
```

La clé API Mammouth AI est déjà configurée dans `.env.example` :

```
OPENAI_API_KEY=SECRET_REMOVED
OPENAI_API_BASE=https://api.mammouth.ai/v1
```

**Note**: Mammouth AI utilise une API compatible OpenAI, donc le code utilise la bibliothèque `openai` avec un `base_url` personnalisé.

### 3. Démarrer avec Docker Compose

```bash
docker-compose up -d
```

Cela va démarrer :
- PostgreSQL avec pgvector sur le port 5432
- Backend FastAPI sur le port 8000

### 4. Créer les tables de la base de données

```bash
cd backend
python create_db.py
```

### 5. Démarrer le frontend Angular

Dans un nouveau terminal :

```bash
cd frontend
npm install
npm start
```

Le frontend sera accessible sur [http://localhost:4200](http://localhost:4200)

## 🧪 Développement Local (sans Docker)

### Backend

1. Installer les dépendances Python :

```bash
cd backend
pip install -r requirements.txt
```

2. S'assurer que PostgreSQL avec pgvector est lancé (via Docker ou local):

```bash
docker-compose up -d db
```

3. Créer les tables :

```bash
python create_db.py
```

4. Lancer le serveur FastAPI :

```bash
uvicorn app.main:app --reload
```

API accessible sur [http://localhost:8000](http://localhost:8000)
Documentation interactive : [http://localhost:8000/docs](http://localhost:8000/docs)

### Frontend

```bash
cd frontend
npm install
npm start
```

## 📁 Structure du Projet

```
PaperChat/
├── backend/
│   ├── app/
│   │   ├── api/           # Endpoints REST
│   │   ├── services/      # Logique métier (PDF, RAG, etc.)
│   │   ├── models.py      # Modèles SQLAlchemy
│   │   ├── schemas.py     # Schémas Pydantic
│   │   ├── database.py    # Configuration DB
│   │   └── main.py        # Application FastAPI
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── pages/     # Pages (Upload, Library, Chat, Dashboard)
│   │   │   └── services/  # Services API
│   │   └── environments/
│   └── package.json
├── docker-compose.yml
└── README.md
```

## 🔧 À Implémenter

Le boilerplate est en place, voici les fonctionnalités principales à développer :

### Backend (dans `backend/app/services/`)

1. **pdf_extractor.py** : Extraction de texte avec pypdf
2. **metadata_extractor.py** : Extraction de métadonnées via OpenAI
3. **chunker.py** : Découpage intelligent avec LangChain
4. **embeddings.py** : Génération d'embeddings OpenAI
5. **vector_store.py** : Recherche vectorielle avec pgvector
6. **rag.py** : Pipeline RAG complet

### Frontend

Les composants sont prêts mais utilisent des données mockées. Décommenter les appels API dans :
- `upload.component.ts`
- `library.component.ts`
- `chat.component.ts`
- `dashboard.component.ts`

## 🧪 Tests

```bash
cd backend
pytest
```

## 📊 API Endpoints

- `POST /api/papers/upload` - Upload un PDF
- `GET /api/papers` - Liste des articles
- `GET /api/papers/{id}` - Détails d'un article
- `DELETE /api/papers/{id}` - Supprimer un article
- `POST /api/chat` - Poser une question RAG
- `GET /api/monitoring/stats` - Statistiques d'utilisation

Documentation complète : [http://localhost:8000/docs](http://localhost:8000/docs)

## 🎨 Interface Utilisateur

- **/upload** : Upload et indexation de PDFs
- **/library** : Liste et gestion des articles
- **/chat** : Interface de questions/réponses RAG
- **/dashboard** : Monitoring (coûts, performances)

## 📝 Base de Données

### Tables

- **papers** : Articles scientifiques (métadonnées)
- **chunks** : Segments de texte avec embeddings (vecteurs 1536D)
- **query_logs** : Historique des requêtes et coûts

### Extension pgvector

L'extension pgvector est activée pour permettre la recherche de similarité vectorielle.

## 💡 Conseils de Développement

1. Commencer par implémenter l'upload PDF et l'extraction de texte
2. Ajouter l'extraction de métadonnées via OpenAI
3. Implémenter le chunking avec LangChain
4. Générer et stocker les embeddings
5. Développer la recherche vectorielle
6. Finaliser le pipeline RAG complet

## 📚 Ressources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [pgvector](https://github.com/pgvector/pgvector)
- [LangChain](https://python.langchain.com/)
- [Mammouth AI](https://mammouth.ai) - API compatible OpenAI
- [OpenAI API Documentation](https://platform.openai.com/docs) - Compatible avec Mammouth AI
- [Angular Material](https://material.angular.io/)

## 📄 Licence

Projet portfolio / Proof of Concept
