from flask import Flask, render_template, request, redirect, url_for, session, flash
from app.database import db
from app.models.patient_model import Patient
from app.models.user_model import Doctor
from dotenv import load_dotenv
import os
import functools
import joblib

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = os.getenv('SECRET_KEY', 'cle_secrete_par_defaut')

    db.init_app(app)

    with app.app_context():
        db.create_all()

    # Chargement modèle ML (adapter le chemin si besoin)
    model_path = os.path.join(os.path.dirname(__file__), '..', 'ml_model', 'model.pkl')
    model = joblib.load(model_path)

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
            new_patient = Patient(
                doctor_id=doctor.id,
                name=request.form.get("name"),
                age=int(request.form.get("age")),
                bmi=float(request.form.get("bmi")),
                glucose=float(request.form.get("glucose")),
                blood_pressure=float(request.form.get("blood_pressure")),
                prediction=float(request.form.get("glucose")) > 125,
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

            print("Features brutes:", features)

            features_scaled = scaler.transform([features])
            print("Features scalées:", features_scaled)

            pred = model.predict(features_scaled)[0]
            print("Prediction (cluster):", pred)

            # Interprétation du cluster
            if pred == 1:
                prediction_text = "Risque élevé (diabétique)"
            else:
                prediction_text = "Risque faible (non diabétique)"

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
                prediction=bool(pred)
            )
            db.session.add(patient)
            db.session.commit()

            return render_template("add_patient.html", prediction=prediction_text)


        return render_template("add_patient.html")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
