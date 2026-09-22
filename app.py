"""
AI Medical Expert System
-------------------------
A simple, beginner-friendly rule-based expert system built for a
college mini-project with a refined, modern clinical UI/UX.

Technologies used:
- Streamlit  -> web interface
- Pandas     -> loading and processing the medical knowledge base (CSV)
- SQLite     -> storing assessment history
"""

import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# ---------------------------------------------------------------------
# BASIC APP CONFIGURATION
# ---------------------------------------------------------------------

st.set_page_config(
    page_title="Health Expert System",
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
# GLOBAL STYLE — Dark Teal & Slate Modern Theme
# ---------------------------------------------------------------------

def inject_css(css: str) -> None:
    html_block = f"<style>{css}</style>"
    if hasattr(st, "html"):
        st.html(html_block)
    else:
        st.markdown(html_block, unsafe_allow_html=True)


APP_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --brand-dark: #0f2e2b;
    --brand-teal: #0f766e;
    --brand-light-teal: #e6f4f1;
    --brand-accent: #14b8a6;
    --bg-surface: #f0f7ff;
    --card-border: #dbe4e2;
    --text-main: #0f2e2b;
    --text-muted: #5b6b69;
    --radius: 12px;
}

html, body, [class*="css"]  {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: var(--text-main);
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header[data-testid="stHeader"] {background: transparent;}
div[data-testid="stToolbar"] {visibility: hidden;}
section[data-testid="stSidebar"] {display: none;}

.stApp {
    background-color: var(--bg-surface);
}

.block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
    max-width: 900px;
}

/* ---------------- NAVBAR ---------------- */
.navbar-wrap {
    background: #1e293b;
    border-radius: var(--radius);
    padding: 12px 24px;
    box-shadow: 0 2px 8px rgba(15, 46, 43, 0.05);
    margin-bottom: 1.5rem;
    border: 1px solid var(--card-border);
}
.brand {
    display: flex;
    align-items: center;
    gap: 10px;
    font-weight: 800;
    font-size: 1.15rem;
    color: var(--brand-dark);
    letter-spacing: -0.3px;
}
.brand-badge {
    background: var(--brand-dark);
    color: white;
    width: 32px;
    height: 32px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
}

div[data-testid="stHorizontalBlock"] div.stButton > button {
    background: transparent;
    border: none;
    color: var(--text-muted);
    font-weight: 600;
    font-size: 0.9rem;
    border-radius: 8px;
    padding: 0.4rem 0.8rem;
    transition: all 0.2s ease;
    width: 100%;
}
div[data-testid="stHorizontalBlock"] div.stButton > button:hover {
    background: var(--brand-light-teal);
    color: var(--brand-dark);
}
.nav-active button {
    background: var(--brand-dark) !important;
    color: #ffffff !important;
}

/* ---------------- HERO / HEADER CARDS ---------------- */
.hero-card {
    background: var(--brand-dark);
    border-radius: var(--radius);
    padding: 2.2rem 2rem;
    color: white;
    margin-bottom: 1.5rem;
}
.hero-card h1 {
    font-size: 1.8rem;
    font-weight: 800;
    margin: 0 0 0.5rem 0;
    color: white !important;
    line-height: 1.2;
}
.hero-card p {
    font-size: 0.95rem;
    opacity: 0.88;
    margin: 0;
    line-height: 1.5;
}

/* ---------------- COMPACT CARDS ---------------- */
.card {
    background-color: #ffffff;
    padding: 1.25rem 1.5rem;
    border-radius: var(--radius);
    border: 1px solid var(--card-border);
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}

.stat-card {
    border-top: 3px solid var(--brand-teal);
    text-align: left;
}
.stat-label {
    color: var(--text-muted);
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.stat-value {
    font-size: 1.5rem;
    font-weight: 800;
    color: var(--brand-dark);
    margin: 0.2rem 0 0 0;
}

/* ---------------- FIX FOR INPUT WHITE SPACES ---------------- */
/* Blends Streamlit input boxes into the page styling seamlessly */
div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
    border-radius: 8px !important;
    border: 1px solid var(--card-border) !important;
    background-color: #ffffff !important;
}
div[data-baseweb="input"]:focus-within > div, div[data-baseweb="select"]:focus-within > div {
    border-color: var(--brand-teal) !important;
}
.stMultiSelect [data-baseweb="tag"] {
    background-color: var(--brand-light-teal) !important;
    border: 1px solid #b2d8d8 !important;
    border-radius: 6px !important;
}
.stMultiSelect [data-baseweb="tag"] span {
    color: var(--brand-dark) !important;
    font-weight: 600 !important;
}

