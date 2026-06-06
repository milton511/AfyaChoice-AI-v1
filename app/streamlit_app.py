import streamlit as st
from PIL import Image
from recommend import rank_methods
import datetime
import math

st.set_page_config(page_title="AfyaChoice AI", page_icon="🌸", layout="wide")

# ---------- THEME STATE ----------
if "theme" not in st.session_state:
    st.session_state.theme = "light"

# ---------- SIDEBAR ----------
with st.sidebar:
    if st.button("🌓 Toggle Dark/Light Theme"):
        st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
        st.rerun()
    try:
        logo = Image.open("assets/doctor.jpg")
        st.image(logo, width=100)
    except:
        st.image("https://images.unsplash.com/photo-1531206715517-5c0ba140b2b8?w=100", width=80)
    st.markdown("## 🌸 AfyaChoice AI")
    st.markdown("---")
    st.markdown("📍 Kenyan FP Guidelines 2025")
    st.markdown("🏥 **County:** Nairobi (local resources available)")

# ---------- CSS FOR LIGHT/DARK THEMES ----------
if st.session_state.theme == "light":
    theme_css = """
        .stApp { background: linear-gradient(135deg, #FFF0F5 0%, #FFE4EC 100%); }
        [data-testid="stSidebar"] { background-color: #FFE4EC; }
        .rec-card { background-color: white; box-shadow: 0 4px 12px rgba(0,0,0,0.1); border-radius: 16px; padding: 20px; margin-bottom: 20px; }
        html, body, [class*="css"], label, .stRadio label, .stSelectbox label, .stMarkdown p, div[data-testid="stMarkdownContainer"] p {
            color: #1a1a1a !important;
            font-family: 'Segoe UI', 'Roboto', sans-serif;
        }
        input, textarea, select { color: #000000 !important; background-color: #ffffff !important; }
        .stButton > button { background-color: #0077be; color: white !important; border-radius: 30px; font-weight: bold; }
        h1, h2, h3 { color: #0056a7 !important; }
        .stInfo, .stSuccess, .stWarning { color: #1a1a1a !important; }
    """
else:
    theme_css = """
        .stApp { background-color: #1e1e2f; }
        [data-testid="stSidebar"] { background-color: #2a2a3b; }
        .rec-card { background-color: #2d2d44; border-radius: 16px; padding: 20px; margin-bottom: 20px; }
        html, body, [class*="css"], label, .stRadio label, .stSelectbox label, .stMarkdown p, div[data-testid="stMarkdownContainer"] p {
            color: #f0f0f0 !important;
            font-family: 'Segoe UI', 'Roboto', sans-serif;
        }
        input, textarea, select { color: #ffffff !important; background-color: #3a3a55 !important; }
        .stButton > button { background-color: #0077be; color: white !important; border-radius: 30px; font-weight: bold; }
        h1, h2, h3 { color: #FFB6C1 !important; }
        .stInfo, .stSuccess, .stWarning { color: #f0f0f0 !important; }
        .stInfo { background-color: #2a2a3b !important; }
    """
st.markdown(f"<style>{theme_css}</style>", unsafe_allow_html=True)

# ---------- MAIN TITLE & BANNER ----------
st.title("🌸 AfyaChoice AI – Family Planning Decision Support")
st.markdown("Based on **Kenyan FP Guidelines** + **WHO MEC** + **Your Preferences**")

try:
    banner = Image.open("assets/mother.jpg")
    st.image(banner, use_container_width=True)
except:
    pass

st.markdown("---")
st.subheader("📝 Your Health & Preference Profile")

# ---------- TWO‑COLUMN INPUT FORM ----------
col1, col2 = st.columns(2)

with col1:
    age_group = st.selectbox("Age group", ["Adolescent (15-19)", "Peak Reproductive (20-34)", "Advanced Maternal Age (35-49)"])
    edu = st.selectbox("Education", ["Primary", "Secondary", "Tertiary"])
    marital = st.selectbox("Marital status", ["Married", "Never married", "Other"])
    ever_pregnant = st.radio("Ever been pregnant?", ["No", "Yes"])
    sti_risk = st.radio("At risk of STI / have an STI?", ["No", "Yes"])
    county = st.selectbox("Your county", [
        "Nairobi", "Mombasa", "Kisumu", "Nakuru", "Kiambu", "Machakos", "Uasin Gishu",
        "Kakamega", "Bungoma", "Meru", "Kilifi", "Kitui", "Embu", "Turkana", "Wajir"
    ])

