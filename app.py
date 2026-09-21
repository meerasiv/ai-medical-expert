"""
AI Medical Expert System
-------------------------
A simple, beginner-friendly rule-based expert system built for a
college mini-project.

Technologies used:
- Streamlit  -> web interface
- Pandas     -> loading and processing the medical knowledge base (CSV)
- SQLite     -> storing assessment history

IMPORTANT: This is NOT a machine-learning system. It simply compares
the symptoms a user selects against a small knowledge base of common
conditions and shows how many symptoms match. It is an educational
project only and is not a substitute for professional medical advice.
"""

import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# ---------------------------------------------------------------------
# BASIC APP CONFIGURATION
# ---------------------------------------------------------------------

st.set_page_config(
    page_title="AI Medical Expert",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

DB_FILE = "medical.db"
CSV_FILE = "diseases.csv"

SYMPTOM_LIST = [
    "Fever", "Cough", "Sore Throat", "Headache", "Fatigue", "Body Pain",
    "Runny Nose", "Nausea", "Vomiting", "Diarrhea", "Abdominal Pain", "Dizziness"
]

WARNING_SYMPTOMS = ["Vomiting", "Diarrhea", "Abdominal Pain", "Dizziness"]

NAV_PAGES = ["Home", "New Assessment", "History", "About"]
NAV_ICONS = {"Home": "🏠", "New Assessment": "🩺", "History": "📋", "About": "ℹ️"}

# ---------------------------------------------------------------------
# GLOBAL STYLE — hides Streamlit chrome and builds a "real website" feel
# ---------------------------------------------------------------------

def inject_css(css: str) -> None:
    """Inject raw CSS safely. Prefers st.html (no markdown parsing, so the
    CSS text can never leak onto the page as visible text); falls back to
    st.markdown for older Streamlit versions that lack st.html."""
    html_block = f"<style>{css}</style>"
    if hasattr(st, "html"):
        st.html(html_block)
    else:
        st.markdown(html_block, unsafe_allow_html=True)


APP_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&family=Inter:wght@400;500;600&display=swap');

:root {
    --primary: #0f766e;
    --primary-dark: #0b5a54;
    --primary-light: #14b8a6;
    --accent: #38bdf8;
    --bg: #f4faf9;
    --card-bg: #ffffff;
    --text-dark: #0f2e2b;
    --text-muted: #5b6b69;
    --danger: #ef4444;
    --warning: #f59e0b;
    --success: #22c55e;
    --radius: 18px;
}

html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif;
}
h1, h2, h3, h4, h5, .nav-title {
    font-family: 'Poppins', sans-serif !important;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header[data-testid="stHeader"] {background: transparent;}
div[data-testid="stToolbar"] {visibility: hidden;}
section[data-testid="stSidebar"] {display: none;}

.stApp {
    background: linear-gradient(180deg, #f4faf9 0%, #eef7f6 100%);
}

.block-container {
    padding-top: 1.2rem;
    max-width: 1100px;
}

/* ---------------- NAVBAR ---------------- */
.navbar-wrap {
    background: var(--card-bg);
    border-radius: 999px;
    padding: 10px 18px;
    box-shadow: 0 4px 20px rgba(15, 118, 110, 0.08);
    margin-bottom: 2rem;
    border: 1px solid #e4f2f0;
}
.navbar-inner {
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.brand {
    display: flex;
    align-items: center;
    gap: 10px;
    font-weight: 700;
    font-size: 1.15rem;
    color: var(--primary-dark);
    white-space: nowrap;
}
.brand-badge {
    background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
    color: white;
    width: 36px;
    height: 36px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    box-shadow: 0 4px 10px rgba(20, 184, 166, 0.35);
}

div[data-testid="stHorizontalBlock"] div.stButton > button {
    background: transparent;
    border: none;
    color: var(--text-muted);
    font-weight: 600;
    font-size: 0.95rem;
    border-radius: 999px;
    padding: 0.5rem 1.1rem;
    transition: all 0.15s ease;
    width: 100%;
}
div[data-testid="stHorizontalBlock"] div.stButton > button:hover {
    background: #e7f6f4;
    color: var(--primary-dark);
}
.nav-active button {
    background: var(--primary) !important;
    color: white !important;
    box-shadow: 0 4px 12px rgba(15, 118, 110, 0.35);
}

/* ---------------- HERO ---------------- */
.hero {
    background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary) 55%, var(--accent) 120%);
    border-radius: 28px;
    padding: 3rem 2.5rem;
    color: white;
    position: relative;
    overflow: hidden;
    margin-bottom: 2rem;
    box-shadow: 0 20px 40px rgba(15, 118, 110, 0.25);
}
.hero::after {
    content: "";
    position: absolute;
    right: -60px;
    top: -60px;
    width: 260px;
    height: 260px;
    background: rgba(255,255,255,0.08);
    border-radius: 50%;
}
.hero::before {
    content: "";
    position: absolute;
    left: 30%;
    bottom: -90px;
    width: 200px;
    height: 200px;
    background: rgba(255,255,255,0.06);
    border-radius: 50%;
}
.hero-eyebrow {
    text-transform: uppercase;
    letter-spacing: 2px;
    font-size: 0.75rem;
    font-weight: 600;
    opacity: 0.85;
    margin-bottom: 0.6rem;
}
.hero h1 {
    font-size: 2.6rem;
    font-weight: 800;
    margin: 0 0 0.6rem 0;
    line-height: 1.15;
    color: white !important;
}
.hero p {
    font-size: 1.05rem;
    opacity: 0.92;
    max-width: 560px;
    margin-bottom: 0;
}

/* ---------------- CARDS ---------------- */
.card {
    background-color: var(--card-bg);
    padding: 1.5rem;
    border-radius: var(--radius);
    border: 1px solid #eaf3f1;
    box-shadow: 0 6px 18px rgba(15, 118, 110, 0.06);
    margin-bottom: 1.1rem;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.card:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 24px rgba(15, 118, 110, 0.12);
}
.stat-card {
    text-align: left;
    padding: 1.4rem 1.5rem;
}
.stat-label {
    color: var(--text-muted);
    font-size: 0.85rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 0.3rem;
}
.stat-value {
    font-size: 1.9rem;
    font-weight: 800;
    color: var(--text-dark);
    margin: 0;
}
.stat-icon {
    font-size: 1.6rem;
    margin-bottom: 0.5rem;
}

.feature-card {
    text-align: left;
    height: 100%;
}
.feature-icon {
    font-size: 1.8rem;
    margin-bottom: 0.6rem;
}
.feature-title {
    font-weight: 700;
    color: var(--text-dark);
    margin-bottom: 0.3rem;
}
.feature-text {
    color: var(--text-muted);
    font-size: 0.9rem;
    line-height: 1.5;
}

.result-card {
    background: linear-gradient(135deg, #ffffff 0%, #f0faf8 100%);
}

.symptom-tag {
    display: inline-block;
    background-color: #e6f4f1;
    color: var(--primary-dark);
    padding: 5px 14px;
    border-radius: 999px;
    margin: 4px 4px 0 0;
    font-size: 0.85rem;
    font-weight: 600;
    border: 1px solid #cdeae5;
}

.risk-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 18px;
    border-radius: 999px;
    font-weight: 700;
    font-size: 1.1rem;
}
.risk-Low { background: #eafcef; color: #16803c; }
.risk-Moderate { background: #fff7e6; color: #b45309; }
.risk-High { background: #fdecec; color: #b91c1c; }

.condition-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.match-bar-bg {
    background: #eef5f4;
    border-radius: 999px;
    height: 8px;
    width: 100%;
    margin-top: 8px;
    overflow: hidden;
}
.match-bar-fill {
    background: linear-gradient(90deg, var(--primary) 0%, var(--accent) 100%);
    height: 100%;
    border-radius: 999px;
}

.disclaimer {
    background-color: #eaf6f6;
    border-left: 4px solid var(--primary-light);
    padding: 0.9rem 1.1rem;
    border-radius: 10px;
    font-size: 0.88rem;
    color: #33403f;
}

.section-heading {
    font-weight: 700;
    color: var(--text-dark);
    margin: 1.6rem 0 0.6rem 0;
    font-size: 1.15rem;
}

/* Buttons */
div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
    border: none;
    border-radius: 12px;
    padding: 0.6rem 1.6rem;
    font-weight: 700;
    box-shadow: 0 6px 16px rgba(15, 118, 110, 0.3);
}
div.stButton > button[kind="primary"]:hover {
    box-shadow: 0 8px 20px rgba(15, 118, 110, 0.42);
    transform: translateY(-1px);
}

.footer-note {
    text-align: center;
    color: var(--text-muted);
    font-size: 0.8rem;
    margin-top: 2.5rem;
    padding-top: 1rem;
    border-top: 1px solid #e4f2f0;
}
"""

inject_css(APP_CSS)


# ---------------------------------------------------------------------
# DATABASE FUNCTIONS (SQLite)
# ---------------------------------------------------------------------

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT,
            age INTEGER,
            gender TEXT,
            symptoms TEXT,
            severity TEXT,
            duration TEXT,
            risk_level TEXT,
            top_conditions TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_assessment(name, age, gender, symptoms, severity, duration, risk_level, top_conditions):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO assessments
        (patient_name, age, gender, symptoms, severity, duration, risk_level, top_conditions, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name, age, gender,
        ", ".join(symptoms),
        severity, duration, risk_level,
        top_conditions,
        datetime.now().strftime("%Y-%m-%d %H:%M")
    ))
    conn.commit()
    conn.close()


def load_history():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM assessments ORDER BY id DESC", conn)
    conn.close()
    return df


def clear_history():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM assessments")
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------
# KNOWLEDGE BASE FUNCTIONS (Pandas)
# ---------------------------------------------------------------------

def load_knowledge_base():
    return pd.read_csv(CSV_FILE)


def match_symptoms(selected_symptoms, df):
    results = []
    for _, row in df.iterrows():
        condition_name = row["Condition"]
        matched = [s for s in selected_symptoms if row.get(s, 0) == 1]
        match_count = len(matched)
        if len(selected_symptoms) > 0:
            match_percent = round((match_count / len(selected_symptoms)) * 100)
        else:
            match_percent = 0
        results.append({
            "condition": condition_name,
            "match_percent": match_percent,
            "matched_symptoms": matched
        })
    results = [r for r in results if r["match_percent"] > 0]
    results.sort(key=lambda r: r["match_percent"], reverse=True)
    return results[:3]


# ---------------------------------------------------------------------
# RISK ASSESSMENT LOGIC
# ---------------------------------------------------------------------

def calculate_risk(severity, selected_symptoms):
    if severity == "Mild":
        risk = "Low"
    elif severity == "Moderate":
        risk = "Moderate"
    else:
        risk = "High"
    show_warning = severity == "Severe" and any(s in WARNING_SYMPTOMS for s in selected_symptoms)
    return risk, show_warning


def risk_emoji(risk_level):
    return {"Low": "🟢", "Moderate": "🟡", "High": "🔴"}.get(risk_level, "⚪")


# ---------------------------------------------------------------------
# RESULT GENERATION
# ---------------------------------------------------------------------

def generate_recommendation(risk_level):
    base = [
        "Monitor your symptoms and note any changes.",
        "Maintain adequate hydration and rest.",
    ]
    if risk_level == "Low":
        base.append("Symptoms appear mild. Continue self-care and rest.")
    elif risk_level == "Moderate":
        base.append("Consider consulting a healthcare professional if symptoms persist or worsen.")
    else:
        base.append("Please consider seeking professional medical attention promptly.")
    return base


# ---------------------------------------------------------------------
# INITIALIZE APP STATE
# ---------------------------------------------------------------------

init_db()
knowledge_base = load_knowledge_base()

if "page" not in st.session_state:
    st.session_state.page = "Home"
if "last_result" not in st.session_state:
    st.session_state.last_result = None

DISCLAIMER = ("This application provides an educational symptom assessment and "
              "is not a substitute for professional medical advice.")


# ---------------------------------------------------------------------
# TOP NAVBAR (renders like a real website header, not a sidebar)
# ---------------------------------------------------------------------

st.markdown('<div class="navbar-wrap">', unsafe_allow_html=True)
nav_cols = st.columns([2.4, 1, 1, 1, 1])
with nav_cols[0]:
    st.markdown(
        '<div class="brand"><div class="brand-badge">🩺</div> AI Medical Expert</div>',
        unsafe_allow_html=True
    )
for i, page_name in enumerate(NAV_PAGES):
    with nav_cols[i + 1]:
        is_active = st.session_state.page == page_name
        if is_active:
            st.markdown('<div class="nav-active">', unsafe_allow_html=True)
        if st.button(f"{NAV_ICONS[page_name]} {page_name}", key=f"nav_{page_name}", use_container_width=True):
            st.session_state.page = page_name
            st.rerun()
        if is_active:
            st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

page = st.session_state.page


# ---------------------------------------------------------------------
# HOME PAGE
# ---------------------------------------------------------------------

if page == "Home":
    st.markdown("""
        <div class="hero">
            <div class="hero-eyebrow">Educational Health Assistant</div>
            <h1>Understand your symptoms<br>in a few clicks.</h1>
            <p>A simple, rule-based expert system that compares your symptoms against a
            knowledge base of common conditions — built as a learning project, designed
            to feel like a real product.</p>
        </div>
    """, unsafe_allow_html=True)

    history_df = load_history()
    total_assessments = len(history_df)
    last_assessment = history_df.iloc[0]["created_at"] if total_assessments > 0 else "—"
    recent_risk = history_df.iloc[0]["risk_level"] if total_assessments > 0 else "N/A"

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""<div class="card stat-card">
                    <div class="stat-icon">📊</div>
                    <div class="stat-label">Total Assessments</div>
                    <p class="stat-value">{total_assessments}</p></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="card stat-card">
                    <div class="stat-icon">🕒</div>
                    <div class="stat-label">Last Assessment</div>
                    <p class="stat-value" style="font-size:1.3rem;">{last_assessment}</p></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="card stat-card">
                    <div class="stat-icon">{risk_emoji(recent_risk)}</div>
                    <div class="stat-label">Recent Risk Level</div>
                    <p class="stat-value" style="font-size:1.3rem;">{recent_risk}</p></div>""", unsafe_allow_html=True)

    st.write("")
    cta_col, _ = st.columns([1, 3])
    with cta_col:
        if st.button("▶️  Start Assessment", type="primary", use_container_width=True):
            st.session_state.page = "New Assessment"
            st.rerun()

    st.markdown('<div class="section-heading">How it works</div>', unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)
    with f1:
        st.markdown("""<div class="card feature-card">
            <div class="feature-icon">📝</div>
            <div class="feature-title">1. Describe symptoms</div>
            <div class="feature-text">Select what you're experiencing, how severe it is, and how long it's lasted.</div>
            </div>""", unsafe_allow_html=True)
    with f2:
        st.markdown("""<div class="card feature-card">
            <div class="feature-icon">🔍</div>
            <div class="feature-title">2. Get matched</div>
            <div class="feature-text">Your symptoms are compared against a knowledge base of common conditions.</div>
            </div>""", unsafe_allow_html=True)
    with f3:
        st.markdown("""<div class="card feature-card">
            <div class="feature-icon">📋</div>
            <div class="feature-title">3. Review results</div>
            <div class="feature-text">See a risk level, possible conditions, and general self-care guidance.</div>
            </div>""", unsafe_allow_html=True)

    st.write("")
    st.markdown(f'<div class="disclaimer">⚠️ {DISCLAIMER}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------
# NEW ASSESSMENT PAGE
# ---------------------------------------------------------------------

elif page == "New Assessment":
    st.markdown('<h2 style="margin-bottom:0;">🩺 New Assessment</h2>', unsafe_allow_html=True)
    st.caption("Fill in the details below to get a symptom-based assessment.")
    st.write("")

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-heading" style="margin-top:0;">Patient Information</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        name = st.text_input("Name")
    with c2:
        age = st.number_input("Age", min_value=0, max_value=120, value=25)
    with c3:
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-heading" style="margin-top:0;">Symptoms</div>', unsafe_allow_html=True)
    selected_symptoms = st.multiselect("Select all symptoms that apply", SYMPTOM_LIST)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-heading" style="margin-top:0;">Symptom Details</div>', unsafe_allow_html=True)
    c4, c5 = st.columns(2)
    with c4:
        severity = st.radio("Symptom Severity", ["Mild", "Moderate", "Severe"], horizontal=True)
    with c5:
        duration = st.selectbox(
            "Duration",
            ["Less than 1 day", "1–3 days", "4–7 days", "More than 1 week"]
        )
    st.markdown('</div>', unsafe_allow_html=True)

    st.write("")
    analyze = st.button("🔍  Analyze Symptoms", type="primary")

    if analyze:
        if len(selected_symptoms) == 0:
            st.error("Please select at least one symptom before analyzing.")
        elif not name:
            st.error("Please enter the patient's name.")
        else:
            top_matches = match_symptoms(selected_symptoms, knowledge_base)
            risk_level, show_warning = calculate_risk(severity, selected_symptoms)

            conditions_summary = "; ".join(
                [f"{m['condition']} ({m['match_percent']}%)" for m in top_matches]
            ) if top_matches else "No clear match found"

            st.session_state.last_result = {
                "name": name,
                "age": age,
                "gender": gender,
                "symptoms": selected_symptoms,
                "severity": severity,
                "duration": duration,
                "risk_level": risk_level,
                "show_warning": show_warning,
                "top_matches": top_matches,
            }

            save_assessment(
                name, age, gender, selected_symptoms, severity, duration,
                risk_level, conditions_summary
            )

            st.success("✅ Assessment complete! See your results below.")

    # -------------------------------------------------------------
    # RESULTS SECTION (shown after analysis)
    # -------------------------------------------------------------
    result = st.session_state.last_result
    if result:
        st.markdown("---")
        st.markdown('<div class="section-heading" style="font-size:1.4rem;">📄 Assessment Result</div>', unsafe_allow_html=True)

        risk = result["risk_level"]
        st.markdown(f"""
            <div class="card result-card">
                <div class="stat-label">Patient</div>
                <p style="font-size:1.1rem; font-weight:600; margin:0 0 0.9rem 0;">{result['name']}, {result['age']} years old ({result['gender']})</p>
                <div class="stat-label">Risk Level</div>
                <span class="risk-badge risk-{risk}">{risk_emoji(risk)} {risk}</span>
            </div>
        """, unsafe_allow_html=True)

        if result["show_warning"]:
            st.warning("⚠️ Severe symptoms reported. It is recommended to seek professional "
                       "medical attention promptly.")

        st.markdown('<div class="section-heading">Selected Symptoms</div>', unsafe_allow_html=True)
        tags_html = "".join([f'<span class="symptom-tag">{s}</span>' for s in result["symptoms"]])
        st.markdown(f'<div class="card">{tags_html}</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-heading">Possible Conditions</div>', unsafe_allow_html=True)
        if result["top_matches"]:
            for i, m in enumerate(result["top_matches"], start=1):
                st.markdown(f"""
                    <div class="card">
                        <div class="condition-row">
                            <b>{i}. {m['condition']}</b>
                            <span style="color:var(--primary-dark); font-weight:700;">{m['match_percent']}%</span>
                        </div>
                        <div class="match-bar-bg"><div class="match-bar-fill" style="width:{m['match_percent']}%;"></div></div>
                        <small style="color:var(--text-muted);"><i>Why this appeared:</i> matched on {", ".join(m['matched_symptoms'])}</small>
                    </div>
                """, unsafe_allow_html=True)
            st.caption("These are symptom-match scores based on a simplified educational "
                       "knowledge base, NOT medical probabilities or diagnoses.")
        else:
            st.info("No condition in the knowledge base closely matched the selected symptoms.")

        st.markdown('<div class="section-heading">General Recommendation</div>', unsafe_allow_html=True)
        rec_html = "".join([f"<li style='margin-bottom:4px;'>{tip}</li>" for tip in generate_recommendation(risk)])
        st.markdown(f'<div class="card"><ul style="margin:0; padding-left:1.2rem;">{rec_html}</ul></div>', unsafe_allow_html=True)

        st.markdown(f'<div class="disclaimer">⚠️ {DISCLAIMER}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------
# ASSESSMENT HISTORY PAGE
# ---------------------------------------------------------------------

elif page == "History":
    st.markdown('<h2 style="margin-bottom:0;">📋 Assessment History</h2>', unsafe_allow_html=True)
    st.caption("Browse and review all past assessments.")
    st.write("")

    history_df = load_history()

    if history_df.empty:
        st.markdown("""<div class="card" style="text-align:center; padding:2.5rem;">
            <div style="font-size:2.2rem;">📭</div>
            <p style="color:var(--text-muted); margin-top:0.5rem;">No assessments recorded yet. Head to <b>New Assessment</b> to create one.</p>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        display_df = history_df.rename(columns={
            "created_at": "Date",
            "patient_name": "Patient",
            "symptoms": "Symptoms",
            "risk_level": "Risk",
            "top_conditions": "Possible Conditions"
        })[["Date", "Patient", "Symptoms", "Risk", "Possible Conditions"]]
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-heading">View Assessment Details</div>', unsafe_allow_html=True)
        selected_id = st.selectbox(
            "Select a record to view full details",
            options=history_df.index,
            format_func=lambda i: f"{history_df.loc[i, 'patient_name']} — {history_df.loc[i, 'created_at']}"
        )
        record = history_df.loc[selected_id]
        st.markdown(f"""
            <div class="card">
                <div class="condition-row">
                    <b style="font-size:1.05rem;">{record['patient_name']}</b>
                    <span class="risk-badge risk-{record['risk_level']}">{risk_emoji(record['risk_level'])} {record['risk_level']}</span>
                </div>
                <p style="color:var(--text-muted); margin:0.6rem 0 0.2rem 0;">{record['age']} years old &nbsp;•&nbsp; {record['gender']}</p>
                <p style="margin:0.4rem 0;"><b>Symptoms:</b> {record['symptoms']}</p>
                <p style="margin:0.4rem 0;"><b>Severity:</b> {record['severity']} &nbsp;|&nbsp; <b>Duration:</b> {record['duration']}</p>
                <p style="margin:0.4rem 0;"><b>Possible Conditions:</b> {record['top_conditions']}</p>
                <p style="margin:0.4rem 0 0 0; color:var(--text-muted); font-size:0.85rem;">{record['created_at']}</p>
            </div>
        """, unsafe_allow_html=True)

        st.write("")
        with st.expander("🗑️  Clear History"):
            st.write("This will permanently delete all saved assessments.")
            if st.button("Confirm: Clear All History"):
                clear_history()
                st.success("History cleared.")
                st.rerun()


# ---------------------------------------------------------------------
# ABOUT PAGE
# ---------------------------------------------------------------------

elif page == "About":
    st.markdown('<h2 style="margin-bottom:0;">ℹ️ About This Project</h2>', unsafe_allow_html=True)
    st.write("")

    st.markdown("""
    <div class="card">
    <div class="section-heading" style="margin-top:0;">AI Medical Expert System</div>
    <p style="color:var(--text-muted);">This is a college mini-project demonstrating a simple <b>rule-based expert system</b>
    for educational symptom assessment.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-heading">How it works</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="card">
    <ul style="margin:0; padding-left:1.2rem; color:var(--text-dark);">
        <li>The user selects symptoms, severity, and duration.</li>
        <li>The system compares selected symptoms against a small knowledge base
        of common conditions stored in <code>diseases.csv</code>.</li>
        <li>A symptom-match percentage is calculated for each condition using Pandas.</li>
        <li>The top 3 matching conditions are displayed, along with a simple
        rule-based risk level.</li>
        <li>Every assessment is saved to a local SQLite database for later review.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-heading">Technologies used</div>', unsafe_allow_html=True)
    t1, t2, t3 = st.columns(3)
    for col, (icon, label) in zip([t1, t2, t3], [("🐍", "Python + Streamlit"), ("🐼", "Pandas"), ("🗄️", "SQLite")]):
        with col:
            st.markdown(f"""<div class="card feature-card" style="text-align:center;">
                <div class="feature-icon">{icon}</div>
                <div class="feature-title">{label}</div>
                </div>""", unsafe_allow_html=True)

    st.write("")
    st.markdown(f'<div class="disclaimer">⚠️ {DISCLAIMER}</div>', unsafe_allow_html=True)

st.markdown('<div class="footer-note">AI Medical Expert System — Educational Mini-Project</div>', unsafe_allow_html=True)
