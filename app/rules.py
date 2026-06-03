class SafetyRuleEngine:
    def __init__(self):
        # Hardcoded rules from Kenya FP Guidelines 2025
        self.rules = [
            {"condition": "breastfeeding_under_6_weeks", "avoid_methods": ["combined_pill"], "reason": "Estrogen may affect milk supply."},
            {"condition": "age_over_35_and_smoker", "avoid_methods": ["combined_pill"], "reason": "Increased cardiovascular risk."},
            {"condition": "migraine_with_aura", "avoid_methods": ["combined_pill"], "reason": "Increased stroke risk."},
            {"condition": "blood_clot_history", "avoid_methods": ["combined_pill"], "reason": "Estrogen increases clot risk."},
            {"condition": "breast_cancer_current", "avoid_methods": ["combined_pill", "progestin_pill", "implant", "injectable", "hormonal_iud"], "reason": "Hormones may stimulate breast cancer."},
            {"condition": "pelvic_infection_current", "avoid_methods": ["copper_iud", "hormonal_iud"], "reason": "IUD insertion can worsen infection."},
            {"condition": "heavy_menstrual_bleeding", "avoid_methods": ["copper_iud"], "reason": "Copper IUD makes bleeding heavier."}
        ]

    def apply(self, health_profile):
        unsafe = set()
        reasons = []
        for rule in self.rules:
            if self._check_condition(rule["condition"], health_profile):
                unsafe.update(rule["avoid_methods"])
                reasons.append(rule["reason"])
        return {"unsafe_methods": unsafe, "safety_reasons": reasons}

    def _check_condition(self, condition, profile):
        mapping = {
            "breastfeeding_under_6_weeks": lambda p: p.get("breastfeeding") and p.get("weeks_postpartum", 100) < 6,
            "age_over_35_and_smoker": lambda p: p.get("age", 0) > 35 and p.get("smoker", False),
            "migraine_with_aura": lambda p: p.get("migraine_with_aura", False),
            "blood_clot_history": lambda p: p.get("blood_clot_history", False),
            "breast_cancer_current": lambda p: p.get("breast_cancer_current", False),
            "pelvic_infection_current": lambda p: p.get("pelvic_infection_current", False),
            "heavy_menstrual_bleeding": lambda p: p.get("heavy_menstrual_bleeding", False),
        }
        if condition in mapping:
            return mapping[condition](profile)
        return False
