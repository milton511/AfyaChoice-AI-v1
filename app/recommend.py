"""
Recommendation Engine - Ranks suitable methods based on safety and preferences
"""

import json
from pathlib import Path
from typing import Dict, List, Any


class RecommendationEngine:
    """Ranks and scores methods based on safety, preferences, and context"""

    def __init__(self, methods_path: str = None):
        if methods_path is None:
            methods_path = Path(__file__).parent / "methods.json"

        with open(methods_path, "r") as f:
            self.methods = json.load(f)

        self.preference_weights = {
            "needs_privacy": 0.25,
            "wants_long_term": 0.25,
            "prefers_non_hormonal": 0.20,
            "wants_children_soon": 0.15,
            "wants_std_protection": 0.30,
            "difficulty_remembering_daily": 0.20,
            "religious_concerns": 0.15
        }

    def get_safe_methods(self, health_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Get all methods that are medically safe"""
        try:
            from rules import SafetyRuleEngine
            safety_engine = SafetyRuleEngine()
            safety_result = safety_engine.apply_health_filters(health_profile)

            safe_methods = {}

            for method_id, method_data in self.methods.items():
                if method_id not in safety_result["unsafe_methods"]:
                    safe_methods[method_id] = method_data

            return {
                "safe_methods": safe_methods,
                "unsafe_methods": {
                    method_id: self.methods[method_id]
                    for method_id in safety_result["unsafe_methods"]
                    if method_id in self.methods
                },
                "safety_reasons": safety_result["reasons"],
                "warnings": safety_result["warnings"]
            }
        except Exception as e:
            return {
                "safe_methods": self.methods,
                "unsafe_methods": {},
                "safety_reasons": [],
                "warnings": []
            }

    def rank_methods(
        self,
        health_profile: Dict[str, Any],
        preferences: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Rank safe methods based on preferences"""
        safe_methods_data = self.get_safe_methods(health_profile)
        safe_methods = safe_methods_data["safe_methods"]

        if context is None:
            context = {}

        ranked_methods = []

        for method_id, method_data in safe_methods.items():
            score = self._calculate_score(
                method_id,
                method_data,
                preferences,
                context
            )

            ranked_methods.append({
                "method_id": method_id,
                "name": method_data["name"],
                "type": method_data.get("type", "unknown"),
                "effectiveness": method_data.get("effectiveness", 0),
                "hormonal": method_data.get("hormonal", False),
                "score": score,
                "advantages": method_data.get("advantages", [])[:3],
                "side_effects_preview": method_data.get("side_effects", [])[:2]
            })

        ranked_methods.sort(key=lambda x: x["score"], reverse=True)

        return ranked_methods

    def _calculate_score(
        self,
        method_id: str,
        method_data: Dict[str, Any],
        preferences: Dict[str, Any],
        context: Dict[str, Any]
    ) -> float:
        """Calculate score for a single method"""
        score = 0.0

        if preferences.get("needs_privacy", False):
            if method_data.get("type") in ["long_acting_reversible"]:
                score += self.preference_weights["needs_privacy"]

        if preferences.get("wants_long_term", False):
            if method_data.get("type") == "long_acting_reversible":
                score += self.preference_weights["wants_long_term"]

        if preferences.get("wants_children_soon", False):
            if method_data.get("type") not in ["long_acting_reversible"]:
                score += self.preference_weights["wants_children_soon"]

        if preferences.get("wants_non_hormonal", False):
            if not method_data.get("hormonal", False):
                score += self.preference_weights["prefers_non_hormonal"]

        if preferences.get("wants_std_protection", False):
            if method_data.get("type") == "barrier":
                score += self.preference_weights["wants_std_protection"]

        if preferences.get("difficulty_remembering_daily", False):
            if method_data.get("type") in ["long_acting_reversible", "short_acting"]:
                if not method_data.get("duration_daily", False):
                    score += self.preference_weights["difficulty_remembering_daily"]

        if preferences.get("religious_concerns", False):
            if not method_data.get("hormonal", False):
                score += self.preference_weights["religious_concerns"]

        effectiveness_score = method_data.get("effectiveness", 0) / 100
        score += effectiveness_score * 0.20

        return round(score, 2)

    def get_method_details(self, method_id: str) -> Dict[str, Any]:
        """Get complete information about a method"""
        if method_id not in self.methods:
            return None

        method = self.methods[method_id].copy()
        method["method_id"] = method_id

        return method