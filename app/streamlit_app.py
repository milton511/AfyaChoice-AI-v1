import streamlit as st
from PIL import Image
from recommend import rank_methods
from ml_model import hormonal_probability

st.set_page_config(page_title="AfyaChoice AI", page_icon="🌸", layout="wide")

# ============================================
# CSS with improved text contrast
# ============================================
st.markdown("""
<style>
    .stApp {
        background-color: #FFF0F5;
    }
    html, body, [class*="css"] {
        color: #2d2d2d !important;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #C71585 !important;
    }
    .stButton > button {
        background-color: #FF69B4;
        color: white !important;
        border-radius: 10px;
        padding: 10px 24px;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #FF1493;
        color: white !important;
    }
    [data-testid="stSidebar"] {
        background-color: #FFE4EC;
    }
    [data-testid="stSidebar"] * {
        color: #1a1a1a !important;
    }
    .rec-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        color: #000000 !important;
    }
    .rec-card * {
        color: #000000 !important;
    }
    label, .stRadio label, .stSelectbox label, .stMarkdown p {
        color: #2d2d2d !important;
    }
    input, textarea, select {
        color: #000000 !important;
        background-color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# Sidebar with local logo
# ============================================
with st.sidebar:
    try:
        logo = Image.open("assets/doctor.jpg")
        st.image(logo, width=100)
    except:
        st.image("https://images.unsplash.com/photo-1531206715517-5c0ba140b2b8?w=100", width=80)
    st.markdown("## 🌸 AfyaChoice AI")
    st.markdown("---")
    st.markdown("📍 Kenyan FP Guidelines 2025")

# ============================================
# Main title
# ============================================
st.title("🌸 AfyaChoice AI – Family Planning Decision Support")
st.markdown("Based on **Kenyan FP Guidelines** + **WHO MEC** + **Your Preferences**")

# ============================================
# Optional banner image
# ============================================
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
with col2:
    breastfeeding = st.radio("Breastfeeding?", ["No", "Yes"])
    hypertension = st.radio("Hypertension?", ["No", "Yes"])
    migraine = st.radio("Migraine with aura?", ["No", "Yes"])
    preference = st.selectbox("Your preference", ["No preference", "Long-acting", "Short-term", "No hormones"])

# ============================================
# Prediction button
# ============================================
if st.button("🌸 Get my recommendations", use_container_width=True):
    with st.spinner("Analyzing your profile..."):
        # Calculate probability directly from model
        prob = hormonal_probability(age_group, edu, marital, ever_pregnant)
        
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

    # Display probability metric
    st.metric("📊 Hormonal suitability score", f"{prob:.0%}")
    
    st.subheader("🌟 Your top 3 recommendations")
    for i, m in enumerate(top3, 1):
        st.markdown(f'<div class="rec-card">', unsafe_allow_html=True)
        st.markdown(f"### {i}. {m['name']} {'💊' if m['type']=='hormonal' else '🛡️'}")
        st.markdown(f"**Effectiveness (typical use):** {m['effectiveness']}%")
        st.markdown(f"**✅ Benefits:** {', '.join(m['benefits'])}")
        st.markdown(f"**⚠️ Side effects:** {', '.join(m['side_effects'])}")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("---")
