@echo off
setlocal enabledelayedexpansion

echo ========================================
echo    FinData IA-M.K - Démarrage
echo ========================================
echo.

REM Vérifier si Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installé ou n'est pas dans le PATH !
    echo Veuillez installer Python 3.8+ depuis https://python.org
    pause
    exit /b 1
)

REM Vérifier si Node.js est installé
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js n'est pas installé ou n'est pas dans le PATH !
    echo Veuillez installer Node.js 16+ depuis https://nodejs.org
    pause
    exit /b 1
)

REM Vérifier si l'environnement virtuel existe
if not exist "env\Scripts\activate.bat" (
    echo 🔧 Création de l'environnement virtuel...
    python -m venv env
    if errorlevel 1 (
        echo ❌ Erreur lors de la création de l'environnement virtuel !
        pause
        exit /b 1
    )
)

REM Activer l'environnement virtuel
echo 🔧 Activation de l'environnement virtuel...
call env\Scripts\activate.bat

REM Vérifier si l'activation a réussi
if errorlevel 1 (
    echo ❌ Erreur lors de l'activation de l'environnement virtuel !
    pause
    exit /b 1
)

echo ✅ Environnement virtuel activé

REM Vérifier si les dépendances backend sont installées
if not exist "backend\requirements.txt" (
    echo ❌ Fichier requirements.txt manquant !
    pause
    exit /b 1
)

echo 📦 Installation/Vérification des dépendances backend...
cd backend
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Erreur lors de l'installation des dépendances backend !
    cd ..
    pause
    exit /b 1
)
cd ..

REM Vérifier si les dépendances frontend sont installées
if not exist "frontend-react\node_modules" (
    echo 📦 Installation des dépendances frontend...
    cd frontend-react
    npm install
    if errorlevel 1 (
        echo ❌ Erreur lors de l'installation des dépendances frontend !
        cd ..
        pause
        exit /b 1
    )
    cd ..
)

REM Vérifier si le fichier .env existe
if not exist ".env" (
    echo ⚠️  Fichier .env non trouvé !
    echo 📝 Création d'un fichier .env avec les valeurs par défaut...
    copy env.example .env >nul 2>&1
    if errorlevel 1 (
        echo ❌ Impossible de créer le fichier .env !
        echo Veuillez créer manuellement un fichier .env basé sur env.example
        pause
        exit /b 1
    )
    echo ✅ Fichier .env créé avec les valeurs par défaut
    echo ⚠️  N'oubliez pas de configurer vos API keys !
)

echo.
echo 🚀 Démarrage de l'application...
echo.

REM Démarrer le backend dans une nouvelle fenêtre avec l'environnement activé
echo 📡 Démarrage du backend Flask...
start "Backend Flask" cmd /k "cd /d %CD% && env\Scripts\activate.bat && cd backend && python app.py"

REM Attendre un peu pour que le backend démarre
echo ⏳ Attente du démarrage du backend...
timeout /t 5 /nobreak > nul

REM Vérifier si le backend répond
echo 🔍 Vérification du backend...
curl -s http://localhost:8080/api/health >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Le backend ne répond pas encore, mais on continue...
) else (
    echo ✅ Backend opérationnel
)

REM Démarrer le frontend dans une nouvelle fenêtre
echo 🌐 Démarrage du frontend React...
start "Frontend React" cmd /k "cd /d %CD% && cd frontend-react && npm start"

echo.
echo ✅ Application démarrée !
echo.
echo 📍 Backend: http://localhost:8080
echo 📍 Frontend: http://localhost:3000
echo.
echo 🔐 Identifiants par défaut:
echo    Utilisateur: admin
echo    Mot de passe: admin123
echo.
echo ⚠️  N'oubliez pas de configurer votre fichier .env !
echo.
echo 🧪 Pour tester l'API: python test_app.py
echo.
pause 