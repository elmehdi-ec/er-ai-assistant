# ✅ Imports
import os
import json
import datetime
import pandas as pd
import streamlit as st
import altair as alt
import matplotlib.pyplot as plt
from triage_logic import assess_triage
from cas_patients import enregistrer_cas, trier_cas
from export_cas import exporter_file
# ✅ Imports
import os
import json
import datetime
import pandas as pd
import streamlit as st

# 🔒 Bouton déconnexion dans la barre latérale
if st.sidebar.button("🔒 Se déconnecter"):
    st.session_state["authentifie"] = False
    st.experimental_rerun()

# 🔐 Authentification rapide des médecins
if "authentifie" not in st.session_state:
    st.session_state["authentifie"] = False
if "medecin_actif" not in st.session_state:
    st.session_state["medecin_actif"] = ""

# 🧑 Liste des identifiants disponibles
liste_medecins = ["dr_elmehdi", "dr_ayoub", "ide_amal"]

if not st.session_state["authentifie"]:
    st.markdown("## 🔐 Connexion utilisateur")
    identifiant = st.selectbox("🆔 Sélectionnez votre identifiant :", liste_medecins)
    if st.button("🔓 Se connecter"):
        st.session_state["authentifie"] = True
        st.session_state["medecin_actif"] = identifiant
        st.success(f"✅ Connecté en tant que **{identifiant}**")
    st.stop()

# 🌍 Configuration Streamlit
st.set_page_config(page_title="Triage Clinique", page_icon="🩺", layout="centered")

if "mode" not in st.session_state:
    st.session_state["mode"] = "clair"

if st.sidebar.button("🌙 Mode nuit" if st.session_state["mode"] == "clair" else "☀️ Mode clair"):
    st.session_state["mode"] = "nuit" if st.session_state["mode"] == "clair" else "clair"
