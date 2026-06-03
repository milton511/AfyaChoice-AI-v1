import pickle
import pandas as pd
import numpy as np
from pathlib import Path
import traceback

class MLRanker:
    def __init__(self, model_path=None):
        if model_path is None:
            model_path = Path(__file__).parent / "data" / "model.pkl"
        if not model_path.exists():
            print("Model file not found. Training on the fly using available Excel files.")
            self._train_model_on_disk(model_path)
        with open(model_path, "rb") as f:
            obj = pickle.load(f)
        self.model = obj["model"]
        self.le = obj["label_encoder"]
        self.scaler = obj["scaler"]
        self.feature_names = obj["feature_names"]

    def _train_model_on_disk(self, model_path):
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.preprocessing import LabelEncoder, StandardScaler
        from sklearn.model_selection import train_test_split

        data_dir = Path(__file__).parent / "data"
        all_features = []
        all_targets = []

        for xlsx in data_dir.glob("*.xlsx"):
            df = pd.read_excel(xlsx)
            # Try to find target column
            target_cols = ["FP_method", "FP_methods_used", "FP_currently_using_clean", "FP_methods_cleaned"]
            target = None
            for col in target_cols:
                if col in df.columns:
                    target = df[col].astype(str)
                    break
            if target is None:
                continue
            # Features
            feats = {}
            for col in ["age", "age_in_yrs"]:
                if col in df.columns:
                    feats["age"] = df[col]
                    break
            for col in ["biological_children", "noOfLiveBirthPreg", "total_live_births", "children"]:
                if col in df.columns:
                    feats["parity"] = df[col]
                    break
            for col in ["edu_level_clean", "edu_level", "highestEduLevel"]:
                if col in df.columns:
                    feats["education"] = df[col].astype(str)
                    break
            for col in ["marital_status_clean", "maritalStatus", "marital_status"]:
                if col in df.columns:
                    feats["marital"] = df[col].astype(str)
                    break
            if feats:
                X = pd.DataFrame(feats).dropna()
                y = target.loc[X.index]
                if len(X) > 0:
                    all_features.append(X)
                    all_targets.append(y)

        if not all_features:
            # Fallback dummy data
            n = 500
            X = pd.DataFrame({
                "age": np.random.randint(18,45,n),
                "parity": np.random.randint(0,5,n),
                "education": np.random.choice(["Primary","Secondary","College"],n),
                "marital": np.random.choice(["Married","Single","Living together"],n)
            })
            y = np.random.choice(["Injectables","Implants","Pills","IUCD","Male Condom"],n)
        else:
            X = pd.concat(all_features, ignore_index=True)
            y = pd.concat(all_targets, ignore_index=True)

        # Encode categoricals
        for col in ["education", "marital"]:
            if col in X.columns:
                # simple mapping that matches training
                if col == "education":
                    mapping = {"None":0, "Primary":1, "Secondary":2, "College":3, "University":4}
                else:
                    mapping = {"Single":0, "Married":1, "Living together":2, "Divorced":3, "Widowed":4}
                X[col] = X[col].map(mapping).fillna(0)

        le_target = LabelEncoder()
        y_enc = le_target.fit_transform(y)
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_scaled, y_enc)

        # Save model
        model_path.parent.mkdir(exist_ok=True)
        with open(model_path, "wb") as f:
            pickle.dump({
                "model": model,
                "label_encoder": le_target,
                "scaler": scaler,
                "feature_names": list(X.columns)
            }, f)
        print(f"Model trained and saved to {model_path}")

    def predict_scores(self, user_features):
        df = pd.DataFrame([user_features])
        # Ensure all feature columns present
        for col in self.feature_names:
            if col not in df.columns:
                df[col] = 0
        df = df[self.feature_names]
        # Encode categoricals again (use same mapping as training)
        for col in ["education", "marital"]:
            if col in df.columns:
                if col == "education":
                    mapping = {"None":0, "Primary":1, "Secondary":2, "College":3, "University":4}
                else:
                    mapping = {"Single":0, "Married":1, "Living together":2, "Divorced":3, "Widowed":4}
                df[col] = df[col].map(mapping).fillna(0)
        X_scaled = self.scaler.transform(df)
        proba = self.model.predict_proba(X_scaled)[0]
        return {self.le.classes_[i]: proba[i] for i in range(len(proba))}
