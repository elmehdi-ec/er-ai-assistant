import os
import json
from datetime import datetime

def creer_dossier_patient(nom, triage_data):
    # Si le nom est vide, on utilise "Anonyme"
    nom = nom.strip() or "Anonyme"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dossier_path = os.path.join("patients", f"Patient_{nom}_{timestamp}")
    os.makedirs(dossier_path, exist_ok=True)

    fiche_path = os.path.join(dossier_path, "fiche.json")
    with open(fiche_path, "w", encoding="utf-8") as f:
        json.dump(triage_data, f, ensure_ascii=False, indent=4)

    return dossier_path
