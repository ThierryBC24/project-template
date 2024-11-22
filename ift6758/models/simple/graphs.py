import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_curve, auc
from sklearn.calibration import calibration_curve
import matplotlib.pyplot as plt

# Charger les données
play_by_play_path = Path(__file__).parent.parent.parent.parent / "data" / "dataframe_2016_to_2019.csv"
play_by_play = pd.read_csv(play_by_play_path)
play_by_play = play_by_play.loc[play_by_play["gameType"] == "regular-season"].dropna()

# Variables indépendantes (features) : distance, angle
X_distance = play_by_play.iloc[:, 26:27]  # Distance
X_angle = play_by_play.iloc[:, 27:28]  # Angle 
X_both = play_by_play.iloc[:, 26:28]  # Distance et angle

# Variable cible
y = play_by_play["isGoal"]

# Fonction pour entraîner un modèle et récupérer les prédictions
def train_model(X, y):
    X_train, X_validate, y_train, y_validate = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LogisticRegression()
    model.fit(X_train, y_train)
    prob = model.predict_proba(X_validate)[:, 1]
    return prob, y_validate

# Obtenir les probabilités et les vraies étiquettes pour chaque modèle
prob_distance, y_validate = train_model(X_distance, y)
prob_angle, _ = train_model(X_angle, y)
prob_both, _ = train_model(X_both, y)

# Générer une ligne de base aléatoire (probabilités uniformes)
np.random.seed(42)
prob_random = np.random.uniform(0, 1, size=len(y_validate))

# **1. Courbe ROC et AUC**
plt.figure(figsize=(8, 6))
for name, prob in [
    ("Distance", prob_distance),
    ("Angle", prob_angle),
    ("Distance + Angle", prob_both),
    ("Aléatoire", prob_random),
]:
    fpr, tpr, _ = roc_curve(y_validate, prob)
    roc_auc = auc(fpr, tpr)
    plt.plot(fpr, tpr, label=f"{name} (AUC = {roc_auc:.2f})")

# Ajouter une ligne de base pour le classificateur aléatoire
#plt.plot([0, 1], [0, 1], "k--", label="Deviner au hasard")
plt.xlabel("Taux de faux positifs (FPR)")
plt.ylabel("Taux de vrais positifs (TPR)")
plt.title("Courbe ROC")
plt.legend()
plt.grid()
plt.show()

# **2. Taux de buts par centile**
plt.figure(figsize=(8, 6))
for name, prob in [
    ("Distance", prob_distance),
    ("Angle", prob_angle),
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
        for i in range(len(percentiles)-1)
    ]
    plt.plot(np.arange(0, 100, 10), [rate * 100 for rate in goal_rates], label=name)

plt.xlabel("Centile de la probabilité prédite")
plt.ylabel("Taux de buts (%)")
plt.title("Taux de buts par centile de probabilité")
plt.ylim(0, 100)
plt.grid()
plt.legend()
plt.gca().invert_xaxis()  # Inverser l'axe X pour aller de 100% à 0%
plt.show()

# **3. Proportion cumulée des buts**
plt.figure(figsize=(8, 6))
for name, prob in [
    ("Distance", prob_distance),
    ("Angle", prob_angle),
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
plt.show()

# **4. Diagramme de fiabilité**
models = [
    ("Distance", prob_distance),
    ("Angle", prob_angle),
    ("Distance + Angle", prob_both),
    ("Aléatoire", prob_random),
]

for name, prob in models:
    fraction_of_positives, mean_predicted_value = calibration_curve(
        y_validate, prob, n_bins=10, strategy="quantile"
    )
    print(fraction_of_positives,mean_predicted_value)
    plt.plot(mean_predicted_value, fraction_of_positives, label=name)

plt.plot([0, 1], [0, 1], "k--", label="Calibration parfaite")

plt.title("Diagramme de fiabilité (Calibration)")
plt.xlabel("Probabilités prédites")
plt.ylabel("Fréquence observée (empirique)")
plt.legend()
plt.grid()
plt.show()

