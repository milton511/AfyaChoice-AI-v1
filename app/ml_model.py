import pickle
import pandas as pd
import numpy as np
from pathlib import Path

class MLRanker:
    def __init__(self, model_path=None):
        if model_path is None:
            model_path = Path(__file__).parent / "data" / "model.pkl"
        if not model_path.exists():
            print("Model not found, training on the fly using available Excel files...")
            self._train_and_save(model_path)
        with open(model_path, "rb") as f:
            obj = pickle.load(f)
        self.model = obj["model"]
        self.le = obj["label_encoder"]
        self.scaler = obj["scaler"]
        self.feature_names = obj["feature_names"]

    def _train_and_save(self, model_path):
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.preprocessing import LabelEncoder, StandardScaler

        data_dir = Path(__file__).parent / "data"
        all_X, all_y = [], []
        for fname in data_dir.glob("*.xlsx"):
            df = pd.read_excel(fname)
            # Identify target column
            target_cols = ["FP_method", "FP_methods_used", "FP_currently_using_clean", "FP_methods_cleaned"]
            target = None
            for col in target_cols:
                if col in df.columns:
                    target = df[col].astype(str)
                    break
            if target is None:
                continue
            # Extract features
            features = {}
            for col in ["age", "age_in_yrs"]:
                if col in df.columns:
                    features["age"] = df[col]
                    break
            for col in ["biological_children", "noOfLiveBirthPreg", "total_live_births", "children"]:
                if col in df.columns:
                    features["parity"] = df[col]
                    break
            for col in ["edu_level_clean", "edu_level", "highestEduLevel"]:
                if col in df.columns:
                    features["education"] = df[col].astype(str)
                    break
            for col in ["marital_status_clean", "maritalStatus", "marital_status"]:
                if col in df.columns:
                    features["marital"] = df[col].astype(str)
                    break
            if features:
                X = pd.DataFrame(features).dropna()
                y = target.loc[X.index]
                if len(X) > 0:
                    all_X.append(X)
                    all_y.append(y)

        if not all_X:
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
            X = pd.concat(all_X, ignore_index=True)
            y = pd.concat(all_y, ignore_index=True)

        # Encode categorical features with simple mapping
        for col in ["education", "marital"]:
            if col in X.columns:
                mapping = {"None":0, "Primary":1, "Secondary":2, "College":3, "University":4} if col == "education" \
                          else {"Single":0, "Married":1, "Living together":2, "Divorced":3, "Widowed":4}
                X[col] = X[col].map(mapping).fillna(0)

        le_target = LabelEncoder()
        y_enc = le_target.fit_transform(y)
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_scaled, y_enc)

        model_path.parent.mkdir(parents=True, exist_ok=True)
        with open(model_path, "wb") as f:
            pickle.dump({
                "model": model,
                "label_encoder": le_target,
                "scaler": scaler,
                "feature_names": list(X.columns)
            }, f)
        print(f"Model saved to {model_path}")

    def predict_scores(self, user_features):
        df = pd.DataFrame([user_features])
        # Ensure all required columns present
        for col in self.feature_names:
            if col not in df.columns:
                df[col] = 0
        df = df[self.feature_names]
        # Encode categoricals
        for col in ["education", "marital"]:
            if col in df.columns:
                mapping = {"None":0, "Primary":1, "Secondary":2, "College":3, "University":4} if col == "education" \
                          else {"Single":0, "Married":1, "Living together":2, "Divorced":3, "Widowed":4}
                df[col] = df[col].map(mapping).fillna(0)
        X_scaled = self.scaler.transform(df)
        proba = self.model.predict_proba(X_scaled)[0]
        return {self.le.classes_[i]: proba[i] for i in range(len(proba))}
