import streamlit as st
from PIL import Image
from recommend import rank_methods
from ml_model import hormonal_probability
import os
import datetime
import requests
import json
from functools import lru_cache

st.set_page_config(page_title="AfyaChoice AI", page_icon="🌸", layout="wide")

# Theme state
if "theme" not in st.session_state:
    st.session_state.theme = "light"

# ---------- Sidebar (moved chatbot here) ----------
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

    # ---------- Chatbot now in sidebar (left side) ----------
    st.markdown("---")
    st.subheader("💬 Ask Afya")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    # Show last few messages (compact)
    for msg in st.session_state.chat_history[-6:]:
        st.markdown(f"**{msg['role'].capitalize()}:** {msg['content'][:100]}...")
    user_question = st.text_input("Your question:", key="chat_input", placeholder="e.g., side effects of pills")

    # Simple in‑memory cache for identical questions
    @lru_cache(maxsize=100)
    def cached_groq_response(question):
        # Use the same API call logic but cached
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key and hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
            api_key = st.secrets["GROQ_API_KEY"]
        if not api_key:
            return None, "API key missing."
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": question}],
            "temperature": 0.7,
            "max_tokens": 500
        }
        try:
            resp = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=10)
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"], None
            else:
                return None, f"API error {resp.status_code}"
        except Exception as e:
            return None, str(e)

    # Fallback rule‑based answers for common questions when rate limited
    def fallback_answer(question):
        q = question.lower()
        if "side effect" in q and "pill" in q:
            return "Common side effects of contraceptive pills include nausea, breast tenderness, mood changes, headaches, and spotting. Most are mild and improve after a few months."
        elif "pregnancy" in q:
            return "Pregnancy has three trimesters. Regular prenatal care, folic acid, and avoiding harmful substances are key. Always consult a healthcare provider."
        elif "breastfeeding" in q:
            return "While breastfeeding, progestin‑only pills, implants, IUDs, and condoms are safe. Combined pills are not recommended."
        else:
            return "I'm sorry, I'm currently experiencing high demand. Please try again in a minute or rephrase your question."

    if user_question:
        st.session_state.chat_history.append({"role": "user", "content": user_question})
        # Try to get cached answer
        answer, error = cached_groq_response(user_question)
        if answer and "rate_limit" not in error.lower():
            bot_reply = answer
        else:
            # If rate limited or error, use fallback
            bot_reply = fallback_answer(user_question)
        st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
        st.rerun()

# ---------- CSS for professional medical look (unchanged) ----------
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

# ---------- Main content (Health profile, unchanged) ----------
st.markdown("---")
st.subheader("📝 Your Health & Preference Profile")

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
