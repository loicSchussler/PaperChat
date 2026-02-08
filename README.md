# PaperChat RAG

Assistant IA pour analyser, indexer et interroger des articles scientifiques avec système de conversations persistantes.

## Fonctionnalités

- Upload et analyse de PDFs scientifiques
- Extraction automatique de métadonnées (titre, auteurs, année, abstract)
- Recherche vectorielle avec pgvector
- Chat RAG avec mémoire conversationnelle
- Visualiseur PDF intégré
- Dashboard de monitoring

## Stack Technique

- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: Angular 18 + Angular Material
- **Base de données**: PostgreSQL 15 avec pgvector
- **LLM**: Mammouth AI (API compatible OpenAI)

## Images
<img width="500" height="500" alt="image" src="https://github.com/user-attachments/assets/60b6a072-7979-435b-bae6-59d5743fec68" />


## Prérequis

- Docker & Docker Compose
- Clé API Mammouth AI ([obtenir ici](https://mammouth.ai))

## Installation et Démarrage

### 1. Configuration

Copier `.env.example` vers `.env` et ajouter votre clé API:

```bash
cp .env.example .env
# Éditer .env et ajouter votre OPENAI_API_KEY
```

### 2. Démarrage

**Linux/Mac**:
```bash
make start
```

**Windows**:
```powershell
.\start.ps1 start
```

C'est tout! Les services seront accessibles sur:
- Frontend: http://localhost:4200
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Commandes Utiles

**Linux/Mac**: `make <commande>`
**Windows**: `.\start.ps1 <commande>`

| Commande | Description |
|----------|-------------|
| `start` | Démarrer tous les services |
| `stop` | Arrêter tous les services |
| `logs` | Voir les logs en temps réel |
| `status` | Voir le statut des services |
| `test` | Lancer les tests |
| `help` | Afficher toutes les commandes |

## Structure du Projet

```
PaperChat/
├── backend/          # API FastAPI + services RAG
├── frontend/         # Application Angular
├── docker-compose.yml
├── Makefile          # Commandes Linux/Mac
└── start.ps1         # Commandes Windows
```

## API Endpoints Principaux

- `POST /api/papers/upload` - Upload et indexation d'un PDF
- `GET /api/papers` - Liste des articles
- `POST /api/chat` - Chat RAG avec contexte
- `GET /api/conversations` - Historique des conversations
- `GET /api/monitoring/stats` - Statistiques d'utilisation

Documentation complète: http://localhost:8000/docs

## Développement Local (sans Docker)

```bash
# Backend
docker-compose up -d db
cd backend && python init_db.py
uvicorn app.main:app --reload

# Frontend
cd frontend && npm install && npm start
```

## Tests

```bash
make test              # Linux/Mac
.\start.ps1 test       # Windows
```

## Licence

Projet portfolio / Proof of Concept
