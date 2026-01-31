# PaperChat - Script de gestion PowerShell
# Utilisation: .\start.ps1 <commande>
# Exemple: .\start.ps1 start

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

function Show-Help {
    Write-Host "PaperChat - Commandes disponibles:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  start           " -NoNewline -ForegroundColor Green
    Write-Host "Demarrer tous les services (DB, Backend, Frontend)"
    Write-Host "  stop            " -NoNewline -ForegroundColor Yellow
    Write-Host "Arreter tous les services"
    Write-Host "  restart         " -NoNewline -ForegroundColor Cyan
    Write-Host "Redemarrer tous les services"
    Write-Host "  build           " -NoNewline -ForegroundColor Magenta
    Write-Host "Construire les images Docker"
    Write-Host "  rebuild         " -NoNewline -ForegroundColor Magenta
    Write-Host "Reconstruire les images et redemarrer"
    Write-Host "  logs            " -NoNewline -ForegroundColor Blue
    Write-Host "Afficher les logs de tous les services"
    Write-Host "  logs-backend    " -NoNewline -ForegroundColor Blue
    Write-Host "Afficher les logs du backend"
    Write-Host "  logs-frontend   " -NoNewline -ForegroundColor Blue
    Write-Host "Afficher les logs du frontend"
    Write-Host "  logs-db         " -NoNewline -ForegroundColor Blue
    Write-Host "Afficher les logs de la base de donnees"
    Write-Host "  status          " -NoNewline -ForegroundColor Cyan
    Write-Host "Afficher le statut des services"
    Write-Host "  clean           " -NoNewline -ForegroundColor Red
    Write-Host "Nettoyer les containers et volumes"
    Write-Host "  test            " -NoNewline -ForegroundColor Green
    Write-Host "Lancer les tests du backend"
    Write-Host "  test-cov        " -NoNewline -ForegroundColor Green
    Write-Host "Lancer les tests avec couverture"
    Write-Host "  shell-backend   " -NoNewline -ForegroundColor Gray
    Write-Host "Ouvrir un shell dans le container backend"
    Write-Host "  shell-frontend  " -NoNewline -ForegroundColor Gray
    Write-Host "Ouvrir un shell dans le container frontend"
    Write-Host "  shell-db        " -NoNewline -ForegroundColor Gray
    Write-Host "Ouvrir un shell PostgreSQL"
    Write-Host "  dev-backend     " -NoNewline -ForegroundColor Yellow
    Write-Host "Demarrage backend en mode developpement local"
    Write-Host "  dev-frontend    " -NoNewline -ForegroundColor Yellow
    Write-Host "Demarrage frontend en mode developpement local"
    Write-Host ""
}

function Start-Services {
    Write-Host "[*] Demarrage de PaperChat..." -ForegroundColor Green
    docker-compose up -d
    Write-Host ""
    Write-Host "[OK] Services demarres!" -ForegroundColor Green
    Write-Host "  - Frontend: http://localhost:4200" -ForegroundColor Cyan
    Write-Host "  - Backend API: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "  - API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "[INFO] Utiliser '.\start.ps1 logs' pour voir les logs" -ForegroundColor Yellow
}

function Stop-Services {
    Write-Host "[*] Arret des services..." -ForegroundColor Yellow
    docker-compose down
    Write-Host "[OK] Services arretes" -ForegroundColor Green
}

function Restart-Services {
    Stop-Services
    Start-Services
}

function Build-Images {
    Write-Host "[*] Construction des images Docker..." -ForegroundColor Magenta
    docker-compose build
    Write-Host "[OK] Images construites" -ForegroundColor Green
}

function Rebuild-All {
    Write-Host "[*] Reconstruction complete..." -ForegroundColor Magenta
    docker-compose down
    docker-compose build --no-cache
    docker-compose up -d
    Write-Host "[OK] Reconstruction terminee" -ForegroundColor Green
}

function Show-Logs {
    docker-compose logs -f
}

function Show-LogsBackend {
    docker-compose logs -f backend
}

function Show-LogsFrontend {
    docker-compose logs -f frontend
}

function Show-LogsDb {
    docker-compose logs -f db
}

function Show-Status {
    Write-Host "[INFO] Statut des services:" -ForegroundColor Cyan
    docker-compose ps
}

function Clean-All {
    Write-Host "[*] Nettoyage..." -ForegroundColor Red
    docker-compose down -v
    Write-Host "[OK] Nettoyage termine" -ForegroundColor Green
}

function Run-Tests {
    docker-compose exec backend pytest
}

function Run-TestsCov {
    docker-compose exec backend pytest --cov=app
}

function Shell-Backend {
    docker-compose exec backend /bin/bash
}

function Shell-Frontend {
    docker-compose exec frontend /bin/sh
}

function Shell-Db {
    docker-compose exec db psql -U paperchat -d paperchat_db
}

function Dev-Backend {
    Write-Host "[*] Demarrage du backend en mode developpement local..." -ForegroundColor Yellow
    Set-Location backend
    uvicorn app.main:app --reload
}

function Dev-Frontend {
    Write-Host "[*] Demarrage du frontend en mode developpement local..." -ForegroundColor Yellow
    Set-Location frontend
    npm start
}

# Router vers la commande appropriee
switch ($Command.ToLower()) {
    "start"          { Start-Services }
    "stop"           { Stop-Services }
    "restart"        { Restart-Services }
    "build"          { Build-Images }
    "rebuild"        { Rebuild-All }
    "logs"           { Show-Logs }
    "logs-backend"   { Show-LogsBackend }
    "logs-frontend"  { Show-LogsFrontend }
    "logs-db"        { Show-LogsDb }
    "status"         { Show-Status }
    "clean"          { Clean-All }
    "test"           { Run-Tests }
    "test-cov"       { Run-TestsCov }
    "shell-backend"  { Shell-Backend }
    "shell-frontend" { Shell-Frontend }
    "shell-db"       { Shell-Db }
    "dev-backend"    { Dev-Backend }
    "dev-frontend"   { Dev-Frontend }
    "help"           { Show-Help }
    default {
        Write-Host "Commande inconnue: $Command" -ForegroundColor Red
        Write-Host ""
        Show-Help
    }
}
