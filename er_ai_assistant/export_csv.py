import os, json
import pandas as pd

def exporter_all_csv():
    dossiers = os.listdir("patients")
    lignes = []
    for nom in dossiers:
        fiche_path = os.path.join("patients", nom, "fiche.json")
        if os.path.exists(fiche_path):
            try:
                with open(fiche_path, encoding="utf-8") as f:
                    data = json.load(f)
                lignes.append(data)
            except: pass
    df = pd.DataFrame(lignes)
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/dossiers_export.csv", index=False)
