import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_curve, auc
from sklearn.calibration import calibration_curve
from xgboost import XGBClassifier
import matplotlib.pyplot as plt
import wandb

# Initialiser un projet WandB
wandb.init(project="XGBoost distance angle", config={
        "architecture": "Tree",
        "dataset": "play-by-play-regular-season-2016-2019",
        "test_size": 0.2,
        "random_state": 42,
    },)

# Charger les données
play_by_play_path = Path(__file__).parent.parent.parent.parent / "data" / "dataframe_2016_to_2019.csv"
play_by_play = pd.read_csv(play_by_play_path)
play_by_play = play_by_play.loc[play_by_play["gameType"] == "regular-season"].dropna()

# Variables indépendantes (features) : Distance + Angle
X_both = play_by_play.iloc[:, 26:28]  # Distance et Angle
y = play_by_play["isGoal"]

# Fonction pour entraîner un modèle XGBoost et récupérer les prédictions
def train_model(X, y):
    X_train, X_validate, y_train, y_validate = train_test_split(X, y, test_size=0.2, random_state=42)
    model = XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
    
    model.fit(X_train, y_train)
    prob = model.predict_proba(X_validate)[:, 1]
    
    # Loguer les paramètres du modèle
    wandb.log({"learning_rate": model.get_params()['learning_rate'],
               "n_estimators": model.get_params()['n_estimators'],
               "max_depth": model.get_params()['max_depth']})
    wandb.log_model(path=Path(__file__),name="XGBoost_dist_angle")
    return prob, y_validate

# Entraîner le modèle pour "Distance + Angle"
prob_both, y_validate = train_model(X_both, y)

# Générer une ligne de base aléatoire (probabilités uniformes)
np.random.seed(42)
prob_random = np.random.uniform(0, 1, size=len(y_validate))

# **1. Courbe ROC et AUC**
plt.figure(figsize=(8, 6))
for name, prob in [
    ("Distance + Angle", prob_both),
    ("Aléatoire", prob_random),
]:
    fpr, tpr, _ = roc_curve(y_validate, prob)
    roc_auc = auc(fpr, tpr)
    plt.plot(fpr, tpr, label=f"{name} (AUC = {roc_auc:.2f})")

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
for name, prob in [
    ("Distance + Angle", prob_both),
    ("Aléatoire", prob_random),
]:
    # Trier les probabilités et les étiquettes correspondantes
    sorted_indices = np.argsort(prob)
    prob_sorted = prob[sorted_indices]
    y_sorted = np.array(y_validate)[sorted_indices]

    # Calculer les taux de buts par centile
    percentiles = np.percentile(prob_sorted, np.arange(0, 101, 10))
    goal_rates = [
        y_sorted[(prob_sorted >= percentiles[i]) & (prob_sorted < percentiles[i + 1])].mean()
        for i in range(len(percentiles) - 1)
    ]
    plt.plot(np.arange(0, 100, 10), [rate * 100 for rate in goal_rates], label=name)

plt.xlabel("Centile de la probabilité prédite")
plt.ylabel("Taux de buts (%)")
plt.title("Taux de buts par centile de probabilité")
plt.ylim(0, 100)
plt.grid()
plt.legend()
plt.gca().invert_xaxis()

# Loguer le graphique du taux de buts par centile
wandb.log({"goal_rate_by_percentile": wandb.Image(plt)})
plt.show()

# **3. Proportion cumulée des buts**
plt.figure(figsize=(8, 6))
for name, prob in [
    ("Distance + Angle", prob_both),
    ("Aléatoire", prob_random),
]:
    # Trier par probabilité décroissante
    sorted_indices = np.argsort(prob)[::-1]
    y_sorted = np.array(y_validate)[sorted_indices]

    # Calculer la proportion cumulée des buts
    cumulative_goals = np.cumsum(y_sorted)
    total_goals = np.sum(y_sorted)
    cumulative_goal_proportion = cumulative_goals / total_goals

    # Centiles
    centiles = np.linspace(100, 0, len(cumulative_goal_proportion))
    plt.plot(centiles, cumulative_goal_proportion * 100, label=name)

plt.xlabel("Centile de la probabilité prédite")
plt.ylabel("Proportion cumulée des buts (%)")
plt.title("Proportion cumulée des buts par centile de probabilité")
plt.ylim(0, 100)
plt.grid()
plt.legend()
plt.gca().invert_xaxis()

# Loguer la proportion cumulée des buts
wandb.log({"cumulative_goal_proportion": wandb.Image(plt)})
plt.show()

# **4. Diagramme de fiabilité**
plt.figure(figsize=(8, 6))
for name, prob in [
    ("Distance + Angle", prob_both),
    ("Aléatoire", prob_random),
]:
    fraction_of_positives, mean_predicted_value = calibration_curve(
        y_validate, prob, n_bins=10, strategy="quantile"
    )
    plt.plot(mean_predicted_value, fraction_of_positives, label=name)

plt.plot([0, 1], [0, 1], "k--", label="Calibration parfaite")
plt.title("Diagramme de fiabilité (Calibration)")
plt.xlabel("Probabilités prédites")
plt.ylabel("Fréquence observée (empirique)")
plt.legend()
plt.grid()

# Loguer le diagramme de fiabilité
wandb.log({"calibration_plot": wandb.Image(plt)})
plt.show()

# Fin de l'enregistrement dans WandB
wandb.finish()