if st.session_state["mode"] == "clair":
    st.markdown("""
    <style>
    body { background-color: #f8f9fa; font-family: "Segoe UI", sans-serif; }
    h1, h2, h3 { color: #1F3C88; }
    .stTabs [data-baseweb="tab"] { background-color: #E8F0FE; border-radius: 6px; padding: 8px; color: #1F3C88; }
    div.stButton button { background-color: #1F3C88; color: white; border-radius: 8px; padding: 10px; }
    .card { background-color: #ffffff; padding: 16px; border-radius: 10px; box-shadow: 2px 2px 8px rgba(0,0,0,0.1); margin-bottom: 20px; }
    input, textarea, select { font-size: 18px !important; } div.stButton button { width: 100%; }
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    body { background-color: #1c1f26; color: #f0f2f5; font-family: "Segoe UI", sans-serif; }
    h1, h2, h3 { color: #90caf9; }
    .stTabs [data-baseweb="tab"] { background-color: #2b2f3b; color: #f0f2f5; border-radius: 6px; padding: 8px; }
    div.stButton button { background-color: #1565c0; color: white; border-radius: 8px; padding: 10px; }
    .card { background-color: #2c303a; color: #e0e0e0; padding: 16px; border-radius: 10px; border: 1px solid #3e4c63; margin-bottom: 20px; }
    input, textarea, select { font-size: 18px !important; } div.stButton button { width: 100%; }
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)
st.title("🩺 Assistant de Triage Clinique")
mdp = st.text_input("🔑 Mot de passe", type="password")
if mdp != "1234":
    st.warning("Accès restreint.")
    st.stop()

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "👤 Évaluation", "📋 Prise en charge", "📋 File", "📊 Statistiques", "📚 Fiches urgentes", "📂 Dossiers patients"
])

# Initialisation du dossier actif
if "dossier_patient_actuel" not in st.session_state:
    st.session_state["dossier_patient_actuel"] = ""
if "dossier_patient_actuel" not in st.session_state:
    st.session_state["dossier_patient_actuel"] = ""
if "dossier_patient_actuel" not in st.session_state:
    st.session_state["dossier_patient_actuel"] = ""

with tab1:
    st.subheader("🧠 Évaluation patient réel")

    # 👤 Identité
    nom = st.text_input("🧑‍⚕️ Nom ou identifiant du patient")
    age = st.number_input("🧓 Âge", min_value=0, max_value=120, value=30)
    symptome = st.text_area("📝 Motif de consultation (libre)")

    def analyser_systeme(texte):
        texte = texte.lower()
        if any(x in texte for x in ["dyspnée", "toux", "asthme", "crepitants"]): return "Respiratoire"
        if any(x in texte for x in ["thoracique", "oppression", "angine", "palpitations"]): return "Cardiaque"
        if any(x in texte for x in ["céphalée", "vertige", "confusion", "convulsion"]): return "Neurologique"
        if any(x in texte for x in ["fièvre", "infection", "abcès", "pus"]): return "Infectieux"
        if any(x in texte for x in ["plaie", "chute", "trauma", "fracture"]): return "Traumatologique"
        if any(x in texte for x in ["douleur abdominale", "vomissements", "diarrhée"]): return "Digestif"
        return "Inconnu"

    système_suggéré = analyser_systeme(symptome)
    st.markdown(f"🧠 Système suspecté : **{système_suggéré}** *(suggéré par AI)*")

    # 🩺 Constantes vitales
    st.markdown("### 🩺 Constantes vitales")
    fr = st.number_input("🫁 FR", 5, 60, 18)
    fc = st.number_input("❤️ FC", 30, 200, 80)
    pa = st.text_input("💉 PA", "120/80")
    spo2 = st.number_input("🌬️ SpO₂", 0, 100, 98)
    temp = st.number_input("🌡 Température", 30.0, 43.0, 37.0, 0.1)
    gcs = st.number_input("🧠 GCS", 3, 15, 15)
    gly = st.number_input("🍬 Glycémie", 0.4, 3.0, 1.0, 0.1)
    eva = st.slider("⚡ EVA douleur", 0, 10, 5)
    diurese = st.number_input("🚽 Diurèse", 0, 5000, 800)
    pupilles = st.selectbox("👁️ Pupilles", ["Réactives", "Non réactives", "Anisocorie"])
    paralysie = st.selectbox("🧍‍♂️ Paralysie ?", ["Non", "Oui"])

    vitaux = {
        "FR": fr, "FC": fc, "PA": pa, "SpO₂": spo2, "Température": temp, "GCS": gcs,
        "Glycémie": gly, "EVA": eva, "Diurèse": diurese, "Pupilles": pupilles, "Paralysie": paralysie
    }

    # 📊 Évaluation
    if st.button("📊 Évaluer"):
        result = assess_triage(symptome, age, vitaux)
        heure = datetime.datetime.now().strftime("%H:%M:%S")
        grav = int(result.get("gravité", 0))
        couleur = "🔴" if grav == 5 else "🟠" if grav == 4 else "🟡" if grav == 3 else "🟢"

        medecin_id = st.session_state["medecin_actif"]

        st.markdown("### 📊 Résultat AI")
        st.markdown(f"**Gravité** : {couleur} `{grav}/5`")
        st.markdown(f"**ESI** : `{result['esi']}`")
        st.markdown(f"**Red Flag** : `{result['red_flag']}`")
        st.markdown(f"**Orientation AI** : `{result['triage']}`")
        st.markdown(f"**Examens recommandés** : `{result['examens']}`")
        st.markdown(f"👨‍⚕️ Médecin triant : **{medecin_id}**")

        for score, val in result.get("scores", {}).items():
            st.markdown(f"📈 `{score}` : {val}")

        if result.get("système") != "Inconnu":
            st.info(f"🧠 Suggestions AI : `{result['suggestions_ai']}`")

        # 📁 Création dossier patient
        from dossier_patient import creer_dossier_patient
        triage_data = {
            "nom": nom, "âge": age, "symptôme": symptome, "vital": vitaux,
            "triage": result["triage"], "gravité": grav, "esi": result["esi"],
            "red_flag": result["red_flag"], "examens": result["examens"],
            "heure": heure, "scores": result.get("scores", {}),
            "suggestions_ai": result.get("suggestions_ai", ""),
            "médecin": medecin_id
        }
        dossier = creer_dossier_patient(nom, triage_data)
        st.session_state["dossier_patient_actuel"] = dossier
        st.success(f"📁 Dossier patient créé : `{dossier}`")

        # ➕ Ajout CSV si red flag
        if result["red_flag"].startswith("⚠️"):
            if st.button("➕ Ajouter au CSV"):
                df = pd.DataFrame([{
                    "Symptôme": symptome,
                    "Signes_Vitaux": str(vitaux),
                    "Red_Flag": result["red_flag"],
                    "Médecin": medecin_id
                }])
                df.to_csv("data/red_flags.csv", mode="a", header=False, index=False)
                st.success("✅ Cas ajouté.")

    # 🧪 Ajout examens complémentaires
    if st.session_state["dossier_patient_actuel"]:
        st.markdown("### 🧪 Ajouter examens / images")
        uploaded_images = st.file_uploader("📷 Image(s)", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
        examens_types = st.multiselect("🗂️ Type(s)", ["RSP", "TDM", "IRM", "Echo", "ECG", "Bio", "Autre"])
        examens_texte = st.text_area("📝 Compte-rendu / observations")

        if st.button("📂 Enregistrer les examens"):
            for image in uploaded_images:
                path_img = os.path.join(st.session_state["dossier_patient_actuel"], image.name)
                with open(path_img, "wb") as f:
                    f.write(image.getbuffer())
            with open(os.path.join(st.session_state["dossier_patient_actuel"], "examens.json"), "w", encoding="utf-8") as f:
                json.dump({"types": examens_types, "résumé": examens_texte}, f, ensure_ascii=False, indent=4)
            st.success("✅ Examens et imagerie enregistrés.")

with tab2:
    st.subheader("📋 Protocole de prise en charge initiale")

    systemes = ["Respiratoire", "Cardiaque", "Neurologique", "Digestif", "Infectieux", "Trauma", "Urologique", "Autre"]
    choix = st.selectbox("🧠 Système atteint :", systemes)

    st.markdown("### 🔧 Actions recommandées")

    recommandations = {
        "Respiratoire": [
            "Monitorage SpO₂ et FR",
            "Oxygénothérapie (selon SpO₂)",
            "Gaz du sang si dyspnée",
            "Radio thoracique"
        ],
        "Cardiaque": [
            "ECG 12 dérivations",
            "Troponine / BNP",
            "Scope cardiaque",
            "Appel USIC si instabilité"
        ],
        "Neurologique": [
            "Scanner cérébral sans injection",
            "Suivi neurologique (GCS, AVPU)",
            "Pose de VVP si altération conscience",
            "Surveillance rapprochée"
        ],
        "Digestif": [
            "Echo abdominale si douleur localisée",
            "Bilan biologique : lipase, NFS, CRP",
            "Hydratation IV si vomissements"
        ],
        "Infectieux": [
            "Isolement si suspicion contagieuse",
            "Hémocultures + bilan bio",
            "Antibiothérapie probabiliste",
            "Surveillance température + SpO₂"
        ],
        "Trauma": [
            "ATLS : Airway, Breathing, Circulation",
            "Radiographies ciblées",
            "Bilan lésionnel (pan scan si grave)",
            "Antalgie / contention / sutures"
        ],
        "Urologique": [
            "Echo rénale ou vésicale",
            "Sondage évacuateur si rétention",
            "Bilan bio : créat, urée, ECBU"
        ],
        "Autre": ["Action personnalisée à discuter"]
    }

    for action in recommandations.get(choix, []):
        st.markdown(f"✅ {action}")

    st.markdown("---")
    st.markdown("🩺 Tu veux que je te génère un PDF imprimable du protocole choisi ou qu’on connecte ce module au résultat du triage ?")

with tab3:
    st.subheader("📋 File d’attente clinique")
    cas_tries = trier_cas(st.session_state)

    for i, cas in enumerate(cas_tries, start=1):
        couleur = "🔴" if cas["gravité"] == 5 else "🟠" if cas["gravité"] == 4 else "🟡" if cas["gravité"] == 3 else "🟢"
        st.markdown(f"**Cas #{i}** — Gravité : {couleur} `{cas['gravité']}` | ESI : `{cas['esi']}` | 🕒 {cas['heure']}")
        st.write(f"🧓 Âge : `{cas['âge']}` | 🧠 Symptôme : `{cas['symptôme']}` | 💉 Vitaux : `{cas['vital']}`")
        st.write(f"🚨 Red Flag : `{cas['red_flag']}` | 🧪 Examens : `{cas['examens']}`")
        st.markdown("---")

    cas = st.session_state.get("cas_patients", [])
    critiques = [c for c in cas if c["gravité"] == 5]
    if len(critiques) >= 3:
        st.error(f"🚨 {len(critiques)} cas critiques détectés. Risque de surcharge.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Vider la file"):
            st.session_state["cas_patients"] = []
            st.success("🧹 File effacée.")
    with col2:
        if st.button("💾 Exporter la garde"):
            chemin = exporter_file(cas)
            if chemin:
                st.success(f"✅ Export sauvegardé : `{chemin}`")
            else:
                st.warning("Aucun cas à exporter.")
with tab4:
    st.subheader("📊 Statistiques cliniques")
    cas = st.session_state.get("cas_patients", [])
    if cas:
        df_stats = pd.DataFrame(cas)
        df_stats["système"] = df_stats["red_flag"].apply(lambda x: x.split("(")[-1].split(")")[0] if "(" in x else "Inconnu")
        df_stats["type"] = df_stats["gravité"].apply(lambda g: "Critique" if g == 5 else "Autre")

        st.write("🩺 Cas par système médical")
        st.bar_chart(df_stats["système"].value_counts())

        st.write("🎯 Répartition par gravité")
        st.bar_chart(df_stats["gravité"].value_counts().sort_index())

        st.write("📈 Score ESI")
        st.bar_chart(df_stats["esi"].value_counts().sort_index())

        chart_grav = alt.Chart(df_stats).mark_line(point=True).encode(
            x="gravité:O", y="count():Q", color="gravité:O"
        ).properties(width=600)
        st.altair_chart(chart_grav, use_container_width=True)

        st.subheader("🥧 Ratio cas critiques")
        fig, ax = plt.subplots()
        df_stats["type"].value_counts().plot.pie(
            autopct="%1.0f%%", colors=["red", "gray"], ylabel="", ax=ax
        )
        st.pyplot(fig)
    else:
        st.info("Aucun cas enregistré.")
with tab5:
    st.subheader("📚 Fiches urgentes par système médical")
    if cas:
        systemes = sorted(df_stats["système"].unique())
        choix = st.selectbox("🩺 Choisir un système :", systemes)
        sous_df = df_stats[df_stats["système"] == choix]
        for _, ligne in sous_df.iterrows():
            st.markdown(f"### ⚕️ {ligne['symptôme']}")
            st.write(f"🧓 Âge : `{ligne['âge']}` | 💉 Vitaux : `{ligne['vital']}` | 🚨 Red Flag : `{ligne['red_flag']}`")
            st.write(f"🔢 Gravité : `{ligne['gravité']}` | 🧪 Examens : `{ligne['examens']}` | ⏰ {ligne['heure']}")
            st.markdown("---")
    else:
        st.info("⚠️ Aucun cas disponible pour l’exploration.")
import os
import json 
if st.session_state.get("authentifie"):  # ✅ Vérifie que l'utilisateur est connecté
with tab6:
    st.subheader("📂 Dossiers patients enregistrés")

    if os.path.exists("patients"):
        dossiers = os.listdir("patients")
    else:
        dossiers = []

    if dossiers == []:
        st.info("📭 Aucun dossier patient pour le moment.")

    dossiers.sort()

    for dossier in dossiers:
        try:
            with open(os.path.join("patients", dossier, "fiche.json"), encoding="utf-8") as f:
                fiche = json.load(f)
        except:
            continue

        nom_patient = fiche.get("nom", f"dossier_{dossier}")
        st.markdown("---")
        st.markdown(f"### 🧑 {nom_patient} — 🕒 {fiche.get('heure', '—')}")
        st.markdown(f"🔍 Motif : `{fiche.get('symptôme', '—')}`")
        st.markdown(f"⚠️ Red Flag : `{fiche.get('red_flag', '—')}`")
        st.markdown(f"👨‍⚕️ Médecin : `{fiche.get('médecin', '—')}`")
        st.markdown(f"📊 Gravité : `{fiche.get('gravité', '-')}/5` — ESI : `{fiche.get('esi', '-')}`")
        st.markdown(f"📈 Scores : `{fiche.get('scores', {})}`")
        st.markdown(f"🧠 Système : `{fiche.get('système', '—')}`")

        examens_path = os.path.join("patients", dossier, "examens.json")
        if os.path.exists(examens_path):
            try:
                with open(examens_path, encoding="utf-8") as f:
                    examens = json.load(f)
                    st.markdown("### 🧪 Examens complémentaires :")
                    st.markdown(f"- Type(s) : `{examens.get('types', [])}`")
                    st.markdown(f"- Résumé : `{examens.get('résumé', '')}`")
            except:
                st.warning("⚠️ Fichier examens illisible.")

        key_pdf = f"btn_pdf_{dossier}"
        if st.button(f"📤 Exporter PDF : {nom_patient}", key=key_pdf):
            from export_pdf import exporter_pdf
            exporter_pdf(os.path.join("patients", dossier))
            st.success("✅ PDF exporté.")

    # 📊 Lecture sécurisée du fichier CSV
    csv_path = "data/red_flags.csv"
    if os.path.exists(csv_path) and os.path.getsize(csv_path) > 0:
        try:
            df = pd.read_csv(csv_path)
            st.success("📦 Fichier CSV chargé avec succès.")
            st.dataframe(df.head())
        except Exception as e:
            st.error(f"❌ Erreur lecture CSV : {e}")
    else:
        st.warning("⚠️ Fichier CSV `red_flags.csv` absent ou vide.")

    # 📥 Export CSV global
    if st.button("📥 Exporter tous les dossiers en CSV", key="btn_export_all_csv"):
        from export_csv import exporter_all_csv
        exporter_all_csv()
        st.success("📁 Dossiers exportés dans `data/dossiers_export.csv`")
