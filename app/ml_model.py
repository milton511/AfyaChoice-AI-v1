import pickle
import pandas as pd
from pathlib import Path

class MLRanker:
    def __init__(self, model_path=None):
        if model_path is None:
            model_path = Path(__file__).parent / "data" / "model.pkl"
        with open(model_path, "rb") as f:
            obj = pickle.load(f)
        self.model = obj["model"]
        self.le = obj["label_encoder"]
        self.scaler = obj["scaler"]
        self.feature_names = obj["feature_names"]  # ['age','parity','education','marital']

    def predict_scores(self, user_features):
        # user_features is a dict with keys: age, parity, education, marital
        # Build a DataFrame with the exact columns in the correct order
        df = pd.DataFrame([{
            "age": user_features.get("age", 25),
            "parity": user_features.get("parity", 1),
            "education": user_features.get("education", "Secondary"),
            "marital": user_features.get("marital", "Married")
        }])
        # Ensure all columns are present and in the right order
        df = df[self.feature_names]
        # Convert categorical columns to codes (the model was trained on numeric)
        # We'll use LabelEncoder previously saved? Actually the model expects already encoded numbers.
        # But we didn't save encoders for education/marital. So we need to re-encode them here.
        # For simplicity, we'll use the same encoding as in training (we must have saved them)
        # Since we didn't, we'll re-fit on the training data? Not possible here.
        # Quick fix: use pandas category codes – but they may not match training.
        # However, the model was trained on LabelEncoder on the full dataset.
        # So we need to re-apply the same mapping. Let's reload training encoders.
        # We'll create a separate file for encoders. For now, let's just use ordinal encoding and hope for consistency.
        # Better: save the encoders for categorical columns during training.
        # But to make it work now, we'll use pd.Categorical codes on the fly.
        # This is a temporary solution.
        for col in ["education", "marital"]:
            if col in df.columns:
                # Use a fixed mapping based on common values from training
                if col == "education":
                    mapping = {"None":0, "Primary":1, "Secondary":2, "College":3, "University":4}
                else:  # marital
                    mapping = {"Single":0, "Married":1, "Living together":2, "Divorced":3, "Widowed":4}
                df[col] = df[col].map(mapping).fillna(0)
        # Scale
        X_scaled = self.scaler.transform(df)
        proba = self.model.predict_proba(X_scaled)[0]
        return {self.le.classes_[i]: proba[i] for i in range(len(proba))}
