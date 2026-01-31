# PaperChat RAG

Assistant IA pour analyser, indexer et interroger des articles scientifiques en utilisant la technique RAG (Retrieval-Augmented Generation) avec système de conversations persistantes.

## 🎯 Fonctionnalités

### ✅ Implémenté

- **Upload et analyse de PDFs**: Extraction automatique du texte et des métadonnées
- **Extraction de métadonnées**: Titre, auteurs, année, abstract et mots-clés via LLM
- **Chunking intelligent**: Découpage sémantique avec LangChain (RecursiveCharacterTextSplitter)
- **Embeddings**: Vectorisation avec text-embedding-3-small (OpenAI/Mammouth AI)
- **Recherche vectorielle**: Similarité cosinus avec pgvector
- **Pipeline RAG complet**: Génération de réponses contextuelles avec citations des sources
- **Déduplication des sources**: Regroupement intelligent des chunks par article
- **Système de conversations**:
  - Historique persistant des messages
  - Mémoire contextuelle (10 derniers messages)
  - Interface type messenger avec sidebar
  - Gestion complète (création, lecture, suppression)
- **Monitoring**: Dashboard avec statistiques d'utilisation et coûts
- **Visualiseur PDF**: Intégré dans la bibliothèque

## 🏗️ Architecture

- **Backend**: FastAPI (Python 3.11+)
- **Base de données**: PostgreSQL 15 avec extension pgvector
- **Frontend**: Angular 18 avec Angular Material
- **LLM**: Mammouth AI (API compatible OpenAI)
  - GPT-4o-mini pour génération de texte
  - text-embedding-3-small pour embeddings
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

Ensuite, éditer `.env` et ajouter votre clé API Mammouth AI :

```
OPENAI_API_KEY=votre-clé-api-mammouth
OPENAI_API_BASE=https://api.mammouth.ai/v1
OPENAI_CHAT_MODEL=gpt-4.1-nano
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

**Note**:
- Obtenez votre clé API sur [mammouth.ai](https://mammouth.ai)
- Mammouth AI utilise une API compatible OpenAI, donc le code utilise la bibliothèque `openai` avec un `base_url` personnalisé

### 3. Démarrer avec Docker Compose

```bash
docker-compose up -d
```

Cela va démarrer :
- PostgreSQL 15 avec pgvector sur le port 5432
- Backend FastAPI sur le port 8000

### 4. Créer les tables de la base de données

```bash
# Tables principales (papers, chunks, query_logs)
cd backend
python create_db.py

# Tables de conversations (conversations, messages)
docker exec paperchat_backend python run_migration.py
```

**Note**: Le script `run_migration.py` crée les tables `conversations` et `messages` nécessaires pour le système de conversations.

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
docker exec paperchat_backend python run_migration.py
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
│   │   ├── api/              # Endpoints REST
│   │   │   ├── papers.py     # Gestion des articles
│   │   │   ├── chat.py       # Chat RAG
│   │   │   ├── conversations.py  # Gestion des conversations
│   │   │   └── monitoring.py # Statistiques
│   │   ├── services/         # Logique métier
│   │   │   ├── pdf_extractor.py     # Extraction texte PDF
│   │   │   ├── metadata_extractor.py # Extraction métadonnées
│   │   │   ├── chunker.py           # Découpage intelligent
│   │   │   ├── embeddings.py        # Génération embeddings
│   │   │   ├── vector_store.py      # Recherche vectorielle
│   │   │   └── rag.py              # Pipeline RAG complet
│   │   ├── models.py         # Modèles SQLAlchemy
│   │   ├── schemas.py        # Schémas Pydantic
│   │   ├── database.py       # Configuration DB
│   │   └── main.py          # Application FastAPI
│   ├── migrations/           # Scripts de migration SQL
│   ├── tests/               # Tests unitaires
│   ├── requirements.txt
│   ├── run_migration.py     # Script de migration
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── pages/        # Pages Angular
│   │   │   │   ├── upload/   # Upload PDFs
│   │   │   │   ├── library/  # Bibliothèque
│   │   │   │   ├── chat/     # Chat RAG
│   │   │   │   └── dashboard/ # Monitoring
│   │   │   ├── services/     # Services API
│   │   │   └── components/   # Composants réutilisables
│   │   └── environments/
│   └── package.json
├── docker-compose.yml
└── README.md
```

## 📊 API Endpoints

### Papers
- `POST /api/papers/upload` - Upload et indexation d'un PDF
- `GET /api/papers` - Liste des articles (avec recherche et filtres)
- `GET /api/papers/{id}` - Détails d'un article
- `DELETE /api/papers/{id}` - Supprimer un article

### Chat RAG
- `POST /api/chat` - Poser une question avec contexte conversationnel
  - Supporte `conversation_id` pour continuer une conversation
  - Créé automatiquement une nouvelle conversation si non fourni

### Conversations
- `POST /api/conversations` - Créer une nouvelle conversation
- `GET /api/conversations` - Liste des conversations (avec pagination)
- `GET /api/conversations/{id}` - Détails d'une conversation avec messages
- `DELETE /api/conversations/{id}` - Supprimer une conversation
- `PATCH /api/conversations/{id}/title` - Modifier le titre

### Monitoring
- `GET /api/monitoring/stats` - Statistiques d'utilisation (coûts, performances)

