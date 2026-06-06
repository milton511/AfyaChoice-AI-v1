import json
import os
from ml_model import hormonal_probability
from rules import get_mec_score
import streamlit as st

@st.cache_data(ttl=3600)
def load_methods():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, "data", "methods.json")
    with open(json_path, "r", encoding="utf-8-sig") as f:
        return json.load(f)["methods"]

def rank_methods(user_data, user_preference=None):
    methods = load_methods()
    prob = hormonal_probability(
        user_data["age_group_clinical"],
        user_data["edu_level"],
        user_data["marital_status"],
        user_data["ever_been_pregnant"]
    )
    
    conditions = {
        "breastfeeding": user_data.get("breastfeeding", "No"),
        "hypertension": user_data.get("hypertension", "No"),
        "migraine_aura": user_data.get("migraine_aura", "No"),
        "cancer_history": user_data.get("cancer_history", "None"),
        "sti_risk": user_data.get("sti_risk", "No")
    }
    
    scored = []
    for m in methods:
        mec = get_mec_score(m["name"], conditions)
        if mec == 4:
            continue
        
        # Base score from model
        if m["type"] == "hormonal":
            base = prob * 100
        else:
            base = (1 - prob) * 100
        
        mec_weight = {1:15, 2:5, 3:-10}.get(mec, 0)
        
        # Preference weights
        pref_weight = 0
        if user_preference == "Long-acting":
            if "Implant" in m["name"] or "IUD" in m["name"]:
                pref_weight = 20
        elif user_preference == "Short-term":
            if "Pill" in m["name"] or "Condom" in m["name"]:
                pref_weight = 20
        elif user_preference == "No hormones" and m["type"] == "non-hormonal":
            pref_weight = 25
        
        # Duration preference
        duration = user_data.get("duration_pref", "No preference")
        if duration == "Short-term (<1 year)":
            if "Pill" in m["name"] or "Condom" in m["name"]:
                pref_weight += 15
        elif duration == "Long-term (3+ years)":
            if "Implant" in m["name"] or "IUD" in m["name"]:
                pref_weight += 15
        
        # Pregnancy intention
        next_child = user_data.get("next_child", "Not planning")
        if next_child == "Within 1 year":
            if "Pill" in m["name"] or "Condom" in m["name"]:
                pref_weight += 20
        
        total = base + mec_weight + pref_weight
        
        # Build explanation
        explanation_parts = []
        if prob > 60 and m["type"] == "hormonal":
            explanation_parts.append("Matches your hormonal suitability profile")
        elif prob < 40 and m["type"] == "non-hormonal":
            explanation_parts.append("Matches your non-hormonal suitability profile")
        if mec == 1:
            explanation_parts.append("Very safe according to MEC guidelines")
        elif mec == 2:
            explanation_parts.append("Generally safe – benefits outweigh risks")
        if pref_weight > 0:
            explanation_parts.append("Fits your preference/duration choice")
        explanation = "; ".join(explanation_parts) if explanation_parts else "Balanced option"
        
        scored.append({
            "name": m["name"],
            "type": m["type"],
            "effectiveness": m["effectiveness"],
            "benefits": m["benefits"],
            "side_effects": m["side_effects"],
            "score": total,
            "explanation": explanation
        })
    
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:3]
