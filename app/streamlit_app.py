import streamlit as st
from pathlib import Path
import json
from rules import SafetyRuleEngine
from recommend import RecommendationEngine
from explanation import ExplanationEngine

st.set_page_config(page_title="AfyaChoice AI", layout="wide")

# Hardcoded county context
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
        <img src="https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?w=150" style="border-radius: 10px;">
        <img src="https://images.unsplash.com/photo-1543269865-cbf427effbad?w=150" style="border-radius: 10px;">
        <img src="https://images.unsplash.com/photo-1584515933487-779824d29309?w=150" style="border-radius: 10px;">
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

if st.session_state.step == 1:
    st.subheader("Step 1: Your profile")
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Age", 15, 55, 28)
        county = st.selectbox("County", ["Nairobi", "Garissa", "Kisumu", "Mombasa", "Other"])
        children = st.number_input("Number of children", 0, 10, 2)
    with col2:
        marital = st.selectbox("Marital status", ["Married", "Single", "Living together", "Divorced"])
        education = st.selectbox("Education", ["None", "Primary", "Secondary", "College", "University"])
        partner = st.radio("Partner involved in FP decisions?", ["Yes", "No", "Sometimes"])
    if st.button("Continue"):
        st.session_state.user_data.update({
            "age": age, "county": county.lower(), "children": children,
            "marital": marital, "education": education, "partner": partner
        })
        st.session_state.step = 2
        st.rerun()

elif st.session_state.step == 2:
    st.subheader("Step 2: Health screening (safety first)")
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
    if st.button("Check safety"):
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
    st.subheader("Step 3: Your preferences")
    col1, col2 = st.columns(2)
    with col1:
        long_term = st.radio("Want long term protection (3+ years)?", ["Yes", "No"])
        privacy = st.radio("Need a private method?", ["Yes", "No"])
        non_hormonal = st.radio("Prefer non hormonal methods?", ["Yes", "No"])
    with col2:
        sti_protection = st.radio("Need STI protection?", ["Yes", "No"])
        remember_daily = st.radio("Hard to remember daily pills?", ["Yes", "No"])
    if st.button("Get recommendations"):
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
    st.subheader("Your personalised recommendations")
    county = st.session_state.user_data.get("county", "default")
    ctx = load_county_context().get(county, load_county_context()["default"])
    st.info(f"**{county.title()}** – {ctx['access_notes']}")
    st.caption(ctx["partner_dynamics"])

    rec = st.session_state.recommendations
    if "error" in rec:
        st.warning(rec["error"])
    else:
        expl = ExplanationEngine()
        for i, item in enumerate(rec["ranked_methods"][:3]):
            method_id = item["method_id"]
            score = item["score"]
            details = expl.explain_method(method_id)
            with st.expander(f"{i+1}. {details['summary']} (score {score:.0%})"):
                st.markdown("**Advantages:** " + ", ".join(details["advantages"]))
                st.markdown("**Possible side effects:** " + ", ".join(details["side_effects"]))
        if rec.get("safety_warnings"):
            st.warning("Safety notes: " + "; ".join(rec["safety_warnings"]))

    st.subheader("Myth buster – Ask a question")
    user_q = st.text_input("e.g., Can I use EC twice?")
    if user_q:
        ans = ExplanationEngine().myth_buster(user_q)
        st.success(f"**Fact:** {ans}")

    with st.expander("Provider Assistant (for health workers)"):
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
