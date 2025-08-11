from flask import Flask, render_template, request, redirect, url_for, session, flash
from app.database import db
from app.models.patient_model import Patient
from app.models.user_model import Doctor
from dotenv import load_dotenv
import os
import functools
import joblib
import numpy as np

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = os.getenv('SECRET_KEY', 'cle_secrete_par_defaut')

    db.init_app(app)

    with app.app_context():
        db.create_all()

    # Chargement modèle ML
    model_path = os.path.join(os.path.dirname(__file__), '..', 'ml_model', 'model.pkl')
    scaler_path = os.path.join(os.path.dirname(__file__), '..', 'ml_model', 'scaler.pkl')
    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)

    # Fonction de prédiction
    def predict_diabetes(features):
        """
        features : liste [pregnancies, glucose, blood_pressure, skin_thickness,
                          insulin, bmi, diabetes_pedigree_function, age]
        Retourne True si diabétique, False sinon
        """
        arr = np.array(features).reshape(1, -1)
        arr_scaled = scaler.transform(arr)
        pred = model.predict(arr_scaled)[0]

        # Si c'est un classifieur binaire
        if pred in [0, 1]:
            return bool(pred)
        # Si c'est un clusteriseur type KMeans
        # Ici on suppose que cluster 1 = diabétique
        return pred == 1

    # Décorateur pour protéger routes
    def login_required(view):
        @functools.wraps(view)
        def wrapped_view(**kwargs):
            if 'doctor_id' not in session:
                flash("Connectez-vous d'abord.")
                return redirect(url_for('login'))
            return view(**kwargs)
        return wrapped_view

    @app.route("/")
    def home():
        return redirect(url_for("login"))

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            nom = request.form.get("nom")
            prenom = request.form.get("prenom")
            email = request.form.get("email")
            password = request.form.get("password")
            specialite = request.form.get("specialite")
            telephone = request.form.get("telephone")

            if Doctor.query.filter_by(email=email).first():
                flash("Email déjà utilisé.")
                return redirect(url_for("register"))

            new_doctor = Doctor(
                nom=nom,
                prenom=prenom,
                email=email,
                specialite=specialite,
                telephone=telephone
            )
            new_doctor.set_password(password)
            db.session.add(new_doctor)
            db.session.commit()
            flash("Compte créé avec succès. Connectez-vous.")
            return redirect(url_for("login"))

        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")

            doctor = Doctor.query.filter_by(email=email).first()
            if doctor and doctor.check_password(password):
                session.clear()
                session['doctor_id'] = doctor.id
                flash("Connexion réussie.")
                return redirect(url_for("patients"))
            else:
                flash("Email ou mot de passe incorrect.")

        return render_template("login.html")

    @app.route("/profile", methods=["GET", "POST"])
    @login_required
    def profile():
        doctor = Doctor.query.get(session['doctor_id'])
        if request.method == "POST":
            doctor.nom = request.form.get("nom")
            doctor.prenom = request.form.get("prenom")
            doctor.specialite = request.form.get("specialite")
            doctor.telephone = request.form.get("telephone")
            doctor.email = request.form.get("email")
            db.session.commit()
            flash("Profil mis à jour.")
            return redirect(url_for("profile"))
        return render_template("profile.html", doctor=doctor)

    @app.route("/patients", methods=["GET", "POST"])
    @login_required
    def patients():
        doctor = Doctor.query.get(session['doctor_id'])
        if request.method == "POST":
            # Récupération des features
            features = [
                float(request.form.get('pregnancies')),
                float(request.form.get('glucose')),
                float(request.form.get('blood_pressure')),
                float(request.form.get('skin_thickness')),
                float(request.form.get('insulin')),
                float(request.form.get('bmi')),
                float(request.form.get('diabetes_pedigree_function')),
                float(request.form.get('age'))
            ]
            prediction_result = predict_diabetes(features)

            new_patient = Patient(
                doctor_id=doctor.id,
                name=request.form.get("name"),
                age=int(request.form.get("age")),
                pregnancies=int(request.form.get("pregnancies")),
                glucose=float(request.form.get("glucose")),
                blood_pressure=float(request.form.get("blood_pressure")),
                skin_thickness=float(request.form.get("skin_thickness")),
                insulin=float(request.form.get("insulin")),
                bmi=float(request.form.get("bmi")),
                diabetes_pedigree_function=float(request.form.get("diabetes_pedigree_function")),
                prediction=prediction_result
            )
            db.session.add(new_patient)
            db.session.commit()
            return redirect(url_for("patients"))

        patients_list = Patient.query.filter_by(doctor_id=doctor.id).all()
        return render_template("patients.html", patients=patients_list, doctor_name=f"{doctor.prenom} {doctor.nom}")

    @app.route("/add_patient", methods=["GET", "POST"])
    @login_required
    def add_patient():
        prediction_text = None
        doctor = Doctor.query.get(session['doctor_id'])

        if request.method == "POST":
            features = [
                float(request.form.get('pregnancies')),
                float(request.form.get('glucose')),
                float(request.form.get('blood_pressure')),
                float(request.form.get('skin_thickness')),
                float(request.form.get('insulin')),
                float(request.form.get('bmi')),
                float(request.form.get('diabetes_pedigree_function')),
                float(request.form.get('age'))
            ]

            prediction_result = predict_diabetes(features)
            prediction_text = "Diabétique" if prediction_result else "Non diabétique"

            # Stockage
            patient = Patient(
                doctor_id=doctor.id,
                name=request.form.get("name"),
                age=int(request.form.get("age")),
                pregnancies=int(request.form.get("pregnancies")),
                glucose=float(request.form.get("glucose")),
                blood_pressure=float(request.form.get("blood_pressure")),
                skin_thickness=float(request.form.get("skin_thickness")),
                insulin=float(request.form.get("insulin")),
                bmi=float(request.form.get("bmi")),
                diabetes_pedigree_function=float(request.form.get("diabetes_pedigree_function")),
                prediction=prediction_result
            )
            db.session.add(patient)
            db.session.commit()

            return render_template("add_patient.html", prediction=prediction_text)

        return render_template("add_patient.html")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
