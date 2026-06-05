def get_mec_score(method_name, conditions):
    mec = 1  # safe default
    
    # Breastfeeding
    if conditions.get("breastfeeding") == "Yes":
        if "Combined" in method_name:
            mec = 3
        elif method_name == "Injectables":
            mec = 2
    
    # Hypertension
    if conditions.get("hypertension") == "Yes" and "Combined" in method_name:
        mec = 3
    
    # Migraine with aura
    if conditions.get("migraine_aura") == "Yes" and "Combined" in method_name:
        mec = 4
    
    # Cancer history
    cancer = conditions.get("cancer_history", "None")
    if cancer == "Breast cancer" and method_name in ["Combined Pill", "Progestin-Only Pill", "Implant", "Injectables"]:
        mec = 4  # avoid hormonal methods
    elif cancer == "Cervical cancer" and "IUD" in method_name:
        mec = 2  # caution with IUD
    
    # STI risk
    if conditions.get("sti_risk") == "Yes" and "IUD" in method_name:
        mec = 3  # increased infection risk
    
    return mec

def is_eligible(method_name, mec):
    return mec != 4
