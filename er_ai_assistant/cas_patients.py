# 📦 Module pour gérer les cas patients dans la session Streamlit

def enregistrer_cas(session_state, result, age, symptome, vitaux, heure):
    """Ajoute un patient dans la file d'attente avec ses données cliniques."""
    if "cas_patients" not in session_state:
        session_state["cas_patients"] = []

    session_state["cas_patients"].append({
        "âge": age,
        "symptôme": symptome,
        "vital": vitaux,
        "triage": result.get("triage", ""),
        "red_flag": result.get("red_flag", ""),
        "gravité": int(result.get("gravité", 0)),
        "esi": int(result.get("esi", 0)),
        "examens": result.get("examens", ""),
        "heure": heure
    })

def trier_cas(session_state):
    """Retourne les cas triés par gravité (desc) puis score ESI (asc)."""
    if "cas_patients" not in session_state:
        return []
    return sorted(session_state["cas_patients"], key=lambda x: (-x["gravité"], x["esi"]))
