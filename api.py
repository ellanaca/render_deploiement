from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import psycopg2
import os

app = FastAPI()



# Charger les variables d'environnement
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")

# # Définir les origines autorisées
# origins = [
#     "http://localhost",
#     "http://localhost:8501",
#     "http://127.0.0.1:8501",
#     "https://render-deploiement.onrender.com/"
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# Définition de la classe modèle pour les données d'entrée
class PredictionInput(BaseModel):
    orga_segment: str
    nom_gestionnaire: str
    prediction: str

@app.get("/")
async def root():
    return {"message": "Bienvenue dans l'API de prédiction de la santé financière des entreprises"}


# Route pour sauvegarder la prédiction
@app.post("/save_prediction")
async def save_prediction(payload: PredictionInput):
    try:
        # Connexion à la base de données
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        cursor = conn.cursor()

        # Insertion de la prédiction dans la base de données
        insert_query = """
        INSERT INTO predictions (orga_segment, nom_gestionnaire, prediction)
        VALUES (%s, %s, %s)
        """
        cursor.execute(insert_query, (payload.orga_segment, payload.nom_gestionnaire, payload.prediction))

        # Validation et fermeture de la connexion
        conn.commit()
        cursor.close()
        conn.close()

        return {"message": "Prédiction enregistrée avec succès!"}

    except Exception as e:
        return {"error": f"Erreur lors de l'enregistrement: {e}"}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)










# # api.py

# from fastapi import FastAPI
# from pydantic import BaseModel

# app = FastAPI()

# # Définition de la classe modèle pour les données d'entrée
# class PredictionInput(BaseModel):
#     orga_segment: str
#     client_comptable: str
#     infotype_garantie: str
#     montant_ht_fi_ar: float
#     evaluation: str
#     delai_aloue: float
#     montant_garantie: float
#     encours: float
#     nom_gestionnaire: str

# # Fonction pour prédire
# def make_prediction(data: PredictionInput) -> str:
#     # Placeholder for prediction logic using your model
#     return "Prediction Placeholder"

# # Définir la route pour la prédiction
# @app.post("/predict")
# async def predict(payload: PredictionInput):
#     prediction = make_prediction(payload)
#     return {"prediction": prediction}
