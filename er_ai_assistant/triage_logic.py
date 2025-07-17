def assess_triage(symptome, age, vitaux):
    gravité = 1
    red_flag = "✅ Aucun"
    esi = 5
    examens = []
    système = "Général"
    scores = {}

    # 🧪 Extraction sécurisée des constantes
    fr = vitaux.get("FR", 18)
    fc = vitaux.get("FC", 80)
    pa = vitaux.get("PA", "120/80")
    spo2 = vitaux.get("SpO2", 98)
    temp = vitaux.get("Température", 37.0)
    gcs = vitaux.get("GCS", 15)
    gly = vitaux.get("Glycémie", 1.0)
    eva = vitaux.get("EVA", 0)
    diurese = vitaux.get("Diurèse", 800)
    pupilles = vitaux.get("Pupilles", "Réactives")
    paralysie = vitaux.get("Paralysie", "Non")

    # 🔢 NEWS2
    news = 0
    if fr < 8 or fr > 25: news += 2
    if fc < 50 or fc > 110: news += 2
    if spo2 < 92: news += 3
    if temp < 35 or temp > 39.5: news += 1
    if gcs < 15: news += 3
    scores["NEWS2"] = news

    # 🔢 qSOFA
    qsofa = 0
    if fr >= 22: qsofa += 1
    if gcs < 15: qsofa += 1
    try:
        sys_bp = int(pa.split("/")[0])
        if sys_bp <= 100: qsofa += 1
    except:
        pass
    scores["qSOFA"] = qsofa

    # 🧠 Analyse complexe des red flags
    if spo2 < 90 or gcs <= 8 or paralysie == "Oui" or pupilles != "Réactives":
        gravité = 5
        red_flag = "⚠️ Détresse neurologique / respiratoire"
        esi = 1
        examens = ["Scanner cérébral", "Gaz du sang", "Intubation"]
        système = "Critique"
    elif gly < 0.7 or gly > 2.0:
        gravité = 4
        red_flag = "⚠️ Trouble glycémique"
        esi = 2
        examens = ["Bilan diabétique", "GDS", "Monitorage"]
        système = "Métabolique"
    elif temp > 39.5 or fc > 120:
        gravité = 3
        red_flag = "⚠️ Fièvre / infection probable"
        esi = 3
        examens = ["NFS", "CRP", "Hémocultures"]
        système = "Infectieux"
    elif diurese < 400:
        gravité = 3
        red_flag = "⚠️ Oligurie / suspicion IRA"
        esi = 3
        examens = ["Créatinine", "Écho rénale", "Ionogramme"]
        système = "Rénal"
    elif eva >= 7:
        gravité = 2
        red_flag = "⚠️ Douleur intense"
        esi = 3
        examens = ["Analgesie", "Imagerie localisée"]
        système = "Algique"
    else:
        gravité = 1
        red_flag = "✅ Stable"
        esi = 5
        examens = ["Surveillance", "Examens complémentaires"]
        système = "Général"

    return {
        "triage": "Critique" if gravité >= 4 else "Standard",
        "gravité": gravité,
        "esi": esi,
        "red_flag": red_flag + f" ({système})",
        "examens": ", ".join(examens),
        "système": système,
        "scores": scores,
        "suggestions_ai": f"Orientation vers prise en charge {système}"
    }
