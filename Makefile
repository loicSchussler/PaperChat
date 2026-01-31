.PHONY: help start stop restart build logs clean rebuild status

# Variables
DOCKER_COMPOSE = docker-compose

help: ## Afficher l'aide
	@echo "PaperChat - Commandes disponibles:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""

start: ## Démarrer tous les services (DB, Backend, Frontend)
	@echo "🚀 Démarrage de PaperChat..."
	$(DOCKER_COMPOSE) up -d
	@echo ""
	@echo "✓ Services démarrés!"
	@echo "  - Frontend: http://localhost:4200"
	@echo "  - Backend API: http://localhost:8000"
	@echo "  - API Docs: http://localhost:8000/docs"
	@echo ""
	@echo "📋 Utiliser 'make logs' pour voir les logs"

stop: ## Arrêter tous les services
	@echo "⏸️  Arrêt des services..."
	$(DOCKER_COMPOSE) down
	@echo "✓ Services arrêtés"

restart: stop start ## Redémarrer tous les services

build: ## Construire les images Docker
	@echo "🔨 Construction des images Docker..."
	$(DOCKER_COMPOSE) build
	@echo "✓ Images construites"

rebuild: ## Reconstruire les images et redémarrer
	@echo "🔨 Reconstruction complète..."
	$(DOCKER_COMPOSE) down
	$(DOCKER_COMPOSE) build --no-cache
	$(DOCKER_COMPOSE) up -d
	@echo "✓ Reconstruction terminée"

logs: ## Afficher les logs de tous les services
	$(DOCKER_COMPOSE) logs -f

logs-backend: ## Afficher les logs du backend
	$(DOCKER_COMPOSE) logs -f backend

logs-frontend: ## Afficher les logs du frontend
	$(DOCKER_COMPOSE) logs -f frontend

logs-db: ## Afficher les logs de la base de données
	$(DOCKER_COMPOSE) logs -f db

status: ## Afficher le statut des services
	@echo "📊 Statut des services:"
	@$(DOCKER_COMPOSE) ps

clean: ## Nettoyer les containers et volumes
	@echo "🧹 Nettoyage..."
	$(DOCKER_COMPOSE) down -v
	@echo "✓ Nettoyage terminé"

shell-backend: ## Ouvrir un shell dans le container backend
	$(DOCKER_COMPOSE) exec backend /bin/bash

shell-frontend: ## Ouvrir un shell dans le container frontend
	$(DOCKER_COMPOSE) exec frontend /bin/sh

shell-db: ## Ouvrir un shell PostgreSQL
	$(DOCKER_COMPOSE) exec db psql -U paperchat -d paperchat_db

test: ## Lancer les tests du backend
	$(DOCKER_COMPOSE) exec backend pytest

test-cov: ## Lancer les tests avec couverture
	$(DOCKER_COMPOSE) exec backend pytest --cov=app

dev-backend: ## Développement backend local (sans Docker)
	@echo "🔧 Démarrage du backend en mode développement local..."
	@cd backend && uvicorn app.main:app --reload

dev-frontend: ## Développement frontend local (sans Docker)
	@echo "🔧 Démarrage du frontend en mode développement local..."
	@cd frontend && npm start
