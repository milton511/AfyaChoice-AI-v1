import streamlit as st
import time
from pathlib import Path
import json
from rules import SafetyRuleEngine
from recommend import RecommendationEngine
from explanation import ExplanationEngine

st.set_page_config(page_title="AfyaChoice AI", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS with motion graphics, cursor effects, and animations
st.markdown("""
<style>
    /* Animated gradient background */
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .stApp {
        background: linear-gradient(-45deg, #e0f2fe, #f0f9ff, #e0f2fe, #f0f9ff);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
    }

    /* Custom cursor trail effect */
    * {
        cursor: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="24" height="27" viewBox="0 0 24 27"><polygon points="2,2 20,12 12,12 20,24 2,2" fill="%232c7da0" stroke="%231f5068" stroke-width="1"/></svg>') 4 4, auto;
    }

    /* Floating animation for cards */
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-8px); }
        100% { transform: translateY(0px); }
    }
    .recommendation-card {
        background: rgba(255,255,255,0.9);
        backdrop-filter: blur(4px);
        border-radius: 1rem;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border-left: 5px solid #2c7da0;
    }
    .recommendation-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 16px 32px rgba(0,0,0,0.15);
        animation: float 1s ease-in-out infinite;
    }

    /* Pulse animation for buttons */
    @keyframes pulse {
        0% { transform: scale(1); box-shadow: 0 0 0 0 #2c7da0; }
        70% { transform: scale(1.02); box-shadow: 0 0 0 10px rgba(44,125,160,0); }
        100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(44,125,160,0); }
    }
    .stButton > button {
        background: #2c7da0;
        color: white;
        border-radius: 2rem;
        padding: 0.6rem 2rem;
        font-weight: 600;
        border: none;
        transition: all 0.3s;
        animation: pulse 2s infinite;
    }
    .stButton > button:hover {
        background: #1f5068;
        transform: scale(1.02);
        animation: none;
    }

    /* Step indicator with progress */
    .step-container {
        display: flex;
        justify-content: space-between;
        margin-bottom: 2rem;
    }
    .step {
        background: #e9ecef;
        padding: 0.5rem 1rem;
        border-radius: 2rem;
        font-size: 0.9rem;
        color: #495057;
        transition: all 0.3s;
    }
    .step-active {
        background: #2c7da0;
        color: white;
        transform: scale(1.05);
        box-shadow: 0 0 0 4px rgba(44,125,160,0.3);
    }
    .step-completed {
        background: #2e7d32;
        color: white;
    }

    /* Input fields styling */
    .stTextInput>div>div>input, .stSelectbox>div>div>select, .stNumberInput>div>div>input {
        border-radius: 0.75rem;
        border: 1px solid #cbd5e1;
        transition: 0.2s;
    }
    .stTextInput>div>div>input:focus {
        border-color: #2c7da0;
        box-shadow: 0 0 0 2px rgba(44,125,160,0.2);
    }

    /* Info box */
    .stInfo {
        background: rgba(44,125,160,0.1);
        border-radius: 1rem;
        padding: 0.8rem;
        border-left: 4px solid #2c7da0;
    }

    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        margin-top: 2rem;
        color: #6c757d;
        font-size: 0.8rem;
        border-top: 1px solid rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# Hardcoded county context (no JSON file)
COUNTY_CONTEXT = {
    "default": {"access_notes": "Family planning services available at public health facilities, private clinics, and pharmacies.", "partner_dynamics": "You can access services independently. Discuss with provider if needed."},
    "nairobi": {"access_notes": "Wide access across the city. Many youth-friendly centres and Marie Stopes clinics.", "partner_dynamics": "Independent access common. Confidential services available."},
    "garissa": {"access_notes": "Services at Garissa Referral Hospital and mobile clinics. Community health workers available.", "partner_dynamics": "Discussing with husband may be helpful. Female providers available."}
}

def load_county_context():
    return COUNTY_CONTEXT

st.markdown(
    """
    <div style="display: flex; gap: 20px; justify-content: center; margin-bottom: 20px;">
        <img src="https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?w=150" style="border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
        <img src="https://images.unsplash.com/photo-1543269865-cbf427effbad?w=150" style="border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
        <img src="https://images.unsplash.com/photo-1584515933487-779824d29309?w=150" style="border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
    </div>
    """,
    unsafe_allow_html=True
)

st.title("AfyaChoice AI")
st.markdown("**Evidence based family planning decision support – Kenya FP Guidelines 2025**")

if "step" not in st.session_state:
    st.session_state.step = 1
if "user_data" not in st.session_state:
    st.session_state.user_data = {}
if "recommendations" not in st.session_state:
    st.session_state.recommendations = None

def show_step_indicator(current):
    steps = ["Profile", "Health", "Preferences", "Results"]
    cols = st.columns(4)
    for i, (col, name) in enumerate(zip(cols, steps), 1):
        if i < current:
            col.markdown(f"<div class='step step-completed'>✓ {name}</div>", unsafe_allow_html=True)
        elif i == current:
            col.markdown(f"<div class='step step-active'>{name}</div>", unsafe_allow_html=True)
        else:
            col.markdown(f"<div class='step'>{name}</div>", unsafe_allow_html=True)

show_step_indicator(st.session_state.step)

if st.session_state.step == 1:
    st.subheader("👤 Your profile")
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Age", 15, 55, 28)
        county = st.selectbox("County", ["Nairobi", "Garissa", "Kisumu", "Mombasa", "Other"])
        children = st.number_input("Number of children", 0, 10, 2)
    with col2:
        marital = st.selectbox("Marital status", ["Married", "Single", "Living together", "Divorced"])
        education = st.selectbox("Education", ["None", "Primary", "Secondary", "College", "University"])
        partner = st.radio("Partner involved in FP decisions?", ["Yes", "No", "Sometimes"])
    if st.button("Continue →"):
        st.session_state.user_data.update({
            "age": age, "county": county.lower(), "children": children,
            "marital": marital, "education": education, "partner": partner
        })
        st.session_state.step = 2
        st.rerun()

elif st.session_state.step == 2:
    st.subheader("🩺 Health screening (safety first)")
    col1, col2 = st.columns(2)
    with col1:
        pregnant = st.radio("Currently pregnant?", ["No", "Yes"])
        breastfeeding = st.radio("Currently breastfeeding?", ["No", "Yes"])
        weeks_pp = st.number_input("Weeks since delivery", 0, 52, 6) if breastfeeding == "Yes" else 100
        smoker = st.radio("Smoker?", ["No", "Yes"])
        migraine_aura = st.radio("Migraine with aura?", ["No", "Yes"])
    with col2:
        blood_clots = st.radio("History of blood clots?", ["No", "Yes"])
        breast_cancer = st.radio("Current or past breast cancer?", ["No", "Yes"])
        pelvic_infection = st.radio("Current pelvic infection?", ["No", "Yes"])
        heavy_bleeding = st.radio("Heavy menstrual bleeding?", ["No", "Yes"])
        hypertension = st.radio("High blood pressure?", ["No", "Yes"])
    if st.button("Check safety →"):
        health = {
            "age": st.session_state.user_data["age"],
            "breastfeeding": breastfeeding == "Yes",
            "weeks_postpartum": weeks_pp,
            "smoker": smoker == "Yes",
            "migraine_with_aura": migraine_aura == "Yes",
            "blood_clot_history": blood_clots == "Yes",
            "breast_cancer_current": breast_cancer == "Yes",
            "pelvic_infection_current": pelvic_infection == "Yes",
            "heavy_menstrual_bleeding": heavy_bleeding == "Yes",
            "hypertension": hypertension == "Yes",
            "parity": st.session_state.user_data["children"],
            "education": st.session_state.user_data["education"],
            "marital": st.session_state.user_data["marital"]
        }
        st.session_state.user_data["health"] = health
        st.session_state.step = 3
        st.rerun()

elif st.session_state.step == 3:
    st.subheader("⚙️ Your preferences")
    col1, col2 = st.columns(2)
    with col1:
        long_term = st.radio("Want long term protection (3+ years)?", ["Yes", "No"])
        privacy = st.radio("Need a private method?", ["Yes", "No"])
        non_hormonal = st.radio("Prefer non hormonal methods?", ["Yes", "No"])
    with col2:
        sti_protection = st.radio("Need STI protection?", ["Yes", "No"])
        remember_daily = st.radio("Hard to remember daily pills?", ["Yes", "No"])
    if st.button("Get recommendations →"):
        pref = {
            "wants_long_term": long_term == "Yes",
            "needs_privacy": privacy == "Yes",
            "wants_non_hormonal": non_hormonal == "Yes",
            "wants_std_protection": sti_protection == "Yes",
            "difficulty_remembering_daily": remember_daily == "Yes",
        }
        st.session_state.user_data["preferences"] = pref
        rec_engine = RecommendationEngine()
        result = rec_engine.get_recommendations(
            st.session_state.user_data["health"],
            st.session_state.user_data["preferences"],
            st.session_state.user_data.get("county")
        )
        st.session_state.recommendations = result
        st.session_state.step = 4
        st.rerun()

elif st.session_state.step == 4:
    st.subheader("✨ Your personalised recommendations")
    county = st.session_state.user_data.get("county", "default")
    ctx = load_county_context().get(county, load_county_context()["default"])
    st.info(f"📍 **{county.title()}** – {ctx['access_notes']}\n\n👥 {ctx['partner_dynamics']}")

    rec = st.session_state.recommendations
    if "error" in rec:
        st.warning(rec["error"])
    else:
        expl = ExplanationEngine()
        for i, item in enumerate(rec["ranked_methods"][:3]):
            method_id = item["method_id"]
            score = item["score"]
            details = expl.explain_method(method_id)
            with st.expander(f"{i+1}. {details['summary']} (score {score:.0%})", expanded=(i==0)):
                st.markdown("**Advantages:** " + ", ".join(details["advantages"]))
                st.markdown("**Possible side effects:** " + ", ".join(details["side_effects"]))
        if rec.get("safety_warnings"):
            st.warning("⚠️ Safety notes: " + "; ".join(rec["safety_warnings"]))

    st.subheader("💡 Myth buster – Ask a question")
    user_q = st.text_input("e.g., Can I use EC twice?")
    if user_q:
        ans = ExplanationEngine().myth_buster(user_q)
        st.success(f"**Fact:** {ans}")

    with st.expander("👩‍⚕️ Provider Assistant (for health workers)"):
        st.markdown("Enter a patient profile to get counselling checklist:")
        p_age = st.number_input("Patient age", 15, 55, 28)
        p_bf = st.checkbox("Breastfeeding")
        p_smoker = st.checkbox("Smoker")
        if st.button("Generate checklist"):
            sr = SafetyRuleEngine()
            unsafe = sr.apply({"age": p_age, "breastfeeding": p_bf, "smoker": p_smoker})
            st.write("**Unsafe methods:**", ", ".join(unsafe["unsafe_methods"]) if unsafe["unsafe_methods"] else "None")
            st.write("**Counselling points:** Provide detailed explanation of safe methods and follow-up plan.")

    if st.button("Start over"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

st.markdown("<div class='footer'>© 2026 AfyaChoice AI – Kenya FP Guidelines 2025</div>", unsafe_allow_html=True)
