import streamlit as st
from PIL import Image
from recommend import rank_methods
from ml_model import hormonal_probability

st.set_page_config(page_title="AfyaChoice AI", page_icon="🌸", layout="wide")

# Theme state
if "theme" not in st.session_state:
    st.session_state.theme = "light"

# Chatbot messages
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

# Simple FAQ responses
def chatbot_response(question):
    q = question.lower()
    if "breastfeeding" in q and ("pill" in q or "hormonal" in q):
        return "Progestin-only pills are safe during breastfeeding. Avoid combined pills."
    elif "iud" in q and "pain" in q:
        return "Some cramping is normal after IUD insertion. Use ibuprofen if needed."
    elif "side effect" in q:
        return "Side effects vary by method. Common ones include irregular bleeding, headaches, or mood changes."
    elif "effectiveness" in q:
        return "Implant and IUD are >99% effective. Condoms are about 85% with typical use."
    elif "emergency" in q:
        return "Emergency contraceptive pills (ECPs) or Copper IUD can be used up to 5 days after unprotected sex."
    elif "cancer" in q:
        return "Hormonal methods may not be recommended if you have a history of breast cancer."
    else:
        return "Please ask about specific methods, side effects, breastfeeding, or emergency contraception."

# Theme toggle
with st.sidebar:
    if st.button("🌓 Toggle Dark/Light Theme"):
        st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
        st.rerun()
    st.markdown("---")
    try:
        logo = Image.open("assets/doctor.jpg")
        st.image(logo, width=100)
    except:
        st.image("https://images.unsplash.com/photo-1531206715517-5c0ba140b2b8?w=100", width=80)
    st.markdown("## 🌸 AfyaChoice AI")
    st.markdown("📍 Kenyan FP Guidelines 2025")
    st.markdown("---")
    
    # Chatbot section
    st.markdown("### 💬 Ask Afya (FAQ Bot)")
    user_question = st.text_input("Your question:", key="chat_input")
    if st.button("Ask", key="ask_btn"):
        if user_question:
            answer = chatbot_response(user_question)
            st.session_state.chat_messages.append(("You", user_question))
            st.session_state.chat_messages.append(("Afya", answer))
    for speaker, msg in st.session_state.chat_messages[-10:]:
        st.markdown(f"**{speaker}:** {msg}")

# ============================================
# CSS – high contrast light theme fix
# ============================================
if st.session_state.theme == "light":
    theme_css = """
        .stApp { background-color: #FFF0F5; }
        [data-testid="stSidebar"] { background-color: #FFE4EC; }
        .rec-card { background-color: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        html, body, [class*="css"] { color: #000000 !important; }
        .stRadio label, .stSelectbox label, .stMarkdown p, label {
            color: #000000 !important;
            font-weight: 500 !important;
        }
        .stRadio div[role="radiogroup"] label, .stSelectbox div[data-baseweb="select"] {
            color: #000000 !important;
            background-color: #ffffff !important;
        }
        input, textarea, select {
            color: #000000 !important;
            background-color: #ffffff !important;
            border: 1px solid #cccccc !important;
        }
        .stButton > button {
            background-color: #FF69B4;
            color: white !important;
        }
        h1, h2, h3, h4, h5, h6 { color: #C71585 !important; }
    """
else:
    theme_css = """
        .stApp { background-color: #1e1e2f; }
        [data-testid="stSidebar"] { background-color: #2a2a3b; }
        .rec-card { background-color: #2d2d44; box-shadow: 0 2px 4px rgba(255,255,255,0.1); }
        html, body, [class*="css"], label, .stRadio label, .stSelectbox label, .stMarkdown p {
            color: #f0f0f0 !important;
        }
        input, textarea, select {
            color: #ffffff !important;
            background-color: #3a3a55 !important;
        }
        .stButton > button {
            background-color: #FF69B4;
            color: white !important;
        }
        h1, h2, h3, h4, h5, h6 { color: #FFB6C1 !important; }
        .stRadio div[role="radiogroup"] label, .stSelectbox div[data-baseweb="select"] {
            color: white !important;
        }
    """

st.markdown(f"<style>{theme_css}</style>", unsafe_allow_html=True)

st.title("🌸 AfyaChoice AI – Family Planning Decision Support")
st.markdown("Based on **Kenyan FP Guidelines** + **WHO MEC** + **Your Preferences**")

try:
    banner = Image.open("assets/mother.jpg")
    st.image(banner, use_container_width=True)
except:
    pass

# ============================================
# User input form
# ============================================
col1, col2 = st.columns(2)
with col1:
    age_group = st.selectbox("Age group", ["Adolescent (15-19)", "Peak Reproductive (20-34)", "Advanced Maternal Age (35-49)"])
    edu = st.selectbox("Education", ["Primary", "Secondary", "Tertiary"])
    marital = st.selectbox("Marital status", ["Married", "Never married", "Other"])
    ever_pregnant = st.radio("Ever been pregnant?", ["No", "Yes"])
    sti_risk = st.radio("Are you at risk of STI / have an STI?", ["No", "Yes"])
    cancer_history = st.selectbox("Cancer history (affects hormonal methods)", ["None", "Breast cancer", "Cervical cancer", "Other cancer"])

with col2:
    breastfeeding = st.radio("Currently breastfeeding?", ["No", "Yes"])
    hypertension = st.radio("High blood pressure?", ["No", "Yes"])
    migraine = st.radio("Migraine with aura?", ["No", "Yes"])
    next_child = st.radio("When do you plan your next child?", ["Within 1 year", "1-3 years", "3+ years", "Not planning"])
    duration_pref = st.selectbox("Preferred method duration", ["Short-term (<1 year)", "Medium (1-3 years)", "Long-term (3+ years)", "No preference"])
    preference = st.selectbox("Your preference (hormones vs non-hormones)", ["No preference", "Long-acting", "Short-term", "No hormones"])

# ============================================
# Prediction button
# ============================================
if st.button("🌸 Get my recommendations", use_container_width=True):
    with st.spinner("Analyzing your profile..."):
        prob = hormonal_probability(age_group, edu, marital, ever_pregnant)
        user_data = {
            "age_group_clinical": age_group,
            "edu_level": edu,
            "marital_status": marital,
            "ever_been_pregnant": ever_pregnant,
            "breastfeeding": breastfeeding,
            "hypertension": hypertension,
            "migraine_aura": migraine,
            "sti_risk": sti_risk,
            "cancer_history": cancer_history,
            "next_child": next_child,
            "duration_pref": duration_pref
        }
        top3 = rank_methods(user_data, preference)

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
    
    # Pill reminder demo
    if any("Pill" in m['name'] for m in top3):
        st.subheader("💊 Pill reminder (optional)")
        reminder_date = st.date_input("Set a daily reminder start date")
        if st.button("Add to Google Calendar"):
            import datetime
            start = reminder_date.strftime("%Y%m%dT100000")
            end = (reminder_date + datetime.timedelta(days=1)).strftime("%Y%m%dT100000")
            title = "Take your contraceptive pill"
            url = f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={title}&dates={start}/{end}"
            st.markdown(f"[Click here to add to Google Calendar]({url})", unsafe_allow_html=True)
