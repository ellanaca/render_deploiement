import streamlit as st
import requests
import pandas as pd
import joblib

# Définition de l'URL de l'API FastAPI
API_URL = "http://localhost:8000"
headers = {'Content-Type': 'application/json'}

# Fonction pour appeler l'API FastAPI
def predict(data):
    try:
        # Charger le modèle
        with open("model_autre_simplon.pkl", "rb") as f:
            model = joblib.load(f)

        # Assurer que les colonnes du DataFrame correspondent aux colonnes attendues par le modèle
        column_order = ["Orga Segment", "Client Comptable", "Infotype Garantie", "Montant HT (FI-AR)", "Evaluation",
                        "delai aloué", "montant garantie", "encours"]

        # Renommer les clés du dictionnaire pour correspondre aux noms de colonnes attendus
        data_mapped = {
            "Orga Segment": data["orga_segment"],
            "Client Comptable": data["client_comptable"],
            "Infotype Garantie": data["infotype_garantie"],
            "Montant HT (FI-AR)": data["montant_ht_fi_ar"],
            "Evaluation": data["evaluation"],
            "delai aloué": data["delai_aloue"],
            "montant garantie": data["montant_garantie"],
            "encours": data["encours"]
        }

        # Créer le DataFrame
        X = pd.DataFrame([data_mapped])[column_order]

        # Gérer les valeurs manquantes
        X.replace("", None, inplace=True)

        # Assurer que toutes les colonnes sont numériques sauf les colonnes catégorielles
        for col in ["Orga Segment", "Client Comptable", "Infotype Garantie", "Evaluation"]:
            X[col] = X[col].astype(str).fillna("Unknown")

        for col in ["Montant HT (FI-AR)", "delai aloué", "montant garantie", "encours"]:
            X[col] = pd.to_numeric(X[col], errors='coerce')

        # Remplir les valeurs manquantes numériques avec la moyenne si applicable
        X.fillna({
            "Montant HT (FI-AR)": X["Montant HT (FI-AR)"].mean(),
            "delai aloué": X["delai aloué"].mean(),
            "montant garantie": X["montant garantie"].mean(),
            "encours": X["encours"].mean()
        }, inplace=True)

        # Faire la prédiction
        prediction = model.predict(X)

        # Préparer les données pour l'API
        data_to_send = {
            "orga_segment": data["orga_segment"],
            "nom_gestionnaire": data["nom_gestionnaire"],
            "prediction": str(prediction[0])
        }

        # Envoyer la prédiction à Supabase via l'API
        response = requests.post(f"{API_URL}/save_prediction/", json=data_to_send, headers=headers)

        if response.status_code == 200:
            result = response.json()
            return result.get("message")
        else:
            st.error(f"Erreur de l'API : {response.status_code}, {response.text}")
            return None

    except Exception as e:
        st.error(f"Erreur lors de la prédiction : {e}")
        return None

# Application Streamlit
def main():
    st.title('App de Prédiction')

    # Collecte des entrées utilisateur
    orga_segment = st.text_input("Orga Segment")
    client_comptable = st.text_input("Client Comptable")
    infotype_garantie = st.text_input("Infotype Garantie")
    montant_ht_fi_ar = st.number_input("Montant HT (FI-AR)")
    evaluation = st.text_input("Evaluation")
    delai_aloue = st.number_input("Délai Alloué")
    montant_garantie = st.number_input("Montant Garantie")
    encours = st.number_input("Encours")
    nom_gestionnaire = st.text_input("Nom Gestionnaire")

    # Appeler l'API lors du clic sur le bouton
    if st.button('Faire une Prédiction'):
        data = {
            "orga_segment": orga_segment,
            "client_comptable": client_comptable,
            "infotype_garantie": infotype_garantie,
            "montant_ht_fi_ar": montant_ht_fi_ar,
            "evaluation": evaluation,
            "delai_aloue": delai_aloue,
            "montant_garantie": montant_garantie,
            "encours": encours,
            "nom_gestionnaire": nom_gestionnaire
        }

        prediction = predict(data)

        if prediction is not None:
            st.write(f"Prédiction: {prediction}")
        else:
            st.error("Erreur lors de la prédiction")

if __name__ == "__main__":
    main()






# import streamlit as st
# import pandas as pd
# import joblib
# import psycopg2
# from psycopg2.extras import execute_values
# from dotenv import load_dotenv
# import os

