import streamlit as st
from PIL import Image
from recommend import rank_methods
from ml_model import hormonal_probability
from dotenv import load_dotenv
import os
import datetime
from groq import Groq

load_dotenv()

st.set_page_config(page_title="AfyaChoice AI", page_icon="🌸", layout="wide")

# Theme state
if "theme" not in st.session_state:
    st.session_state.theme = "light"

with st.sidebar:
    if st.button("🌓 Toggle Dark/Light Theme"):
        st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
        st.rerun()

# Light/dark CSS (fixed contrast)
if st.session_state.theme == "light":
    theme_css = """
        .stApp { background-color: #FFF0F5; }
        [data-testid="stSidebar"] { background-color: #FFE4EC; }
        .rec-card { background-color: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        html, body, [class*="css"], label, .stRadio label, .stSelectbox label, .stMarkdown p, div[data-testid="stMarkdownContainer"] p, .stRadio div[role="radiogroup"] span, .stSelectbox div[data-baseweb="select"] span, .stDateInput label {
            color: #1a1a1a !important;
        }
        input, textarea, select {
            color: #000000 !important;
            background-color: #ffffff !important;
        }
        .stButton > button {
            background-color: #FF69B4;
            color: white !important;
        }
        h1, h2, h3, h4, h5, h6 { color: #C71585 !important; }
        .st-emotion-cache-16idsys p { color: #1a1a1a !important; }
    """
else:
    theme_css = """
        .stApp { background-color: #1e1e2f; }
        [data-testid="stSidebar"] { background-color: #2a2a3b; }
        .rec-card { background-color: #2d2d44; box-shadow: 0 2px 4px rgba(255,255,255,0.1); }
        html, body, [class*="css"], label, .stRadio label, .stSelectbox label, .stMarkdown p, div[data-testid="stMarkdownContainer"] p, .stRadio div[role="radiogroup"] span, .stSelectbox div[data-baseweb="select"] span, .stDateInput label {
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

# Sidebar (logo unchanged)
with st.sidebar:
    try:
        logo = Image.open("assets/doctor.jpg")
        st.image(logo, width=100)
    except:
        st.image("https://images.unsplash.com/photo-1531206715517-5c0ba140b2b8?w=100", width=80)
    st.markdown("## 🌸 AfyaChoice AI")
    st.markdown("---")
    st.markdown("📍 Kenyan FP Guidelines 2025")

st.title("🌸 AfyaChoice AI – Family Planning Decision Support")
st.markdown("Based on **Kenyan FP Guidelines** + **WHO MEC** + **Your Preferences**")

try:
    banner = Image.open("assets/mother.jpg")
    st.image(banner, use_container_width=True)
except:
    pass

# ============================================
# CHATBOT with Groq (real LLM)
# ============================================
with st.expander("💬 Ask Afya (FAQ Bot) - Ask anything about family planning"):
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['content']}")
        else:
            st.markdown(f"**Afya:** {msg['content']}")
        st.markdown("---")
    
    user_question = st.text_input("Your question:", key="chat_input")
    
    # Groq client (cached)
    @st.cache_resource
    def get_groq_client():
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            st.warning("GROQ_API_KEY not found. Please add it to .env file or Streamlit secrets.")
            return None
        return Groq(api_key=api_key)
    
    if user_question:
        st.session_state.chat_history.append({"role": "user", "content": user_question})
        client = get_groq_client()
        if client:
            try:
                # Prepare conversation context
                messages = [
                    {"role": "system", "content": "You are Afya, a friendly and knowledgeable assistant for family planning in Kenya. Answer questions about contraception, WHO MEC guidelines, pregnancy, STIs, breastfeeding, side effects, emergency contraception, cancer history, and method duration. Keep answers clear, concise (2-3 sentences), and medically accurate. If unsure, suggest consulting a healthcare provider."}
                ]
                # Add last 5 exchanges for context (avoid token overload)
                for msg in st.session_state.chat_history[-10:]:
                    messages.append({"role": msg["role"], "content": msg["content"]})
                
                chat_completion = client.chat.completions.create(
                    messages=messages,
                    model="llama-3.3-70b-versatile",
                    temperature=0.7,
                    max_tokens=500,
                )
                bot_reply = chat_completion.choices[0].message.content
            except Exception as e:
                bot_reply = f"I'm sorry, I'm having trouble right now. Error: {str(e)}. Please try again later."
        else:
            bot_reply = "I need a valid API key to work. Please set GROQ_API_KEY in your environment."
        st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
        st.rerun()

# ============================================
# User input form (unchanged, all fields)
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
    
    # Pill reminder
    if any("Pill" in m['name'] for m in top3):
        st.subheader("💊 Pill reminder (optional)")
        reminder_date = st.date_input("Set a daily reminder start date")
        if st.button("Add to Google Calendar"):
            start = reminder_date.strftime("%Y%m%dT100000")
            end = (reminder_date + datetime.timedelta(days=1)).strftime("%Y%m%dT100000")
            title = "Take your contraceptive pill"
            url = f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={title}&dates={start}/{end}"
            st.markdown(f"[Click here to add to Google Calendar]({url})", unsafe_allow_html=True)
