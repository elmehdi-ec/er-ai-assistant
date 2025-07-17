from fpdf import FPDF
import os
import json

def nettoyer_texte(texte):
    if not isinstance(texte, str):
        texte = str(texte)
    return texte.replace("—", "-").replace("–", "-").encode("latin-1", "replace").decode("latin-1")

def exporter_pdf(dossier_path):
    fiche_path = os.path.join(dossier_path, "fiche.json")
    if not os.path.exists(fiche_path):
        return

    with open(fiche_path, encoding="utf-8") as f:
        data = json.load(f)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(0, 10, txt="Fiche de triage patient", ln=True, align="C")
    pdf.ln(8)

    champs = {
        "Nom": data.get("nom", "-"),
        "Âge": data.get("âge", "-"),
        "Médecin": data.get("médecin", "-"),
        "Date/Heure": data.get("heure", "-"),
        "Symptôme": data.get("symptôme", "-"),
        "Système AI": data.get("système", "-"),
        "Red Flag": data.get("red_flag", "-"),
        "Gravité": f"{data.get('gravité', '-')}/5",
        "ESI": data.get("esi", "-"),
        "Orientation AI": data.get("triage", "-"),
        "Examens suggérés": data.get("examens", "-"),
        "Suggestions AI": data.get("suggestions_ai", "-")
    }

    for champ, valeur in champs.items():
        pdf.cell(0, 10, txt=nettoyer_texte(f"{champ} : {valeur}"), ln=True)

    pdf.ln(4)
    scores = data.get("scores", {})
    if scores:
        pdf.cell(0, 10, txt="Scores cliniques :", ln=True)
        for score, val in scores.items():
            pdf.cell(0, 10, txt=nettoyer_texte(f"- {score} : {val}"), ln=True)

    pdf.output(os.path.join(dossier_path, "fiche_patient.pdf"))
