# 🩺 Application de Prédiction du Diabète pour Médecins

Cette application web permet aux médecins d'enregistrer des patients, de prédire le risque de diabète à l'aide d'un modèle Machine Learning et de stocker les résultats dans une base de données.

## 📂 Structure du projet

├── README.md
├── app
│   ├── __init__.py
│   ├── __pycache__
│   │   ├── __init__.cpython-311.pyc
│   │   ├── database.cpython-311.pyc
│   │   └── main.cpython-311.pyc
│   ├── css
│   │   └── style.css
│   ├── database.py
│   ├── main.py
│   ├── models
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-311.pyc
│   │   │   ├── patient_model.cpython-311.pyc
│   │   │   └── user_model.cpython-311.pyc
│   │   ├── patient_model.py
│   │   └── user_model.py
│   ├── routers
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── patient.py
│   │   └── user_model.py
│   ├── schemas.py
│   ├── static
│   │   └── images
│   │       ├── background.jpg
│   │       ├── en.svg
│   │       ├── favicon.ico
│   │       ├── fr.svg
│   │       └── medicine-logo-png-1.png
│   ├── templates
│   │   ├── add_patient.html
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── patients.html
│   │   ├── profile.html
│   │   └── register.html
│   └── utils.py
├── ml_model
│   ├── model.pkl
│   ├── predict.py
│   └── scaler.pkl
├── requirements.txt
└── run.py


## 🚀 Installation et Lancement

### 1️⃣ Cloner le projet
```bash
git clone https://github.com/votre-repo/diabetes-prediction-app.git
cd diabetes-prediction-app

pip install -r requirements.txt

DATABASE_URL=postgresql://user:password@localhost:5432/diabeto_db
SECRET_KEY=une_cle_ultra_secrete

python run.py
L'application sera accessible sur :
👉 http://127.0.0.1:5000

📊 Fonctionnalités principales:

    Authentification des médecins (inscription, connexion)
    Ajout de patients avec leurs données médicales
    Prédiction du diabète à l'aide d'un modèle Machine Learning (RandomForest / autre)
    Stockage des résultats en base de données PostgreSQL
    Interface utilisateur simple et responsive

🧠 Données utilisées pour la prédiction
Les champs requis pour la prédiction sont :
    Pregnancies
    Glucose
    Blood Pressure
    Skin Thickness
    Insulin
    BMI
    Diabetes Pedigree Function
    Age

🧪 Exemples de données
Patient diabétique
    Pregnancies: 4
    Glucose: 165
    Blood Pressure: 80
    Skin Thickness: 35
    Insulin: 200
    BMI: 33.5
    Diabetes Pedigree Function: 0.75
    Age: 45
Patient non diabétique
    Pregnancies: 1
    Glucose: 90
    Blood Pressure: 70
    Skin Thickness: 20
    Insulin: 80
    BMI: 22.0
    Diabetes Pedigree Function: 0.3
    Age: 28

🛠 Technologies utilisées
    Backend : Flask (Python)
    Base de données : PostgreSQL + SQLAlchemy
    Machine Learning : Scikit-learn, Joblib
    Frontend : HTML, CSS, Jinja2
    Gestion des variables d'environnement : python-dotenv

