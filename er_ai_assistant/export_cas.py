import pandas as pd
import os
from datetime import datetime

def exporter_file(cas_list):
    if not cas_list:
        return None

    df = pd.DataFrame(cas_list)
    dossier = "exports"
    os.makedirs(dossier, exist_ok=True)

    horodatage = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nom_fichier = f"{dossier}/garde_{horodatage}.csv"
    df.to_csv(nom_fichier, index=False, encoding="utf-8-sig")
    return nom_fichier
