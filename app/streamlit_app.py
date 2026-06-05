import streamlit as st
from recommend import rank_methods

st.set_page_config(page_title="AfyaChoice AI", page_icon="??", layout="wide")

# Pink theme + custom CSS
st.markdown("""
<style>
    .stApp { background-color: #FFF0F5; }
    .stButton > button { background-color: #FF69B4; color: white; border-radius: 10px; padding: 10px 24px; }
    .stButton > button:hover { background-color: #FF1493; }
    h1, h2, h3 { color: #C71585; }
    .rec-card { background-color: white; padding: 20px; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

# Sidebar: Team info
from PIL import Image   # make sure this is at the top of the file with other imports

# ... later in the sidebar:
logo = Image.open("app/assets/doctor.jpg")
st.sidebar.image(logo, width=100)
st.sidebar.markdown("## 🌸 AfyaChoice AI")
st.sidebar.markdown("---")
st.sidebar.markdown("📍 Kenyan FP Guidelines 2025")

st.title("?? AfyaChoice AI � Family Planning Decision Support")
banner = Image.open("app/assets/mother.jpg")
st.image(banner, use_container_width=True)
st.markdown("Based on **Kenyan FP Guidelines** + **WHO MEC** + **Your Preferences**")

# User input form
col1, col2 = st.columns(2)
with col1:
    age_group = st.selectbox("Age group", ["Adolescent (15-19)", "Peak Reproductive (20-34)", "Advanced Maternal Age (35-49)"])
    edu = st.selectbox("Education", ["Primary", "Secondary", "Tertiary"])
    marital = st.selectbox("Marital status", ["Married", "Never married", "Other"])
    ever_pregnant = st.radio("Ever been pregnant?", ["No", "Yes"])
with col2:
    breastfeeding = st.radio("Breastfeeding?", ["No", "Yes"])
    hypertension = st.radio("Hypertension?", ["No", "Yes"])
    migraine = st.radio("Migraine with aura?", ["No", "Yes"])
    preference = st.selectbox("Your preference", ["No preference", "Long-acting", "Short-term", "No hormones"])

if st.button("?? Get my recommendations"):
    with st.spinner("Analyzing..."):
        user_data = {
            "age_group_clinical": age_group,
            "edu_level": edu,
            "marital_status": marital,
            "ever_been_pregnant": ever_pregnant,
            "breastfeeding": breastfeeding,
            "hypertension": hypertension,
            "migraine_aura": migraine
        }
        top3 = rank_methods(user_data, preference)
    
    st.subheader("?? Your top 3 recommendations")
    for i, m in enumerate(top3, 1):
        with st.container():
            st.markdown(f'<div class="rec-card">', unsafe_allow_html=True)
            st.markdown(f"### {i}. {m['name']} {'??' if m['type']=='hormonal' else '???'}")
            st.markdown(f"**Effectiveness:** {m['effectiveness']}%")
            st.markdown(f"**? Benefits:** {', '.join(m['benefits'])}")
            st.markdown(f"**?? Side effects:** {', '.join(m['side_effects'])}")
            st.markdown('</div>', unsafe_allow_html=True)
