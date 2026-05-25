"""
Kenya FP Guidelines Safety Filter Rule Engine
Based on Kenya FP Guidelines 7th Edition (2025) and WHO MEC
"""

import json
from pathlib import Path
from typing import Dict, List, Set, Any


class SafetyRuleEngine:
    """Applies Kenya FP guidelines to filter methods based on health profile"""

    def __init__(self, guidelines_path: str = None):
        if guidelines_path is None:
            guidelines_path = Path(__file__).parent / "guidelines.json"

        self.guidelines = self._load_guidelines(guidelines_path)
        self.rules = self.guidelines.get("kenya_fp_guidelines_7th_edition", {}).get("rules", [])
        self._build_method_restrictions()

    def _load_guidelines(self, path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {"kenya_fp_guidelines_7th_edition": {"rules": []}}

    def _build_method_restrictions(self):
        """Build internal mapping of conditions to methods"""
        self.condition_method_map = {}

        for rule in self.rules:
            condition = rule.get("condition", "")
            self.condition_method_map[condition] = {
                "avoid": set(rule.get("avoid_methods", [])),
                "safe": set(rule.get("safe_methods", [])),
                "reason": rule.get("reason", "")
            }

    def apply_health_filters(self, health_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Apply all applicable rules to health profile"""
        unsafe_methods = set()
        safe_methods = set()
        reasons = []
        warnings = []

        for condition, rule_info in self.condition_method_map.items():
            if self._check_condition(condition, health_profile):
                unsafe_methods.update(rule_info["avoid"])
                safe_methods.update(rule_info["safe"])

                if rule_info["avoid"]:
                    reasons.append({
                        "condition": condition,
                        "avoided_methods": list(rule_info["avoid"]),
                        "reason": rule_info["reason"]
                    })

        return {
            "unsafe_methods": unsafe_methods,
            "safe_methods": safe_methods,
            "reasons": reasons,
            "warnings": warnings
        }

    def _check_condition(self, condition: str, profile: Dict[str, Any]) -> bool:
        """Check if a condition applies based on profile data"""
        condition_map = {
            "breastfeeding_under_6_weeks": lambda p: (
                p.get("breastfeeding", False) and
                p.get("weeks_postpartum", 100) < 6
            ),
            "age_over_35_and_smoker": lambda p: (
                p.get("age", 0) > 35 and
                p.get("smoker", False)
            ),
            "migraine_with_aura": lambda p: (
                p.get("migraine_with_aura", False)
            ),
            "blood_clot_history": lambda p: (
                p.get("blood_clot_history", False)
            ),
            "breast_cancer_current": lambda p: (
                p.get("breast_cancer_current", False)
            ),
            "pelvic_infection_current": lambda p: (
                p.get("pelvic_infection_current", False)
            ),
            "heavy_menstrual_bleeding": lambda p: (
                p.get("heavy_menstrual_bleeding", False)
            ),
            "severe_hypertension": lambda p: (
                p.get("severe_hypertension", False)
            ),
            "diabetes_with_complications": lambda p: (
                p.get("diabetes_with_complications", False)
            ),
            "liver_disease_severe": lambda p: (
                p.get("liver_disease_severe", False)
            ),
            "postpartum_under_3_weeks": lambda p: (
                p.get("weeks_postpartum", 100) < 3
            ),
            "puerperal_sepsis": lambda p: (
                p.get("puerperal_sepsis", False)
            ),
            "unexplained_vaginal_bleeding": lambda p: (
                p.get("unexplained_vaginal_bleeding", False)
            )
        }

        checker = condition_map.get(condition)
        if checker:
            return checker(profile)

        return False

    def is_method_contraindicated(self, method: str, health_profile: Dict[str, Any]) -> bool:
        """Check if a specific method is contraindicated"""
        filter_result = self.apply_health_filters(health_profile)
        return method in filter_result["unsafe_methods"]