/* ---------------- BADGES & RESULTS ---------------- */
.symptom-tag {
    display: inline-block;
    background-color: var(--brand-light-teal);
    color: var(--brand-dark);
    padding: 4px 12px;
    border-radius: 20px;
    margin: 3px 3px 3px 0;
    font-size: 0.82rem;
    font-weight: 600;
    border: 1px solid #c8e4df;
}

.risk-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 14px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.95rem;
}
.risk-Low { background: #e6f4ea; color: #137333; }
.risk-Moderate { background: #fef7e0; color: #b06000; }
.risk-High { background: #fce8e6; color: #c5221f; }

.match-bar-bg {
    background: #eef2f5;
    border-radius: 999px;
    height: 6px;
    width: 100%;
    margin-top: 6px;
    overflow: hidden;
}
.match-bar-fill {
    background: var(--brand-teal);
    height: 100%;
    border-radius: 999px;
}

.disclaimer {
    background-color: #ffffff;
    border: 1px solid var(--card-border);
    border-left: 3px solid var(--brand-teal);
    padding: 0.75rem 1rem;
    border-radius: 8px;
    font-size: 0.82rem;
    color: var(--text-muted);
}

.section-title {
    font-weight: 700;
    color: var(--brand-dark);
    margin: 1rem 0 0.5rem 0;
    font-size: 1.05rem;
}

/* Primary Button Styling */
div.stButton > button[kind="primary"] {
    background: var(--brand-dark);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.6rem 1.5rem;
    font-weight: 700;
    transition: background 0.2s ease;
}
div.stButton > button[kind="primary"]:hover {
    background: var(--brand-teal);
}

.footer-note {
    text-align: center;
    color: var(--text-muted);
    font-size: 0.78rem;
    margin-top: 2rem;
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
# TOP NAVBAR
# ---------------------------------------------------------------------

st.markdown('<div class="navbar-wrap">', unsafe_allow_html=True)
nav_cols = st.columns([2.5, 1, 1, 1, 1])
with nav_cols[0]:
    st.markdown(
        '<div class="brand"><div class="brand-badge">🩺</div> Clinical Expert</div>',
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
        <div class="hero-card">
            <h1>Symptom Assessment Engine</h1>
            <p>Answer simple questions about your symptoms to evaluate potential condition matches
            against our rule-based expert knowledge system.</p>
        </div>
    """, unsafe_allow_html=True)

    history_df = load_history()
    total_assessments = len(history_df)
    last_assessment = history_df.iloc[0]["created_at"] if total_assessments > 0 else "—"
    recent_risk = history_df.iloc[0]["risk_level"] if total_assessments > 0 else "N/A"

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""<div class="card stat-card">
                    <div class="stat-label">Total Completed</div>
                    <p class="stat-value">{total_assessments}</p></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="card stat-card">
                    <div class="stat-label">Last Checkup</div>
                    <p class="stat-value" style="font-size:1.1rem; padding-top:0.3rem;">{last_assessment}</p></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="card stat-card">
                    <div class="stat-label">Last Risk State</div>
                    <p class="stat-value" style="font-size:1.1rem; padding-top:0.3rem;">{risk_emoji(recent_risk)} {recent_risk}</p></div>""", unsafe_allow_html=True)

    st.write("")
    if st.button("Start Assessment →", type="primary"):
        st.session_state.page = "New Assessment"
        st.rerun()

    st.markdown('<div class="section-title">How It Works</div>', unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)
    with f1:
        st.markdown("""<div class="card">
            <div style="font-weight:700; color:var(--brand-dark); margin-bottom:0.3rem;">1. Input Details</div>
            <div style="font-size:0.85rem; color:var(--text-muted);">Enter personal details along with current active symptoms.</div>
            </div>""", unsafe_allow_html=True)
    with f2:
        st.markdown("""<div class="card">
            <div style="font-weight:700; color:var(--brand-dark); margin-bottom:0.3rem;">2. Match Conditions</div>
            <div style="font-size:0.85rem; color:var(--text-muted);">Symptoms match across rule sets in our dataset.</div>
            </div>""", unsafe_allow_html=True)
    with f3:
        st.markdown("""<div class="card">
            <div style="font-weight:700; color:var(--brand-dark); margin-bottom:0.3rem;">3. Review Report</div>
            <div style="font-size:0.85rem; color:var(--text-muted);">Get a simple match report and suggested next steps.</div>
            </div>""", unsafe_allow_html=True)

    st.write("")
    st.markdown(f'<div class="disclaimer">⚠️ {DISCLAIMER}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------
# NEW ASSESSMENT PAGE
# ---------------------------------------------------------------------

elif page == "New Assessment":
    st.markdown('<h3 style="margin-bottom:0.2rem; color:var(--brand-dark);">New Assessment</h3>', unsafe_allow_html=True)
    st.caption("Please provide accurate details for a reliable rule match.")
    st.write("")

    st.markdown('<div class="section-title" style="margin-top:0;">1. Patient Details</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        name = st.text_input("Full Name", placeholder="e.g. John Doe")
    with c2:
        age = st.number_input("Age", min_value=0, max_value=120, value=25)
    with c3:
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])

    st.markdown('<div class="section-title">2. Select Symptoms</div>', unsafe_allow_html=True)
    selected_symptoms = st.multiselect("Search or select symptoms", SYMPTOM_LIST)

    st.markdown('<div class="section-title">3. Severity & Duration</div>', unsafe_allow_html=True)
    c4, c5 = st.columns(2)
    with c4:
        severity = st.radio("Symptom Severity", ["Mild", "Moderate", "Severe"], horizontal=True)
    with c5:
        duration = st.selectbox(
            "Duration",
            ["Less than 1 day", "1–3 days", "4–7 days", "More than 1 week"]
        )

    st.write("")
    analyze = st.button("Generate Health Assessment", type="primary")

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

            st.success("Assessment calculated successfully.")

    # -------------------------------------------------------------
    # RESULTS SECTION
    # -------------------------------------------------------------
    result = st.session_state.last_result
    if result:
        st.markdown("---")
        st.markdown('<div class="section-title" style="font-size:1.2rem;">Assessment Summary</div>', unsafe_allow_html=True)

        risk = result["risk_level"]
        st.markdown(f"""
            <div class="card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <div style="font-weight:700; font-size:1.1rem; color:var(--brand-dark);">{result['name']} ({result['age']}y, {result['gender']})</div>
                        <div style="font-size:0.85rem; color:var(--text-muted); margin-top:0.2rem;">Duration: {result['duration']} | Severity: {result['severity']}</div>
                    </div>
                    <div>
                        <span class="risk-badge risk-{risk}">{risk_emoji(risk)} {risk} Risk</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        if result["show_warning"]:
            st.warning("⚠️ Severe symptoms reported. It is recommended to seek professional medical attention promptly.")

        st.markdown('<div class="section-title">Reported Symptoms</div>', unsafe_allow_html=True)
        tags_html = "".join([f'<span class="symptom-tag">{s}</span>' for s in result["symptoms"]])
        st.markdown(f'<div class="card">{tags_html}</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">Matching Conditions</div>', unsafe_allow_html=True)
        if result["top_matches"]:
            for i, m in enumerate(result["top_matches"], start=1):
                st.markdown(f"""
                    <div class="card">
                        <div style="display:flex; justify-content:space-between;">
                            <b>{i}. {m['condition']}</b>
                            <span style="color:var(--brand-teal); font-weight:700;">{m['match_percent']}% Match</span>
                        </div>
                        <div class="match-bar-bg"><div class="match-bar-fill" style="width:{m['match_percent']}%;"></div></div>
                        <div style="font-size:0.8rem; color:var(--text-muted); margin-top:0.4rem;">Matched symptoms: {", ".join(m['matched_symptoms'])}</div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No condition in the knowledge base matched the selected symptoms.")

        st.markdown('<div class="section-title">Next Steps</div>', unsafe_allow_html=True)
        rec_html = "".join([f"<li style='margin-bottom:4px;'>{tip}</li>" for tip in generate_recommendation(risk)])
        st.markdown(f'<div class="card"><ul style="margin:0; padding-left:1.2rem; font-size:0.9rem;">{rec_html}</ul></div>', unsafe_allow_html=True)

        st.markdown(f'<div class="disclaimer">⚠️ {DISCLAIMER}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------
# HISTORY PAGE
# ---------------------------------------------------------------------

elif page == "History":
    st.markdown('<h3 style="margin-bottom:0.2rem; color:var(--brand-dark);">Assessment History</h3>', unsafe_allow_html=True)
    st.caption("Review past assessment logs stored in local database.")
    st.write("")

    history_df = load_history()

    if history_df.empty:
        st.markdown("""<div class="card" style="text-align:center; padding:2rem;">
            <p style="color:var(--text-muted); margin:0;">No record found. Start a new assessment to log data.</p>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        display_df = history_df.rename(columns={
            "created_at": "Date",
            "patient_name": "Patient",
            "symptoms": "Symptoms",
            "risk_level": "Risk",
            "top_conditions": "Matches"
        })[["Date", "Patient", "Symptoms", "Risk", "Matches"]]
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">Detailed Inspection</div>', unsafe_allow_html=True)
        selected_id = st.selectbox(
            "Select assessment record",
            options=history_df.index,
            format_func=lambda i: f"{history_df.loc[i, 'patient_name']} — {history_df.loc[i, 'created_at']}"
        )
        record = history_df.loc[selected_id]
        st.markdown(f"""
            <div class="card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="font-size:1.05rem; color:var(--brand-dark);">{record['patient_name']}</b>
                    <span class="risk-badge risk-{record['risk_level']}">{risk_emoji(record['risk_level'])} {record['risk_level']}</span>
                </div>
                <div style="color:var(--text-muted); font-size:0.85rem; margin:0.4rem 0;">{record['age']} yrs old | {record['gender']}</div>
                <p style="margin:0.4rem 0; font-size:0.9rem;"><b>Symptoms:</b> {record['symptoms']}</p>
                <p style="margin:0.4rem 0; font-size:0.9rem;"><b>Severity:</b> {record['severity']} &nbsp;|&nbsp; <b>Duration:</b> {record['duration']}</p>
                <p style="margin:0.4rem 0; font-size:0.9rem;"><b>Matches:</b> {record['top_conditions']}</p>
            </div>
        """, unsafe_allow_html=True)

        st.write("")
        with st.expander("Clear Database Records"):
            if st.button("Confirm: Clear History"):
                clear_history()
                st.success("History cleared.")
                st.rerun()


# ---------------------------------------------------------------------
# ABOUT PAGE
# ---------------------------------------------------------------------

elif page == "About":
    st.markdown('<h3 style="margin-bottom:0.2rem; color:var(--brand-dark);">About AI Medical Expert</h3>', unsafe_allow_html=True)
    st.write("")

    st.markdown("""
    <div class="card">
    <p style="color:var(--text-main); margin:0;">This is a college mini-project demonstrating a <b>rule-based expert system</b>
    designed with a clean, modern clinical UI/UX.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Core Components</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="card">
    <ul style="margin:0; padding-left:1.2rem; color:var(--text-main); font-size:0.9rem;">
        <li>Symptom selection & intensity scale inputs.</li>
        <li>CSV-backed Knowledge Base matching using Pandas data structures.</li>
        <li>Rule engine to calculate matching ratios and risk levels.</li>
        <li>SQLite persistent transaction database.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    st.markdown(f'<div class="disclaimer">⚠️ {DISCLAIMER}</div>', unsafe_allow_html=True)

st.markdown('<div class="footer-note">AI Medical Expert System — Educational Mini-Project</div>', unsafe_allow_html=True)