with col2:
    breastfeeding = st.radio("Currently breastfeeding?", ["No", "Yes"])
    migraine = st.radio("Do you get severe headaches that also affect your vision (seeing flashes, zigzag lines, or temporary blind spots)?", ["No", "Yes"])
    chronic_conditions = st.multiselect(
        "Do you have any of these chronic conditions? (Select all that apply)",
        ["Diabetes", "High blood pressure (hypertension)", "Cancer (any type)",
         "Mental health condition", "HIV", "Convulsion disorder (epilepsy)"]
    )
    next_child = st.radio("Plan next child?", ["Within 1 year", "1-3 years", "3+ years", "Not planning"])
    duration_pref = st.selectbox("Preferred method duration", ["Short-term (<1 year)", "Medium (1-3 years)", "Long-term (3+ years)", "No preference"])
    privacy_pref = st.selectbox(
        "What kind of method do you prefer?",
        ["No preference", "Prefers pills (may be less discreet)", "Prefers private methods (implant / IUD / injectable)"]
    )

# ---------- LOGISTIC PROBABILITY (inline) ----------
def logistic_probability(age, edu, marital, pregnant):
    logit = -2.88859684330198
    if age == "Peak Reproductive (20-34)":
        logit += 1.48142509663635
    elif age == "Advanced Maternal Age (35-49)":
        logit += 0.184368150894733
    if edu == "Primary":
        logit += 1.04198370847373
    elif edu == "Secondary":
        logit += 0.778263464783876
    if marital == "Other":
        logit += -1.35350229720388
    elif marital == "Never married":
        logit += -1.53204479549144
    if pregnant == "Yes":
        logit += 2.07691659640518
    return 1 / (1 + math.exp(-logit))

# ---------- RECOMMENDATION BUTTON ----------
if st.button("🌸 Get my recommendations", use_container_width=True):
    with st.spinner("Analyzing your profile..."):
        prob = logistic_probability(age_group, edu, marital, ever_pregnant)
        user_data = {
            "age_group_clinical": age_group,
            "edu_level": edu,
            "marital_status": marital,
            "ever_been_pregnant": ever_pregnant,
            "breastfeeding": breastfeeding,
            "migraine_aura": migraine,
            "sti_risk": sti_risk,
            "next_child": next_child,
            "duration_pref": duration_pref,
            "privacy_pref": privacy_pref,
            "chronic_conditions": chronic_conditions
        }
        top3 = rank_methods(user_data, privacy_pref)

    st.metric("📊 Hormonal suitability score", f"{prob:.0%}")
    if prob > 60:
        st.info("🔍 **Why?** Your profile suggests hormonal methods are often well‑tolerated.")
    elif prob < 40:
        st.info("🔍 **Why?** Your profile suggests non‑hormonal methods may be more suitable – shown below.")
    else:
        st.info("🔍 **Why?** Both hormonal and non‑hormonal options exist. We ranked by MEC safety and your preferences.")
    
    st.subheader("🌟 Your top 3 recommendations")
    for i, m in enumerate(top3, 1):
        st.markdown(f'<div class="rec-card">', unsafe_allow_html=True)
        st.markdown(f"### {i}. {m['name']} {'💊' if m['type']=='hormonal' else '🛡️'}")
        st.markdown(f"**Effectiveness (typical use):** {m['effectiveness']}%")
        st.markdown(f"**✅ Benefits:** {', '.join(m['benefits'])}")
        st.markdown(f"**⚠️ Side effects:** {', '.join(m['side_effects'])}")
        if 'explanation' in m:
            st.markdown(f"**📖 Why this method:** {m['explanation']}")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("---")
    
    # Pill reminder if a pill method is in top 3
    if any("Pill" in m['name'] for m in top3):
        st.subheader("💊 Pill reminder (optional)")
        reminder_date = st.date_input("Set daily reminder start date")
        if st.button("Add to Google Calendar"):
            start = reminder_date.strftime("%Y%m%dT100000")
            end = (reminder_date + datetime.timedelta(days=1)).strftime("%Y%m%dT100000")
            title = "Take your contraceptive pill"
            url = f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={title}&dates={start}/{end}"
            st.markdown(f"[Click here to add to Google Calendar]({url})", unsafe_allow_html=True)

st.markdown("---")
st.caption("🔒 Private & secure. This tool follows Kenyan FP guidelines and WHO MEC. Always consult a healthcare provider for final decisions.")
# v2.0 - calendar fix applied

