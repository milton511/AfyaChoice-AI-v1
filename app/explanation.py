"""
Explanation Engine - Provides clear, honest explanations for recommendations
"""

from typing import Dict, Any


class ExplanationEngine:
    """Generates user-friendly explanations for method recommendations"""

    def __init__(self):
        self.effectiveness_labels = {
            99: "More than 99% effective",
            98: "98% effective",
            94: "94% effective",
            91: "91% effective",
            85: "85% effective",
            82: "82% effective",
            79: "79% effective",
            76: "76% effective"
        }

    def generate_explanation(self, method: Dict[str, Any]) -> Dict[str, Any]:
        """Generate complete explanation for a recommended method"""
        effectiveness_text = self.effectiveness_labels.get(
            method.get("effectiveness", 90),
            f"{method.get('effectiveness', 90)}% effective"
        )

        explanation_parts = []

        explanation_parts.append(f"{method['name']} is {effectiveness_text.lower()}.")

        if method.get("hormonal", False):
            explanation_parts.append("This method uses hormones to prevent pregnancy.")
        else:
            explanation_parts.append("This method does not use hormones.")

        method_type = method.get("type", "")
        if method_type == "long_acting_reversible":
            explanation_parts.append("It is long-acting but reversible.")
        elif method_type == "short_acting":
            if method.get("duration_daily"):
                explanation_parts.append("You need to take this daily for it to work.")
            elif method.get("duration_weeks"):
                explanation_parts.append(f"You need it every {method['duration_weeks']} weeks.")
        elif method_type == "barrier":
            explanation_parts.append("You use this each time you have sex.")
        elif method_type == "behavioral":
            explanation_parts.append("This method requires tracking your fertility signs.")

        explanation_parts.append("")

        advantages = method.get("advantages", [])[:3]
        if advantages:
            advantages_text = "Key advantages: " + ", ".join(advantages)
            explanation_parts.append(advantages_text)

        explanation_parts.append("")

        side_effects = method.get("side_effects", [])[:3]
        if side_effects:
            side_effects_text = "Possible side effects: " + ", ".join(side_effects)
            explanation_parts.append(side_effects_text)
            explanation_parts.append("Most side effects are temporary and improve within 3-6 months.")

        return {
            "summary": explanation_parts[0] if explanation_parts else "",
            "detailed": "\n".join(explanation_parts),
            "advantages": method.get("advantages", []),
            "side_effects": method.get("side_effects", []),
            "effectiveness": effectiveness_text
        }

    def generate_caution_explanation(self, method_id: str, method_data: Dict[str, Any]) -> str:
        """Generate explanation for methods that require caution"""
        caution_list = method_data.get("caution_if", [])
        if not caution_list:
            return None

        caution_text = "Caution needed if you have: " + ", ".join(caution_list[:4])
        return caution_text

    def generate_contraindication_explanation(self, method_id: str, method_data: Dict[str, Any]) -> str:
        """Generate explanation for methods that are contraindicated"""
        contraindications = method_data.get("contraindications", [])
        if not contraindications:
            return None

        contraindication_text = "Do not use this method if you have: " + ", ".join(contraindications[:4])
        return contraindication_text