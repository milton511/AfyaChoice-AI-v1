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

def rank_methods(user_data, user_preference="No preference"):
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
        "migraine_aura": user_data.get("migraine_aura", "No")
    }
    
    scored = []
    for m in methods:
        mec = get_mec_score(m["name"], conditions)
        if mec == 4:
            continue
        
        if m["type"] == "hormonal":
            base = prob * 100
        else:
            base = (1 - prob) * 100
        
        mec_weight = {1:15, 2:5, 3:-10}.get(mec, 0)
        
        pref_weight = 0
        if user_preference == "Long-acting":
            if "Implant" in m["name"] or "IUD" in m["name"]:
                pref_weight = 20
        elif user_preference == "Short-term":
            if "Pill" in m["name"] or "Condom" in m["name"]:
                pref_weight = 20
        elif user_preference == "No hormones" and m["type"] == "non-hormonal":
            pref_weight = 25
        
        total = base + mec_weight + pref_weight
        scored.append({
            "name": m["name"],
            "type": m["type"],
            "effectiveness": m["effectiveness"],
            "benefits": m["benefits"],
            "side_effects": m["side_effects"],
            "score": total
        })
    
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:3]
