from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.doctor import Doctor as DoctorModel
from app.schemas import Doctor
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request

router = APIRouter(prefix="/doctors", tags=["doctors"])

templates = Jinja2Templates(directory="app/templates")

@router.get("/profile/{doctor_id}", response_class=HTMLResponse)
def get_profile(doctor_id: int, request: Request, db: Session = Depends(get_db)):
    doctor = db.query(DoctorModel).filter(DoctorModel.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Médecin non trouvé")
    return templates.TemplateResponse("profile.html", {"request": request, "doctor": doctor})

@router.post("/profile/{doctor_id}", response_class=HTMLResponse)
def update_profile(doctor_id: int, request: Request, nom: str = None, prenom: str = None, specialite: str = None, email: str = None, telephone: str = None, db: Session = Depends(get_db)):
    doctor = db.query(DoctorModel).filter(DoctorModel.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Médecin non trouvé")
    if nom: doctor.nom = nom
    if prenom: doctor.prenom = prenom
    if specialite: doctor.specialite = specialite
    if email: doctor.email = email
    if telephone: doctor.telephone = telephone
    db.commit()
    db.refresh(doctor)
    return {"message": "Profil mis à jour avec succès"}
