import pandas as pd
import numpy as np
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from pathlib import Path

def load_and_unify():
    data_dir = Path("app/data")
    all_dfs = []

    files_targets = {
        "decision_support_smartphone.xlsx": "FP_method",
        "Effects_of_Engaging_Baseline_for_modeling.xlsx": "FP_methods_used",
        "partnership_for_maternal_newborn_and_childhealth.xlsx": "FP_currently_using_clean",
        "Prevalence_perceptions_cleaned.xlsx": "FP_methods_cleaned"
    }

    for fname, target_col in files_targets.items():
        path = data_dir / fname
        if not path.exists():
            print(f"Warning: {fname} not found, skipping.")
            continue
        df = pd.read_excel(path)
        if target_col not in df.columns:
            print(f"Warning: {target_col} not in {fname}, skipping.")
            continue

        df = df[df[target_col].notna() & (df[target_col] != "")]
        df["method"] = df[target_col].astype(str)

        features = {}
        for col in ["age", "age_in_yrs"]:
            if col in df.columns:
                features["age"] = df[col]
                break
        for col in ["biological_children", "noOfLiveBirthPreg", "total_live_births", "children"]:
            if col in df.columns:
                features["parity"] = df[col]
                break
        if "breastfeeding" in df.columns:
            features["breastfeeding"] = df["breastfeeding"].map({"Yes":1, "No":0})
        if "smoker" in df.columns:
            features["smoker"] = df["smoker"].map({"Yes":1, "No":0})
        if "hypertension" in df.columns:
            features["hypertension"] = df["hypertension"].map({"Yes":1, "No":0})
        # Education
        for col in ["edu_level_clean", "edu_level", "highestEduLevel"]:
            if col in df.columns:
                features["education"] = df[col].astype(str)
                break
        # Marital status
        for col in ["marital_status_clean", "maritalStatus", "marital_status"]:
            if col in df.columns:
                features["marital"] = df[col].astype(str)
                break

        if features:
            X = pd.DataFrame(features)
            y = df["method"]
            X = X.dropna()
            y = y.loc[X.index]
            if len(X) > 0:
                all_dfs.append((X, y))
                print(f"Added {len(X)} rows from {fname}")

    if not all_dfs:
        print("No usable data found. Falling back to dummy synthetic data.")
        n = 1000
        X = pd.DataFrame({
            "age": np.random.randint(18,45,n),
            "parity": np.random.randint(0,5,n),
            "breastfeeding": np.random.choice([0,1],n),
            "smoker": np.random.choice([0,1],n),
            "hypertension": np.random.choice([0,1],n),
            "education": np.random.choice(["Primary","Secondary","College"],n),
            "marital": np.random.choice(["Married","Single","Living together"],n)
        })
        y = np.random.choice(["Injectables","Implants","Pills","IUCD","Male Condom"],n)
        return X, y

    X_all = pd.concat([x for x,y in all_dfs], ignore_index=True)
    y_all = pd.concat([y for x,y in all_dfs], ignore_index=True)
    return X_all, y_all

def preprocess(X, y):
    cat_cols = X.select_dtypes(include=['object', 'string']).columns
    for col in cat_cols:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
    X = X.fillna(0)

    le_target = LabelEncoder()
    y_encoded = le_target.fit_transform(y)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    return X_scaled, y_encoded, le_target, scaler, list(X.columns)

def train():
    X, y = load_and_unify()
    print(f"Total samples: {len(X)}")
    print(f"Features: {list(X.columns)}")
    print(f"Unique methods: {y.unique()}")

    X_scaled, y_enc, le_target, scaler, feature_names = preprocess(X, y)

    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_enc, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=200, max_depth=15, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate (skip classification report if label mismatch)
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Test accuracy: {acc:.4f}")
    # Only print classification report if the label set matches
    try:
        print(classification_report(y_test, y_pred, target_names=le_target.classes_))
    except ValueError as e:
        print(f"Note: {e} – skipping detailed report.")

    # Save artifacts
    Path("app/data").mkdir(exist_ok=True)
    with open(Path("app/data/model.pkl"), "wb") as f:
        pickle.dump({
            "model": model,
            "label_encoder": le_target,
            "scaler": scaler,
            "feature_names": feature_names
        }, f)
    print("Model saved to app/data/model.pkl")

if __name__ == "__main__":
    train()