# # Load environment variables
# load_dotenv()

# SUPABASE_URL = os.getenv("SUPABASE_URL")
# SUPABASE_KEY = os.getenv("SUPABASE_KEY")
# DB_HOST = os.getenv("DB_HOST")
# DB_NAME = os.getenv("DB_NAME")
# DB_USER = os.getenv("DB_USER")
# DB_PASSWORD = os.getenv("DB_PASSWORD")
# DB_PORT = os.getenv("DB_PORT")

# # Streamlit app
# st.title('App de Prédiction')

# # Collect user input
# orga_segment = st.text_input("Orga Segment")
# client_comptable = st.text_input("Client Comptable")
# infotype_garantie = st.text_input("Infotype Garantie")
# montant_ht_fi_ar = st.number_input("Montant HT (FI-AR)")
# evaluation = st.text_input("Evaluation")
# delai_aloue = st.number_input("Delai Alloué")
# montant_garantie = st.number_input("Montant Garantie")
# encours = st.number_input("Encours")
# nom_gestionnaire = st.text_input("Nom Gestionnaire")

# # Placeholder for predictions
# def predict(data):
#     # Load model
#     with open("model_autre_simplon.pkl", "rb") as f:
#         model = joblib.load(f)

#     # Ensure the DataFrame columns match the model's expected columns
#     column_order = ["Orga Segment", "Client Comptable", "Infotype Garantie", "Montant HT (FI-AR)", "Evaluation",
#                     "delai aloué", "montant garantie", "encours"]

#     # Rename the dictionary keys to match the expected column names
#     data = {
#         "Orga Segment": data["orga_segment"],
#         "Client Comptable": data["client_comptable"],
#         "Infotype Garantie": data["infotype_garantie"],
#         "Montant HT (FI-AR)": data["montant_ht_fi_ar"],
#         "Evaluation": data["evaluation"],
#         "delai aloué": data["delai_aloue"],
#         "montant garantie": data["montant_garantie"],
#         "encours": data["encours"]
#     }

#     # Create DataFrame
#     X = pd.DataFrame([data])[column_order]

#     # Handle missing values
#     X.replace("", None, inplace=True)

#     # Ensure all columns are numeric except for categorical columns
#     for col in ["Orga Segment", "Client Comptable", "Infotype Garantie", "Evaluation"]:
#         X[col] = X[col].astype(str).fillna("Unknown")

#     for col in ["Montant HT (FI-AR)", "delai aloué", "montant garantie", "encours"]:
#         X[col] = pd.to_numeric(X[col], errors='coerce')

#     # Fill numeric missing values with mean if applicable
#     X.fillna({
#         "Montant HT (FI-AR)": X["Montant HT (FI-AR)"].mean(),
#         "delai aloué": X["delai aloué"].mean(),
#         "montant garantie": X["montant garantie"].mean(),
#         "encours": X["encours"].mean()
#     }, inplace=True)

#     prediction = model.predict(X)
#     return prediction[0]

# if st.button('Faire une Prédiction'):
#     data = {
#         "orga_segment": orga_segment,
#         "client_comptable": client_comptable,
#         "infotype_garantie": infotype_garantie,
#         "montant_ht_fi_ar": montant_ht_fi_ar,
#         "evaluation": evaluation,
#         "delai_aloue": delai_aloue,
#         "montant_garantie": montant_garantie,
#         "encours": encours,
#         "nom_gestionnaire": nom_gestionnaire
#     }

#     prediction = predict(data)

#     st.write(f"Prédiction: {prediction}")

#     # Save the prediction in Supabase
#     try:
#         conn = psycopg2.connect(
#             host=DB_HOST,
#             database=DB_NAME,
#             user=DB_USER,
#             password=DB_PASSWORD,
#             port=DB_PORT
#         )
#         cursor = conn.cursor()
#         insert_query = """
#         INSERT INTO predictions (orga_segment, nom_gestionnaire, prediction)
#         VALUES %s
#         """
#         execute_values(cursor, insert_query, [(orga_segment, nom_gestionnaire, prediction)])
#         conn.commit()
#         cursor.close()
#         conn.close()
#         st.success("Prédiction enregistrée avec succès!")
#     except Exception as e:
#         st.error(f"Erreur lors de l'enregistrement: {e}")
