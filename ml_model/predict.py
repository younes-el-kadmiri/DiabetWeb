import joblib
import numpy as np

model = joblib.load("ml_model/model.pkl")    # Ton modèle de classification
scaler = joblib.load("ml_model/scaler.pkl")  # Ton scaler (ex : StandardScaler)

def predict_diabetes(data):
    arr = np.array(data).reshape(1, -1)           # Formatage
    arr_scaled = scaler.transform(arr)            # Normalisation
    pred = model.predict(arr_scaled)              # Prédiction avec modèle
    return bool(pred[0])                          # Retourne True/False
