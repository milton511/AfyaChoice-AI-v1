from rules import SafetyRuleEngine
from ml_model import MLRanker

class RecommendationEngine:
    def __init__(self):
        self.safety = SafetyRuleEngine()
        self.ml = MLRanker()

    def get_recommendations(self, health_profile, preferences, county=None):
        # Safety filter
        safety_result = self.safety.apply(health_profile)
        unsafe = safety_result["unsafe_methods"]

        # Build feature vector exactly as the model expects
        features = {
            "age": health_profile.get("age", 25),
            "parity": health_profile.get("parity", 1),
            "education": health_profile.get("education", "Secondary"),
            "marital": health_profile.get("marital", "Married")
        }
        # Get probabilities for each method from the real model
        method_scores = self.ml.predict_scores(features)

        # Map model output method names to our internal ids
        name_to_id = {
            "Injections": "injectable",
            "Implants": "implant",
            "Pills": "combined_pill",
            "IUCD": "copper_iud",
            "Male Condom": "male_condom",
            "Female Condom": "female_condom",
            "Injectables": "injectable",
            "Condom": "male_condom",
            "Pill": "combined_pill",
            "Patch": "combined_pill",
            "Female Sterilization": "hormonal_iud",
            "Hormonal": "combined_pill",
            "IUD": "copper_iud",
            "Emergency": "injectable",
            "Natural": "lam",
            "Traditional/Herbal": "lam",
            "Rhythm Methods": "lam",
            "Permanent": "copper_iud",
            "Barrier": "male_condom"
        }

        ranked = []
        for ml_method, prob in method_scores.items():
            method_id = name_to_id.get(ml_method)
            if method_id is None:
                continue
            if method_id in unsafe:
                continue
            score = prob  # base score from model
            # preference boosts
            if preferences.get("wants_long_term") and method_id in ["implant", "copper_iud", "hormonal_iud"]:
                score += 0.15
            if preferences.get("wants_non_hormonal") and method_id in ["copper_iud", "male_condom", "female_condom", "lam"]:
                score += 0.15
            if preferences.get("wants_std_protection") and method_id in ["male_condom", "female_condom"]:
                score += 0.20
            ranked.append({"method_id": method_id, "score": score, "name": ml_method})

        ranked.sort(key=lambda x: x["score"], reverse=True)
        return {
            "ranked_methods": ranked[:5],
            "safety_warnings": safety_result["safety_reasons"]
        }
