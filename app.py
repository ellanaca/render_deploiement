import streamlit as st
import requests
import pandas as pd
import joblib
import os
from dotenv import load_dotenv

load_dotenv()

# Définition de l'URL de l'API FastAPI
url = os.environ['FASTAPI_URL']
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
        response = requests.post(f"{url}/save_prediction/", json=data_to_send, headers=headers)

        if response.status_code == 200:
            result = response.json()
            st.write(f"Prédiction: {prediction[0]}")
            return result.get("message")
        else:
            st.error(f"Erreur de l'API : {response.status_code}, {response.text}")
            return None

    except Exception as e:
        st.error(f"Erreur lors de la prédiction : {e}")
        return None


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

        # if prediction is not None:
        #     st.write(f"Prédiction: {0}")
        # else:
        #     st.error("Erreur lors de la prédiction")

def change_is_logged_session():
    st.session_state["is_logged"] = not st.session_state["is_logged"]

### WEB APPLICATION ###
# session state
if "is_logged" not in st.session_state:
    st.session_state["is_logged"] = False


# login form if not logged
if st.session_state["is_logged"] == False:

    placeholder = st.empty()

    with placeholder.form("login"):
        st.markdown("#### Bonjour, veuillez renseigner vos identifiants")
        user_email = st.text_input(label="Email", placeholder="votremail@exemple.com")
        user_password = st.text_input(label="Mot de passe", placeholder="Enter votre mot de passe", type="password")
        login_button = st.form_submit_button("Login")

        if ((login_button) and (user_email == os.environ['EMAIL']) and (user_password == os.environ['PASSWORD'])):
            change_is_logged_session()
            placeholder.empty()
        elif ((login_button) and ((user_email != os.environ['EMAIL']) or (user_password != os.environ['PASSWORD']))):
            st.error('Identifiants incorrects, veuillez réessayer', icon="⚠️")

# submit main  if logged
if st.session_state["is_logged"] == True:
    st.button("Déconnexion", on_click=change_is_logged_session)
    st.text("Bienvenue, vous allez pouvoir connaitre la prédiction financière de votre entreprise !")
    main()

