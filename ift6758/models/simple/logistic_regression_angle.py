import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import wandb

# Initialize WandB for tracking experiment
wandb.init(
    project="Logistic Regression Angle",
    config={
        "architecture": "Cross Validation",
        "dataset": "play-by-play-regular-season-2016-2019",
        "test_size": 0.2,
        "random_state": 42,
    },
)

# Load dataset
play_by_play_path = Path(__file__).parent.parent.parent.parent / "data" / "dataframe_2016_to_2019.csv"
play_by_play = pd.read_csv(play_by_play_path)

# Filter for regular-season games and remove missing values
play_by_play = play_by_play.loc[play_by_play["gameType"] == "regular-season"].dropna()

# Select features and target
X = play_by_play.iloc[:, 26:27]  # Shot distance (for example)
y = play_by_play["isGoal"]

# Split dataset into training and validation sets
X_train, X_validate, y_train, y_validate = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a logistic regression model
model = LogisticRegression()
model.fit(X_train, y_train)

# Make predictions and calculate probabilities
y_pred = model.predict(X_validate)

# Calculate accuracy
accuracy = accuracy_score(y_validate, y_pred)

# Log accuracy to WandB
wandb.log({"accuracy": accuracy})

wandb.log_model(path=Path(__file__),name="Logistic_regression_angle")

# Finish WandB session
wandb.finish()