Documentation complète : [http://localhost:8000/docs](http://localhost:8000/docs)

## 🎨 Interface Utilisateur

### Pages

- **/upload** : Upload et indexation de PDFs avec barre de progression
- **/library** : Bibliothèque d'articles avec recherche, filtres et visualiseur PDF intégré
- **/chat** : Interface de conversations type messenger
  - Sidebar avec liste des conversations
  - Historique des messages persistant
  - Bulles de chat (utilisateur / assistant)
  - Affichage des sources avec pertinence
  - Métadonnées (temps de réponse, coût)
  - Responsive mobile avec sidebar toggleable
- **/dashboard** : Monitoring en temps réel
  - Nombre d'articles et chunks
  - Statistiques de requêtes
  - Coûts totaux et moyens
  - Temps de réponse moyen

## 📝 Base de Données

### Tables

#### papers
Articles scientifiques avec métadonnées extraites

| Colonne | Type | Description |
|---------|------|-------------|
| id | INTEGER | Clé primaire |
| title | VARCHAR | Titre de l'article |
| authors | TEXT[] | Liste des auteurs |
| year | INTEGER | Année de publication |
| abstract | TEXT | Résumé |
| keywords | TEXT[] | Mots-clés |
| nb_chunks | INTEGER | Nombre de chunks |
| created_at | TIMESTAMP | Date d'ajout |

#### chunks
Segments de texte avec embeddings vectoriels (1536D)

| Colonne | Type | Description |
|---------|------|-------------|
| id | INTEGER | Clé primaire |
| paper_id | INTEGER | Référence à papers |
| content | TEXT | Contenu du chunk |
| section_name | VARCHAR | Nom de la section |
| embedding | VECTOR(1536) | Vecteur d'embedding |
| created_at | TIMESTAMP | Date de création |

#### conversations
Sessions de conversations

| Colonne | Type | Description |
|---------|------|-------------|
| id | INTEGER | Clé primaire |
| title | VARCHAR | Titre de la conversation |
| created_at | TIMESTAMP | Date de création |
| updated_at | TIMESTAMP | Dernière mise à jour |

#### messages
Messages individuels dans les conversations

| Colonne | Type | Description |
|---------|------|-------------|
| id | INTEGER | Clé primaire |
| conversation_id | INTEGER | Référence à conversations |
| role | VARCHAR | 'user' ou 'assistant' |
| content | TEXT | Contenu du message |
| sources | TEXT | JSON des sources (pour assistant) |
| cost_usd | FLOAT | Coût de la requête |
| response_time_ms | INTEGER | Temps de réponse |
| created_at | TIMESTAMP | Date de création |

#### query_logs
Historique des requêtes et métriques

| Colonne | Type | Description |
|---------|------|-------------|
| id | INTEGER | Clé primaire |
| question | TEXT | Question posée |
| answer | TEXT | Réponse générée |
| nb_sources | INTEGER | Nombre de sources |
| prompt_tokens | INTEGER | Tokens du prompt |
| completion_tokens | INTEGER | Tokens de complétion |
| cost_usd | FLOAT | Coût total |
| response_time_ms | INTEGER | Temps de réponse |
| created_at | TIMESTAMP | Date de la requête |

### Extension pgvector

L'extension pgvector permet la recherche de similarité vectorielle avec l'opérateur de distance cosinus pour les embeddings 1536D.

## 🧪 Tests

Le projet inclut des tests unitaires complets :

```bash
cd backend
pytest

# Avec couverture
pytest --cov=app

# Tests spécifiques
pytest tests/test_vector_store.py
pytest tests/test_rag.py
```

**Couverture actuelle**: 45 tests (vector_store + RAG + déduplication)

## 🔧 Pipeline RAG

### Étapes du Pipeline

1. **Extraction** : Lecture du PDF et extraction du texte brut
2. **Métadonnées** : Extraction via LLM (titre, auteurs, année, abstract, keywords)
3. **Chunking** : Découpage sémantique avec LangChain (1000 caractères, overlap 200)
4. **Embeddings** : Vectorisation des chunks (text-embedding-3-small, 1536D)
5. **Indexation** : Stockage dans PostgreSQL avec pgvector
6. **Recherche** : Similarité cosinus pour trouver les chunks pertinents (top-k)
7. **Génération** : LLM génère la réponse avec contexte + historique conversation
8. **Déduplication** : Regroupement des chunks par article source

### Fonctionnalités Avancées

- **Mémoire contextuelle** : Les 10 derniers messages sont inclus dans le contexte LLM
- **Déduplication intelligente** : Les chunks d'un même article sont fusionnés
- **Citations précises** : Chaque source inclut le titre, l'année, la section et le score de pertinence
- **Coûts optimisés** : Calcul précis des tokens et coûts Mammouth AI

## 💡 Améliorations Futures

- [ ] Support de formats additionnels (EPUB, DOCX)
- [ ] Recherche hybride (dense + sparse)
- [ ] Fine-tuning des embeddings
- [ ] Export de conversations
- [ ] Annotations et highlights
- [ ] Partage de conversations
- [ ] Multi-utilisateurs avec authentification
- [ ] Amélioration de la génération de titres de conversations
- [ ] Support du streaming pour les réponses longues

## 📚 Ressources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [pgvector](https://github.com/pgvector/pgvector)
- [LangChain](https://python.langchain.com/)
- [Mammouth AI](https://mammouth.ai) - API compatible OpenAI
- [OpenAI API Documentation](https://platform.openai.com/docs) - Compatible avec Mammouth AI
- [Angular Material](https://material.angular.io/)

## 📄 Licence

Projet portfolio / Proof of Concept

---

**Développé avec** ❤️ **et Claude Code**
