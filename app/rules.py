def get_mec_score(method_name, conditions):
    mec = 1
    chronic = [c for c in conditions.get("chronic_conditions", []) if c != "None"]
    
    if conditions.get("breastfeeding") == "Yes":
        if "Combined" in method_name:
            mec = 3
        elif method_name == "Injectables":
            mec = 2
    
    if "High blood pressure (hypertension)" in chronic and "Combined" in method_name:
        mec = 3
    
    if conditions.get("migraine_aura") == "Yes" and "Combined" in method_name:
        mec = 4
    
    if "Cancer (any type)" in chronic and method_name in ["Combined Pill", "Progestin-Only Pill", "Implant", "Injectables"]:
        mec = 4
    
    if "Diabetes" in chronic and "Combined" in method_name:
        mec = 2
    
    if "Convulsion disorder (epilepsy)" in chronic and "Combined" in method_name:
        mec = 3
    
    if "HIV" in chronic and "Combined" in method_name:
        mec = 2
    
    return mec

def is_eligible(method_name, mec):
    return mec != 4
