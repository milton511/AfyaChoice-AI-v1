import json
from pathlib import Path

# Hardcoded myths
MYTHS = {
    "infertility": {"myth": "Contraceptives cause permanent infertility", "evidence": "No scientific evidence shows that. Fertility returns after stopping all methods, though injectable may delay return up to one year."},
    "ec_reusable": {"myth": "I can use emergency contraception every time I have sex", "evidence": "EC is for emergencies only. Repeated use reduces efficacy and causes irregular bleeding. Use a regular method for ongoing protection."},
    "weight_gain": {"myth": "All contraceptives cause weight gain", "evidence": "Only injectable DMPA is clearly linked to weight gain (2-5 kg over 1-2 years). Other methods have no proven significant weight gain."},
    "cancer": {"myth": "Contraceptives cause cancer", "evidence": "Hormonal methods reduce risk of ovarian and endometrial cancer. There is a small, reversible increase in breast/cervical cancer risk."}
}

class ExplanationEngine:
    def __init__(self):
        # No JSON loading – use hardcoded methods and myths
        self.methods = {
            "copper_iud": {"name": "Copper IUD", "effectiveness": 99, "advantages": ["No hormones", "Works immediately"], "side_effects": ["Heavier periods"]},
            "hormonal_iud": {"name": "Hormonal IUD", "effectiveness": 99, "advantages": ["Lighter periods", "Less cramping"], "side_effects": ["Irregular bleeding", "Headaches"]},
            "implant": {"name": "Implant", "effectiveness": 99, "advantages": ["Highly effective", "Discreet"], "side_effects": ["Irregular bleeding", "Weight gain"]},
            "injectable": {"name": "Injectable", "effectiveness": 94, "advantages": ["Private", "Every 3 months"], "side_effects": ["Weight gain", "Delayed fertility"]},
            "combined_pill": {"name": "Combined Pill", "effectiveness": 91, "advantages": ["Regulates periods"], "side_effects": ["Nausea", "Headaches"]},
            "progestin_pill": {"name": "Progestin-Only Pill", "effectiveness": 91, "advantages": ["Safe while breastfeeding"], "side_effects": ["Irregular bleeding"]},
            "male_condom": {"name": "Male Condom", "effectiveness": 82, "advantages": ["STI protection"], "side_effects": ["Reduced sensation"]},
            "female_condom": {"name": "Female Condom", "effectiveness": 79, "advantages": ["STI protection", "Woman-controlled"], "side_effects": ["Can be noisy"]},
            "lam": {"name": "LAM", "effectiveness": 98, "advantages": ["No cost", "No hormones"], "side_effects": ["Requires exclusive breastfeeding"]}
        }
        self.myths = MYTHS

    def explain_method(self, method_id):
        m = self.methods.get(method_id, {"name": "Unknown", "effectiveness": 0, "advantages": [], "side_effects": []})
        return {
            "summary": f"{m['name']} is {m['effectiveness']}% effective.",
            "advantages": m["advantages"],
            "side_effects": m["side_effects"]
        }

    def myth_buster(self, user_question):
        for key, myth in self.myths.items():
            if key.lower() in user_question.lower():
                return myth["evidence"]
        return "Please consult a healthcare provider for accurate information."

    def follow_up(self, method_id, side_effect):
        if "bleeding" in side_effect.lower() and method_id in ["implant", "injectable", "hormonal_iud"]:
            return "Irregular bleeding is common in the first 3-6 months. If heavy or prolonged, consult a provider."
        if "weight" in side_effect.lower() and method_id == "injectable":
            return "Weight gain of 2-5 kg over 1-2 years is possible. A balanced diet and exercise help."
        return "Please visit your nearest health facility for a provider review."
