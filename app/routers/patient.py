from fastapi import APIRouter, Depends, Request, Form
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from app.database import get_db
from app.models.patient_model import Patient as PatientModel
from app.ml_model.predict import predict_diabetes

router = APIRouter(prefix="/patients", tags=["patients"])

templates = Jinja2Templates(directory="app/templates")

@router.get("/")
def read_patients(request: Request, db: Session = Depends(get_db)):
    patients = db.query(PatientModel).all()
    doctor_name = "Dupont"  # Exemple fixe ou à remplacer par auth
    return templates.TemplateResponse("patients.html", {"request": request, "patients": patients, "doctor_name": doctor_name})

@router.get("/add")
def add_patient_form(request: Request):
    return templates.TemplateResponse("add_patient.html", {"request": request})

@router.post("/add")
def add_patient(request: Request,
                name: str = Form(...),
                age: int = Form(...),
                pregnancies: int = Form(...),
                glucose: int = Form(...),
                blood_pressure: int = Form(...),
                skin_thickness: int = Form(...),
                insulin: int = Form(...),
                bmi: float = Form(...),
                diabetes_pedigree_function: float = Form(...),
                db: Session = Depends(get_db)):
    input_data = [pregnancies, glucose, blood_pressure, skin_thickness, insulin, bmi, diabetes_pedigree_function, age]
    prediction = predict_diabetes(input_data)

    patient = PatientModel(
        name=name,
        age=age,
        pregnancies=pregnancies,
        glucose=glucose,
        blood_pressure=blood_pressure,
        skin_thickness=skin_thickness,
        insulin=insulin,
        bmi=bmi,
        diabetes_pedigree_function=diabetes_pedigree_function,
        prediction=prediction
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return templates.TemplateResponse("add_patient.html", {"request": request, "prediction": "Diabétique" if prediction else "Non diabétique"})
