import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.calibration import calibration_curve
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.metrics import roc_curve, auc
from sklearn.feature_selection import VarianceThreshold, SelectKBest, f_classif
import matplotlib.pyplot as plt
import wandb
from xgboost import XGBClassifier
import shap

# Initialiser un projet WandB
wandb.init(project="XGBoost all features", config={
        "architecture": "Tree",
        "dataset": "play-by-play-regular-season-2016-2019",
        "test_size": 0.2,
        "random_state": 42,
    },)


# Charger les données
data_path = Path(__file__).parent.parent.parent.parent / "data" / "dataframe_2016_to_2019.csv"
data = pd.read_csv(data_path)

# Filtrer les données pour les matchs de saison régulière et supprimer les lignes manquantes
data = data.loc[data["gameType"] == "regular-season"].dropna()

# Encodage des variables catégoriques
def encode_and_bind(df, feature):
    dummies = pd.get_dummies(df[feature], prefix=feature)
    return pd.concat([df.drop(columns=feature), dummies], axis=1)

# Préparer les caractéristiques et la cible 26 27 
# Supprimer les colonnes non pertinentes
X = data.drop(data.columns[[1, 2, 3, 5, 6, 14, 15, 16, 18, 19, 20, 21]], axis=1)
features_to_encode = ["previousEventType", "shotType"]

# Appliquer l'encodage sur les caractéristiques sélectionnées
for feature in features_to_encode:
    X = encode_and_bind(X, feature)

y = data["isGoal"]

# Fonction pour entraîner un modèle et récupérer les probabilités prédites
def train_model(X, y):
    X_train, X_validate, y_train, y_validate = train_test_split(X, y, test_size=0.2, random_state=42)
    model = XGBClassifier(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=7,
        subsample=0.8,
        objective="binary:logistic",
        eval_metric="logloss",
        random_state=42
    )
    model.fit(X_train, y_train)

        # Loguer les paramètres du modèle
    wandb.log({"learning_rate": model.get_params()['learning_rate'],
               "n_estimators": model.get_params()['n_estimators'],
               "max_depth": model.get_params()['max_depth']})
    wandb.log_model(path=Path(__file__),name="XGBoost_selected_features")

    # SHAP pour interpréter les contributions des caractéristiques
    explainer = shap.Explainer(model)
    shap_values = explainer(X)
    shap.summary_plot(shap_values, X)

    # Prédire les probabilités sur l'ensemble de validation
    prob = model.predict_proba(X_validate)[:, 1]
    return prob, y_validate

# Entraîner le modèle
probabilities, y_validate = train_model(X, y)

# Générer une base aléatoire pour comparaison
np.random.seed(42)
random_probabilities = np.random.uniform(0, 1, size=len(y_validate))

# **1. Courbe ROC et AUC**
plt.figure(figsize=(8, 6))
for label, prob in [("Modèle (toutes caractéristiques)", probabilities), ("Aléatoire", random_probabilities)]:
    fpr, tpr, _ = roc_curve(y_validate, prob)
    roc_auc = auc(fpr, tpr)
    plt.plot(fpr, tpr, label=f"{label} (AUC = {roc_auc:.2f})")
plt.xlabel("Taux de faux positifs (FPR)")
plt.ylabel("Taux de vrais positifs (TPR)")
plt.title("Courbe ROC")
plt.legend()
plt.grid()

# Loguer le graphique ROC sur WandB
wandb.log({"roc_curve": wandb.Image(plt)})
plt.show()

# **2. Taux de buts par centile**
plt.figure(figsize=(8, 6))
for label, prob in [("Modèle (toutes caractéristiques)", probabilities), ("Aléatoire", random_probabilities)]:
    sorted_indices = np.argsort(prob)
    prob_sorted = prob[sorted_indices]
    y_sorted = np.array(y_validate)[sorted_indices]

    percentiles = np.percentile(prob_sorted, np.arange(0, 101, 10))
    goal_rates = [
        y_sorted[(prob_sorted >= percentiles[i]) & (prob_sorted < percentiles[i + 1])].mean()
        for i in range(len(percentiles) - 1)
    ]
    plt.plot(np.arange(0, 100, 10), [rate * 100 for rate in goal_rates], label=label)

plt.xlabel("Centile de probabilité prédite")
plt.ylabel("Taux de buts (%)")
plt.title("Taux de buts par centile")
plt.ylim(0, 100)
plt.grid()
plt.legend()
plt.gca().invert_xaxis()

# Loguer le graphique du taux de buts par centile
wandb.log({"goal_rate_by_percentile": wandb.Image(plt)})
plt.show()


# **3. Proportion cumulée des buts**
plt.figure(figsize=(8, 6))
for label, prob in [("Modèle (toutes caractéristiques)", probabilities), ("Aléatoire", random_probabilities)]:
    sorted_indices = np.argsort(prob)[::-1]
    y_sorted = np.array(y_validate)[sorted_indices]

    cumulative_goals = np.cumsum(y_sorted)
    total_goals = np.sum(y_sorted)
    cumulative_goal_proportion = cumulative_goals / total_goals

    centiles = np.linspace(100, 0, len(cumulative_goal_proportion))
    plt.plot(centiles, cumulative_goal_proportion * 100, label=label)

plt.xlabel("Centile de probabilité prédite")
plt.ylabel("Proportion cumulée des buts (%)")
plt.title("Proportion cumulée des buts")
plt.ylim(0, 100)
plt.grid()
plt.legend()
plt.gca().invert_xaxis()

# Loguer la proportion cumulée des buts
wandb.log({"cumulative_goal_proportion": wandb.Image(plt)})
plt.show()

# **4. Diagramme de fiabilité**
plt.figure(figsize=(8, 6))
for label, prob in [("Modèle (toutes caractéristiques)", probabilities), ("Aléatoire", random_probabilities)]:
    frac_pos, mean_pred = calibration_curve(y_validate, prob, n_bins=10, strategy="quantile")
    plt.plot(mean_pred, frac_pos, label=label)
plt.plot([0, 1], [0, 1], "k--", label="Calibration parfaite")
plt.xlabel("Probabilités prédites")
plt.ylabel("Fréquence observée")
plt.title("Diagramme de fiabilité")
plt.legend()
plt.grid()


# Recherche des hyperparamètres avec GridSearchCV
def perform_grid_search(X, y):
    param_grid = {
        "n_estimators": [50, 100, 200],
        "learning_rate": [0.01, 0.05, 0.1],
        "max_depth": [5, 7, 9],
        "subsample": [0.7, 0.8, 1.0],
    }
    model = XGBClassifier(eval_metric="logloss", random_state=42)
    grid_search = GridSearchCV(model, param_grid, cv=3, scoring="accuracy", n_jobs=-1, verbose=1)
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
    grid_search.fit(X_train, y_train)
    print("Meilleurs hyperparamètres :", grid_search.best_params_)

# Appeler la recherche d'hyperparamètres
perform_grid_search(X, y)

# Loguer le diagramme de fiabilité
wandb.log({"calibration_plot": wandb.Image(plt)})
plt.show()

# Fin de l'enregistrement dans WandB
wandb.finish()
