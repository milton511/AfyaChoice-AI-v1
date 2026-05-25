"""
AfyaChoice AI - Family Planning Decision Support System
Kenya FP Guidelines 7th Edition (2025) | WHO MEC
Production Version with Medical Images
"""

import streamlit as st
import time
from datetime import datetime
from pathlib import Path
import base64
from urllib.request import urlopen

# Page configuration
st.set_page_config(
    page_title="AfyaChoice AI | Family Planning Decision Support",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Helper function to get base64 encoded image from URL
def get_image_base64(url):
    try:
        with urlopen(url) as response:
            return base64.b64encode(response.read()).decode()
    except:
        return ""

# Free medical images from Unsplash/CDC/WHO (open source)
# Using reliable free image CDNs
WOMAN_IMAGE = "https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?w=400&h=300&fit=crop"
DOCTOR_IMAGE = "https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=400&h=300&fit=crop"
COUNSELING_IMAGE = "https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=400&h=300&fit=crop"
HEALTHCARE_IMAGE = "https://images.unsplash.com/photo-1584515933487-779824d29309?w=400&h=300&fit=crop"
FAMILY_IMAGE = "https://images.unsplash.com/photo-1543269865-cbf427effbad?w=400&h=300&fit=crop"
IUD_IMAGE = "https://cdn.pixabay.com/photo/2020/06/29/12/09/contraceptive-5353110_640.png"
IMPLANT_IMAGE = "https://cdn.pixabay.com/photo/2020/06/29/12/10/contraceptive-5353117_640.png"
PILLS_IMAGE = "https://cdn.pixabay.com/photo/2016/11/29/06/18/medicine-1867768_640.png"
CONDOM_IMAGE = "https://cdn.pixabay.com/photo/2016/04/02/22/42/condom-1303545_640.png"

# Custom CSS for professional UI with image support
st.markdown("""
<style>
    /* Main container */
    .main-header {
        background: linear-gradient(135deg, #0D47A1 0%, #1565C0 50%, #1976D2 100%);
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 30px;
        text-align: center;
        color: white;
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('https://images.unsplash.com/photo-1579684385127-1ef15d508118?w=1200&h=400&fit=crop') no-repeat center center;
        background-size: cover;
        opacity: 0.1;
        z-index: 0;
    }
    
    .main-header h1, .main-header p, .main-header small {
        position: relative;
        z-index: 1;
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 600;
    }
    
    .main-header p {
        margin: 10px 0 0;
        opacity: 0.9;
        font-size: 1rem;
    }
    
    .main-header small {
        font-size: 0.8rem;
        opacity: 0.7;
    }
    
    /* Card styling with image support */
    .recommendation-card {
        background: white;
        border-radius: 16px;
        padding: 24px;
        margin: 16px 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border-left: 5px solid #1565C0;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        position: relative;
        overflow: hidden;
    }
    
    .recommendation-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }
    
    /* Image container */
    .method-image {
        width: 60px;
        height: 60px;
        border-radius: 30px;
        background: #E3F2FD;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 20px;
        float: left;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #1565C0 0%, #0D47A1 100%);
        color: white;
        border: none;
        padding: 12px 28px;
        font-weight: 600;
        border-radius: 30px;
        width: 100%;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        transform: scale(1.02);
        background: linear-gradient(135deg, #0D47A1 0%, #0A3D8F 100%);
        box-shadow: 0 4px 15px rgba(21,101,192,0.3);
    }
    
    /* Step indicator */
    .step-container {
        display: flex;
        justify-content: space-between;
        margin-bottom: 40px;
        background: #f5f5f5;
        border-radius: 50px;
        padding: 8px;
    }
    
    .step {
        flex: 1;
        text-align: center;
        padding: 10px;
        border-radius: 40px;
        transition: all 0.3s ease;
        font-size: 14px;
        font-weight: 500;
    }
    
    .step-active {
        background: #1565C0;
        color: white;
        font-weight: 600;
    }
    
    .step-completed {
        background: #4CAF50;
        color: white;
    }
    
    .step-inactive {
        background: transparent;
        color: #757575;
    }
    
    /* Effectiveness meter */
    .effectiveness-bar {
        background: #E0E0E0;
        border-radius: 10px;
        height: 24px;
        overflow: hidden;
        margin: 12px 0;
    }
    
    .effectiveness-fill {
        background: linear-gradient(90deg, #FF9800, #4CAF50);
        height: 100%;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: flex-end;
        padding-right: 12px;
        color: white;
        font-weight: 600;
        font-size: 12px;
    }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin-right: 8px;
        margin-bottom: 8px;
    }
    
    .badge-larc {
        background: #E3F2FD;
        color: #1565C0;
    }
    
    .badge-hormonal {
        background: #F3E5F5;
        color: #7B1FA2;
    }
    
    .badge-non-hormonal {
        background: #E8F5E9;
        color: #2E7D32;
    }
    
    .badge-barrier {
        background: #FFF3E0;
        color: #E65100;
    }
    
    /* Myth card */
    .myth-card {
        background: #FFF8E1;
        border-radius: 12px;
        padding: 16px;
        margin: 12px 0;
        border-left: 4px solid #FF9800;
    }
    
    /* Info box */
    .info-box {
        background: #E8EAF6;
        border-radius: 12px;
        padding: 16px;
        margin: 16px 0;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 24px;
        margin-top: 40px;
        border-top: 1px solid #E0E0E0;
        font-size: 12px;
        color: #757575;
    }
    
    /* Progress bar */
    .progress-container {
        background: #E0E0E0;
        border-radius: 10px;
        height: 6px;
        margin: 20px 0;
    }
    
    .progress-fill {
        background: linear-gradient(90deg, #1565C0, #42A5F5);
        border-radius: 10px;
        height: 6px;
        transition: width 0.3s ease;
    }
    
    /* Image row for welcome section */
    .image-row {
        display: flex;
        justify-content: space-between;
        margin: 20px 0;
        gap: 15px;
    }
    
    .image-card {
        flex: 1;
        background: white;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .image-card img {
        width: 100%;
        height: 120px;
        object-fit: cover;
        border-radius: 8px;
    }
    
    .image-card p {
        margin-top: 10px;
        font-size: 12px;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DATA (Embedded for clean deployment)
# ============================================================================

COUNTY_CONTEXT = {
    "default": {
        "access_notes": "Family planning services available at public health facilities across Kenya.",
        "partner_dynamics": "Partner involvement varies. You can access services independently.",
        "common_myths": ["infertility", "weight_gain", "religion"]
    },
    "nairobi": {
        "access_notes": "Wide access across the city. Public facilities, private clinics, and pharmacies available.",
        "partner_dynamics": "Women can access services independently. Many clinics offer confidential services.",
        "common_myths": ["infertility", "weight_gain", "side_effects"]
    },
    "garissa": {
        "access_notes": "Services at Garissa Referral Hospital and mobile clinics. Community health workers available.",
        "partner_dynamics": "Discussing family planning with your husband may be helpful. Female providers available.",
        "common_myths": ["infertility", "religion", "only_for_married"]
    },
    "kisumu": {
        "access_notes": "Good access at Jaramogi Oginga Odinga Teaching and Referral Hospital.",
        "partner_dynamics": "Mix of independent and partner-involved care. Youth-friendly centers available.",
        "common_myths": ["infertility", "side_effects", "weight_gain"]
    },
    "mombasa": {
        "access_notes": "Services at Coast General Hospital, private clinics, and pharmacies.",
        "partner_dynamics": "Increasing independent access. Confidential services available.",
        "common_myths": ["infertility", "cancer", "ec_is_abortion"]
    }
}

METHODS = {
    "copper_iud": {
        "name": "Copper IUD", "type": "long_acting_reversible", "hormonal": False,
        "effectiveness": 99, "advantages": ["No hormones", "Works immediately", "Effective for 10 years", "Reversible"],
        "side_effects": ["Heavier periods", "More cramping first 3-6 months"],
        "questions": ["Will insertion be painful?", "How do I check strings?"],
        "image": IUD_IMAGE
    },
    "hormonal_iud": {
        "name": "Hormonal IUD", "type": "long_acting_reversible", "hormonal": True,
        "effectiveness": 99, "advantages": ["Lighter periods", "Less cramping", "Effective for 5 years"],
        "side_effects": ["Irregular bleeding first 3-6 months", "Headaches", "Breast tenderness"],
        "questions": ["Will I gain weight?", "How is it inserted?"],
        "image": IUD_IMAGE
    },
    "implant": {
        "name": "Implant", "type": "long_acting_reversible", "hormonal": True,
        "effectiveness": 99, "advantages": ["Highly effective", "Discreet", "No daily action", "Works for 3-5 years"],
        "side_effects": ["Irregular bleeding", "Headaches", "Weight gain possible", "Mood changes"],
        "questions": ["Can I feel it under my skin?", "How is it removed?"],
        "image": IMPLANT_IMAGE
    },
    "injectable": {
        "name": "Injectable", "type": "short_acting", "hormonal": True,
        "effectiveness": 94, "advantages": ["Private", "Every 3 months", "No daily pill", "May stop periods"],
        "side_effects": ["Weight gain common", "Delayed return to fertility", "Irregular bleeding"],
        "questions": ["When will my periods return?", "Do I need calcium supplements?"],
        "image": PILLS_IMAGE
    },
    "combined_pill": {
        "name": "Combined Pill", "type": "short_acting", "hormonal": True,
        "effectiveness": 91, "advantages": ["Regulates periods", "Less cramping", "Lighter periods", "May improve acne"],
        "side_effects": ["Nausea first months", "Headaches", "Breast tenderness", "Blood clot risk (rare)"],
        "questions": ["What if I miss a pill?", "Does it interact with other medications?"],
        "image": PILLS_IMAGE
    },
    "progestin_pill": {
        "name": "Progestin-Only Pill", "type": "short_acting", "hormonal": True,
        "effectiveness": 91, "advantages": ["Safe while breastfeeding", "No estrogen side effects", "Can use with migraines"],
        "side_effects": ["Irregular bleeding", "Headaches", "Breast tenderness", "Mood changes"],
        "questions": ["Same time every day required?", "What if I am late?"],
        "image": PILLS_IMAGE
    },
    "male_condom": {
        "name": "Male Condom", "type": "barrier", "hormonal": False,
        "effectiveness": 82, "advantages": ["STI protection including HIV", "No hormones", "No prescription needed"],
        "side_effects": ["Reduced sensation possible", "Latex allergy possible"],
        "questions": ["Are they free at government clinics?", "What lubricant is safe?"],
        "image": CONDOM_IMAGE
    },
    "female_condom": {
        "name": "Female Condom", "type": "barrier", "hormonal": False,
        "effectiveness": 79, "advantages": ["STI protection", "Woman-controlled", "No hormones", "Insert hours before sex"],
        "side_effects": ["Can be noisy", "Requires practice"],
        "questions": ["Where can I find these?", "How do I insert correctly?"],
        "image": CONDOM_IMAGE
    },
    "lam": {
        "name": "Lactational Amenorrhea Method", "type": "behavioral", "hormonal": False,
        "effectiveness": 98, "advantages": ["No cost", "No hormones", "No side effects", "Works with exclusive breastfeeding"],
        "side_effects": ["Requires exclusive breastfeeding", "Only works for first 6 months"],
        "questions": ["When should I switch to another method?"],
        "image": FAMILY_IMAGE
    },
    "nfp": {
        "name": "Natural Family Planning", "type": "behavioral", "hormonal": False,
        "effectiveness": 76, "advantages": ["No hormones", "No cost", "No side effects", "Acceptable to all religions"],
        "side_effects": ["Requires daily tracking", "Less effective for irregular cycles", "No STI protection"],
        "questions": ["How do I track ovulation accurately?", "Is there an app to help?"],
        "image": FAMILY_IMAGE
    }
}

MYTHS = {
    "infertility": {
        "myth": "Modern contraceptives cause permanent infertility",
        "evidence": "No scientific evidence shows contraceptives cause permanent infertility. Fertility returns when you stop using contraception."
    },
    "weight_gain": {
        "myth": "Contraceptives cause permanent weight gain",
        "evidence": "Only the injectable is clearly linked to weight gain of about 2-5 kg over 1-2 years. This weight is not permanent."
    },
    "religion": {
        "myth": "Family planning is against my religion",
        "evidence": "Most major religions including Christianity and Islam allow family planning for health and well-being of the family."
    },
    "only_for_married": {
        "myth": "Family planning is only for married women",
        "evidence": "Family planning is for all sexually active women regardless of marital status."
    },
    "future_pregnancy": {
        "myth": "Family planning will permanently stop me from having children",
        "evidence": "This is false except for sterilization. All other methods are reversible."
    },
    "side_effects": {
        "myth": "All side effects mean the method is dangerous for me",
        "evidence": "Most side effects are normal and temporary as your body adjusts to hormones."
    },
    "cancer": {
        "myth": "Contraceptives cause cancer",
        "evidence": "Hormonal contraceptives reduce risk of ovarian and endometrial cancer."
    },
    "ec_is_abortion": {
        "myth": "Emergency contraception is the abortion pill",
        "evidence": "Emergency contraception PREVENTS pregnancy. It cannot end an existing pregnancy."
    }
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_badge_class(method_type, hormonal):
    badges = []
    if method_type == "long_acting_reversible":
        badges.append('<span class="badge badge-larc">Long-Acting Reversible</span>')
    elif method_type == "short_acting":
        badges.append('<span class="badge">Short-Acting</span>')
    elif method_type == "barrier":
        badges.append('<span class="badge badge-barrier">Barrier Method</span>')
    elif method_type == "behavioral":
        badges.append('<span class="badge">Behavioral Method</span>')
    
    if hormonal:
        badges.append('<span class="badge badge-hormonal">Hormonal</span>')
    else:
        badges.append('<span class="badge badge-non-hormonal">Non-Hormonal</span>')
    
    return "".join(badges)


def calculate_recommendations(user_data):
    recommendations = []
    wants_long_term = user_data.get("wants_long_term", False)
    needs_privacy = user_data.get("needs_privacy", False)
    wants_non_hormonal = user_data.get("wants_non_hormonal", False)
    wants_std_protection = user_data.get("wants_std_protection", False)
    difficulty_remembering = user_data.get("difficulty_remembering_daily", False)
    religious_concerns = user_data.get("religious_concerns", False)
    
    for method_id, method in METHODS.items():
        score = 50
        
        if wants_long_term and method["type"] == "long_acting_reversible":
            score += 20
        if needs_privacy and method["type"] == "long_acting_reversible":
            score += 15
        if wants_non_hormonal and not method["hormonal"]:
            score += 15
        if wants_std_protection and method["type"] == "barrier":
            score += 25
        if difficulty_remembering and method["type"] in ["long_acting_reversible", "short_acting"]:
            score += 15
        if religious_concerns and not method["hormonal"]:
            score += 20
        
        score += method["effectiveness"] / 2
        
        recommendations.append({
            "method_id": method_id,
            "name": method["name"],
            "type": method["type"],
            "effectiveness": method["effectiveness"],
            "hormonal": method["hormonal"],
            "score": score,
            "advantages": method["advantages"][:3],
            "side_effects": method["side_effects"][:3],
            "questions": method["questions"][:3],
            "image": method.get("image", "")
        })
    
    recommendations.sort(key=lambda x: x["score"], reverse=True)
    return recommendations


def show_step_indicator(current_step):
    steps = ["Profile", "Health Screening", "Preferences", "Results"]
    step_container = '<div class="step-container">'
    
    for i, step in enumerate(steps, 1):
        if i < current_step:
            status = "step-completed"
            icon = "✓"
        elif i == current_step:
            status = "step-active"
            icon = str(i)
        else:
            status = "step-inactive"
            icon = str(i)
        
        step_container += f'<div class="step {status}">{icon} {step}</div>'
    
    step_container += '</div>'
    st.markdown(step_container, unsafe_allow_html=True)


# ============================================================================
# MAIN APP
# ============================================================================

def main():
    # Header with background image
    st.markdown("""
        <div class="main-header">
            <h1>AfyaChoice AI</h1>
            <p>AI-Assisted Family Planning Counselling & Decision Support System</p>
            <small>Based on Kenya FP Guidelines 7th Edition (2025) | WHO Medical Eligibility Criteria</small>
        </div>
    """, unsafe_allow_html=True)
    
    # Image row for visual appeal (only on first page)
    if st.session_state.get("step", 1) == 1:
        st.markdown("""
            <div class="image-row">
                <div class="image-card">
                    <img src="https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?w=200&h=120&fit=crop" alt="Women's health">
                    <p>Informed Decisions</p>
                </div>
                <div class="image-card">
                    <img src="https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=200&h=120&fit=crop" alt="Healthcare provider">
                    <p>Expert Guidance</p>
                </div>
                <div class="image-card">
                    <img src="https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=200&h=120&fit=crop" alt="Counseling">
                    <p>Quality Counseling</p>
                </div>
                <div class="image-card">
                    <img src="https://images.unsplash.com/photo-1543269865-cbf427effbad?w=200&h=120&fit=crop" alt="Family">
                    <p>Family Wellbeing</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Initialize session state
    if "step" not in st.session_state:
        st.session_state.step = 1
    if "user_data" not in st.session_state:
        st.session_state.user_data = {}
    if "recommendations" not in st.session_state:
        st.session_state.recommendations = None
    
    # Progress bar
    progress_width = ((st.session_state.step - 1) / 3) * 100
    st.markdown(f"""
        <div class="progress-container">
            <div class="progress-fill" style="width: {progress_width}%;"></div>
        </div>
    """, unsafe_allow_html=True)
    
    show_step_indicator(st.session_state.step)
    
    # Step 1: Basic Profile
    if st.session_state.step == 1:
        st.markdown("### Personal Information")
        st.markdown("This helps us understand your context better.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            age = st.number_input("Age", min_value=15, max_value=55, value=25, step=1)
            county = st.selectbox("County", ["Nairobi", "Garissa", "Kisumu", "Mombasa", "Kakamega", "Kiambu", "Nakuru", "Other"])
            children = st.number_input("Number of children", min_value=0, max_value=10, value=1, step=1)
        
        with col2:
            marital_status = st.selectbox("Marital Status", ["Married", "Single", "Living together", "Divorced", "Widowed"])
            education = st.selectbox("Education Level", ["None", "Primary", "Secondary", "College", "University"])
            partner_involved = st.radio("Partner involved in family planning decisions?", ["Yes", "No", "Sometimes"])
        
        if st.button("Continue", type="primary"):
            with st.spinner("Saving your information..."):
                time.sleep(0.5)
                st.session_state.user_data.update({
                    "age": age,
                    "county": county.lower(),
                    "children": children,
                    "marital_status": marital_status,
                    "education": education,
                    "partner_involved": partner_involved
                })
                st.session_state.step = 2
                st.rerun()
    
    # Step 2: Health Screening
    elif st.session_state.step == 2:
        st.markdown("### Health Screening")
        st.markdown("These questions help us recommend safe methods based on Kenya FP Guidelines.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            pregnant = st.radio("Are you currently pregnant?", ["No", "Yes"])
            breastfeeding = st.radio("Are you currently breastfeeding?", ["No", "Yes"])
            if breastfeeding == "Yes":
                weeks_postpartum = st.slider("Weeks since delivery", 0, 52, 6)
            else:
                weeks_postpartum = 100
            smoker = st.radio("Do you smoke?", ["No", "Yes"])
            migraine_aura = st.radio("Do you have migraines with aura?", ["No", "Yes"])
        
        with col2:
            blood_clots = st.radio("History of blood clots?", ["No", "Yes"])
            breast_cancer = st.radio("Current or past breast cancer?", ["No", "Yes"])
            pelvic_infection = st.radio("Current pelvic infection?", ["No", "Yes"])
            heavy_bleeding = st.radio("Heavy menstrual bleeding?", ["No", "Yes"])
            hypertension = st.radio("High blood pressure (BP over 160/100)?", ["No", "Yes"])
            liver_disease = st.radio("Severe liver disease?", ["No", "Yes"])
        
        if st.button("Check Safety", type="primary"):
            with st.spinner("Applying Kenya FP Guidelines safety rules..."):
                time.sleep(0.8)
                st.session_state.user_data.update({
                    "pregnant": pregnant == "Yes",
                    "breastfeeding": breastfeeding == "Yes",
                    "weeks_postpartum": weeks_postpartum if breastfeeding == "Yes" else 100,
                    "smoker": smoker == "Yes",
                    "migraine_with_aura": migraine_aura == "Yes",
                    "blood_clot_history": blood_clots == "Yes",
                    "breast_cancer_current": breast_cancer == "Yes",
                    "pelvic_infection_current": pelvic_infection == "Yes",
                    "heavy_menstrual_bleeding": heavy_bleeding == "Yes",
                    "severe_hypertension": hypertension == "Yes",
                    "liver_disease_severe": liver_disease == "Yes"
                })
                st.session_state.step = 3
                st.rerun()
    
    # Step 3: Preferences
    elif st.session_state.step == 3:
        st.markdown("### Your Preferences")
        st.markdown("Tell us what matters most to you.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            wants_children_soon = st.radio("Do you want children within the next year?", ["Yes", "No"])
            wants_long_term = st.radio("Do you want long-term protection (3+ years)?", ["Yes", "No"])
            wants_non_hormonal = st.radio("Do you prefer non-hormonal methods?", ["Yes", "No"])
            needs_privacy = st.radio("Do you need a private method?", ["Yes", "No"])
        
        with col2:
            wants_std_protection = st.radio("Do you need STI protection including HIV?", ["Yes", "No"])
            difficulty_remembering = st.radio("Is it hard to remember daily pills?", ["Yes", "No"])
            religious_concerns = st.radio("Do you have religious concerns about hormonal methods?", ["Yes", "No"])
        
        if st.button("Get Recommendations", type="primary"):
            with st.spinner("Finding the best options for you..."):
                time.sleep(1.2)
                st.session_state.user_data.update({
                    "wants_children_soon": wants_children_soon == "Yes",
                    "wants_long_term": wants_long_term == "Yes",
                    "wants_non_hormonal": wants_non_hormonal == "Yes",
                    "needs_privacy": needs_privacy == "Yes",
                    "wants_std_protection": wants_std_protection == "Yes",
                    "difficulty_remembering_daily": difficulty_remembering == "Yes",
                    "religious_concerns": religious_concerns == "Yes"
                })
                st.session_state.recommendations = calculate_recommendations(st.session_state.user_data)
                st.session_state.step = 4
                st.rerun()
    
    # Step 4: Results
    elif st.session_state.step == 4:
        st.markdown("### Your Personalized Recommendations")
        
        county = st.session_state.user_data.get("county", "default")
        context = COUNTY_CONTEXT.get(county, COUNTY_CONTEXT.get("default", {}))
        
        with st.expander("Information for your area", expanded=False):
            st.markdown(f"**Access to services:** {context.get('access_notes')}")
            st.markdown(f"**Partner involvement:** {context.get('partner_dynamics')}")
        
        if st.session_state.recommendations:
            top_methods = st.session_state.recommendations[:3]
            
            # Effectiveness guide
            st.markdown("**Effectiveness Guide**")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("- **99%+** : Highly Effective (IUDs, Implant)")
            with col2:
                st.markdown("- **94-98%** : Very Effective (Injectable, LAM)")
            with col3:
                st.markdown("- **79-91%** : Effective with correct use (Pills, Condoms)")
            
            st.markdown("---")
            
            for idx, method in enumerate(top_methods):
                badge_html = get_badge_class(method["type"], method["hormonal"])
                
                st.markdown(f"""
                    <div class="recommendation-card">
                        <h2 style="margin:0 0 12px; color:#0D47A1;">{idx + 1}. {method['name']}</h2>
                        <div style="margin-bottom: 16px;">{badge_html}</div>
                        <div class="effectiveness-bar">
                            <div class="effectiveness-fill" style="width: {method['effectiveness']}%;">
                                {method['effectiveness']}% Effective
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Key Advantages**")
                    for adv in method["advantages"]:
                        st.markdown(f"- {adv}")
                
                with col2:
                    st.markdown("**Possible Side Effects**")
                    for se in method["side_effects"]:
                        st.markdown(f"- {se}")
                
                with st.expander("Questions to ask your provider"):
                    for q in method["questions"]:
                        st.markdown(f"- {q}")
                
                st.markdown("---")
            
            # Myth busting section
            st.markdown("### Evidence-Based Answers to Common Myths")
            st.markdown("Based on Kenya FP Guidelines 7th Edition")
            
            myth_cols = st.columns(2)
            myth_items = list(MYTHS.items())[:6]
            
            for i, (myth_id, myth_data) in enumerate(myth_items):
                with myth_cols[i % 2]:
                    st.markdown(f"""
                        <div class="myth-card">
                            <strong>Myth:</strong> {myth_data['myth']}<br>
                            <strong>Fact:</strong> {myth_data['evidence']}
                        </div>
                    """, unsafe_allow_html=True)
            
            # Download report
            report_data = f"""
AfyaChoice AI Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

User Profile:
- Age: {st.session_state.user_data.get('age', 'N/A')}
- County: {st.session_state.user_data.get('county', 'N/A').title()}
- Children: {st.session_state.user_data.get('children', 'N/A')}

Top 3 Recommendations:
1. {top_methods[0]['name']} - {top_methods[0]['effectiveness']}% effective
2. {top_methods[1]['name']} - {top_methods[1]['effectiveness']}% effective
3. {top_methods[2]['name']} - {top_methods[2]['effectiveness']}% effective

Disclaimer: This is a decision support tool based on Kenya FP Guidelines.
Always consult a healthcare provider before making decisions about contraception.
            """
            
            st.download_button(
                label="Download Report",
                data=report_data,
                file_name=f"afyachoice_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Start Over"):
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.rerun()
            
            with col2:
                st.markdown("""
                    <div class="info-box">
                        <strong>Disclaimer</strong><br>
                        This tool provides information based on Kenya FP Guidelines.
                        Always consult a healthcare provider before making decisions.
                    </div>
                """, unsafe_allow_html=True)
        
        else:
            st.warning("No recommendations available. Please start over.")
            if st.button("Start Over"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
    
    # Footer
    st.markdown("""
        <div class="footer">
            <p>Kenya FP Guidelines 7th Edition (2025) | WHO Medical Eligibility Criteria 5th Edition</p>
            <p>AfyaChoice AI - Empowering informed family planning decisions in Kenya</p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()