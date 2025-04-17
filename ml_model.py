from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import pandas as pd

def train_liking_model(liked_df, disliked_df, features):
    # Label data
    liked_df = liked_df.copy()
    disliked_df = disliked_df.copy()
    liked_df["liked"] = 1
    disliked_df["liked"] = 0

    training_df = pd.concat([liked_df, disliked_df], ignore_index=True)

    X = training_df[features]
    y = training_df["liked"]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = RandomForestClassifier(random_state=42)
    model.fit(X_scaled, y)

    return model, scaler


def predict_like_scores(model, scaler, candidate_df, features):
    X_candidates = candidate_df[features]
    X_scaled = scaler.transform(X_candidates)
    proba = model.predict_proba(X_scaled)[:, 1]
    return proba
