import streamlit as st
from PIL import Image
from recommend import rank_methods
from ml_model import hormonal_probability
import os
import datetime
from groq import Groq

st.set_page_config(page_title="AfyaChoice AI", page_icon="🌸", layout="wide")

# Theme state
if "theme" not in st.session_state:
    st.session_state.theme = "light"

# Sidebar
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

# CSS for professional medical look + theme
if st.session_state.theme == "light":
    theme_css = """
        .stApp { background: linear-gradient(135deg, #FFF0F5 0%, #FFE4EC 100%); }
        [data-testid="stSidebar"] { background-color: #FFE4EC; }
        .rec-card { background-color: white; box-shadow: 0 4px 12px rgba(0,0,0,0.1); border-radius: 16px; padding: 20px; margin-bottom: 20px; }
        html, body, [class*="css"], label, .stRadio label, .stSelectbox label, .stMarkdown p {
            color: #1a1a1a !important;
            font-family: 'Segoe UI', 'Roboto', sans-serif;
        }
        input, textarea, select { color: #000 !important; background-color: #fff !important; }
        .stButton > button { background-color: #0077be; color: white !important; border-radius: 30px; font-weight: bold; }
        h1, h2, h3 { color: #0056a7 !important; }
    """
else:
    theme_css = """
        .stApp { background-color: #1e1e2f; }
        [data-testid="stSidebar"] { background-color: #2a2a3b; }
        .rec-card { background-color: #2d2d44; border-radius: 16px; padding: 20px; margin-bottom: 20px; }
        html, body, [class*="css"], label, .stRadio label, .stSelectbox label, .stMarkdown p {
            color: #f0f0f0 !important;
            font-family: 'Segoe UI', 'Roboto', sans-serif;
        }
        input, textarea, select { color: #fff !important; background-color: #3a3a55 !important; }
        .stButton > button { background-color: #0077be; color: white !important; border-radius: 30px; }
        h1, h2, h3 { color: #FFB6C1 !important; }
    """
st.markdown(f"<style>{theme_css}</style>", unsafe_allow_html=True)

st.title("🌸 AfyaChoice AI – Family Planning Decision Support")
st.markdown("Based on **Kenyan FP Guidelines** + **WHO MEC** + **Your Preferences**")

try:
    banner = Image.open("assets/mother.jpg")
    st.image(banner, use_container_width=True)
except:
    pass

# ---------- Chatbot ----------
with st.expander("💬 Ask Afya – Your Family Planning Assistant", expanded=False):
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    for msg in st.session_state.chat_history:
        st.markdown(f"**{msg['role'].capitalize()}:** {msg['content']}")
        st.markdown("---")
    user_question = st.text_input("Your question:", key="chat_input")

    @st.cache_resource
    def get_groq_client():
        # Try environment variable first (local .env), then Streamlit secrets
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key and hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
            api_key = st.secrets["GROQ_API_KEY"]
        if not api_key:
            st.warning("⚠️ GROQ_API_KEY not found. Set it in Streamlit secrets or .env file.")
            return None
        return Groq(api_key=api_key)

    if user_question:
        st.session_state.chat_history.append({"role": "user", "content": user_question})
        client = get_groq_client()
        if client:
            try:
                system_prompt = "You are Afya, a Kenyan family planning assistant. Answer clearly and concisely about pregnancy, contraception, side effects, breastfeeding, STIs, emergency contraception, and WHO MEC guidelines. Keep answers 3-5 sentences."
                messages = [{"role": "system", "content": system_prompt}]
                for msg in st.session_state.chat_history[-12:]:
                    messages.append({"role": msg["role"], "content": msg["content"]})
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=500
                )
                bot_reply = response.choices[0].message.content
            except Exception as e:
                bot_reply = f"Error: {str(e)}. Please try again."
        else:
            bot_reply = "API key missing. Please add GROQ_API_KEY to Streamlit secrets."
        st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
        st.rerun()

st.markdown("---")
st.subheader("📝 Your Health & Preference Profile")

# Input form
col1, col2 = st.columns(2)
with col1:
    age_group = st.selectbox("Age group", ["Adolescent (15-19)", "Peak Reproductive (20-34)", "Advanced Maternal Age (35-49)"])
    edu = st.selectbox("Education", ["Primary", "Secondary", "Tertiary"])
    marital = st.selectbox("Marital status", ["Married", "Never married", "Other"])
    ever_pregnant = st.radio("Ever been pregnant?", ["No", "Yes"])
    sti_risk = st.radio("At risk of STI / have an STI?", ["No", "Yes"])
    cancer_history = st.selectbox("Cancer history", ["None", "Breast cancer", "Cervical cancer", "Other cancer"])
    county = st.selectbox("Your county", ["Nairobi", "Mombasa", "Kisumu", "Nakuru", "Kiambu", "Machakos", "Uasin Gishu", "Kakamega", "Bungoma", "Meru", "Kilifi", "Kitui", "Embu", "Turkana", "Wajir"])

with col2:
    breastfeeding = st.radio("Currently breastfeeding?", ["No", "Yes"])
    hypertension = st.radio("High blood pressure?", ["No", "Yes"])
    migraine = st.radio("Migraine with aura?", ["No", "Yes"])
    next_child = st.radio("Plan next child?", ["Within 1 year", "1-3 years", "3+ years", "Not planning"])
    duration_pref = st.selectbox("Preferred method duration", ["Short-term (<1 year)", "Medium (1-3 years)", "Long-term (3+ years)", "No preference"])
    preference = st.selectbox("Hormone preference", ["No preference", "Long-acting", "Short-term", "No hormones"])

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
    st.info("🔍 **Why?** Based on your age, pregnancy history, and medical conditions, this score reflects the likelihood that hormonal methods are suitable.")
    
    st.subheader("🌟 Your top 3 recommendations")
    for i, m in enumerate(top3, 1):
        st.markdown(f'<div class="rec-card">', unsafe_allow_html=True)
        st.markdown(f"### {i}. {m['name']} {'💊' if m['type']=='hormonal' else '🛡️'}")
        st.markdown(f"**Effectiveness:** {m['effectiveness']}%")
        st.markdown(f"**✅ Benefits:** {', '.join(m['benefits'])}")
        st.markdown(f"**⚠️ Side effects:** {', '.join(m['side_effects'])}")
        if 'explanation' in m:
            st.markdown(f"**📖 Why this method:** {m['explanation']}")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("---")
    
    if any("Pill" in m['name'] for m in top3):
        st.subheader("💊 Pill reminder")
        reminder_date = st.date_input("Set start date")
        if st.button("Add to Google Calendar"):
            start = reminder_date.strftime("%Y%m%dT100000")
            end = (reminder_date + datetime.timedelta(days=1)).strftime("%Y%m%dT100000")
            url = f"https://calendar.google.com/calendar/render?action=TEMPLATE&text=Take%20your%20pill&dates={start}/{end}"
            st.markdown(f"[Click to add to Google Calendar]({url})", unsafe_allow_html=True)

st.markdown("---")
st.caption("🔒 Private & secure. This tool uses Kenyan FP guidelines and WHO MEC. Always consult a healthcare provider.")
