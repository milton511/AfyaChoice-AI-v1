def get_mec_score(method_name, conditions):
    """
    Returns MEC score 1-4 based on WHO/Kenya guidelines.
    conditions: dict with keys 'breastfeeding', 'hypertension', 'migraine_aura'
    """
    mec = 1  # safe by default
    
    if conditions.get("breastfeeding") == "Yes":
        if "Combined" in method_name:
            mec = 3  # avoid combined pill
        elif method_name == "Injectables":
            mec = 2  # caution
        else:
            mec = 1
    
    if conditions.get("hypertension") == "Yes" and "Combined" in method_name:
        mec = 3
    
    if conditions.get("migraine_aura") == "Yes" and "Combined" in method_name:
        mec = 4  # unacceptable risk
    
    return mec

def is_eligible(method_name, mec):
    return mec != 4