import os
import json
import pandas as pd
from typing import List, Dict, Union

class PlayByPlayCleaner:
    def __init__(self, base_path: str):
        """
        Initialize with the base path where the JSON data is stored.
        :param base_path: Path to the directory where the JSON files are saved.
        """
        self.base_path = base_path

    def load_data(self) -> List[Dict]:
        """
        Load and process JSON files one by one.
        :yield: Data from each JSON file one at a time.
        """
        for file in os.listdir(self.base_path):
            if file.endswith('.json'):
                file_path = os.path.join(self.base_path, file)
                with open(file_path, 'r') as json_file:
                    data = json.load(json_file)
                    yield data

    def clean_raw_data(self, data: Union[List[Dict], Dict]) -> List[pd.DataFrame]:
        """
        Cleans raw play-by-play data by extracting relevant columns and handling missing data.
        :param data: A list of dictionaries representing all games for a season.
        :return: A list of cleaned DataFrames.
        """
        dataframes = []
        
        for game in data:
            # Extraire les informations globales du match
            game_id = game.get("id", None)
            home_team = game.get("homeTeam", {}).get("name", {}).get("default", "Unknown")
            away_team = game.get("awayTeam", {}).get("name", {}).get("default", "Unknown")

            player_names = {
                player["playerId"]: " ".join([player["firstName"]["default"], player["lastName"]["default"]])
                for player in game.get("rosterSpots", [])
            }

            rows = []
            for play in game.get("plays", []):
                if play.get("typeDescKey") in {"goal", "shot-on-goal"}:
                    details = play.get("details", {})
                    event_team = details.get("eventOwnerTeamId", None)

                    # Construire la ligne de données
                    row = {
                        "idGame": game_id,
                        "Type": "But" if play["typeDescKey"] == "goal" else "Tir au but",
                        "Periode": play.get("periodDescriptor", {}).get("number", None),
                        "Temps": play.get("timeInPeriod", None),
                        "Equipe": home_team if event_team == game.get("homeTeam", {}).get("id") else away_team,
                        "xCoord": details.get("xCoord", None),
                        "yCoord": details.get("yCoord", None),
                        "zoneCode": details.get("zoneCode", "Unknown"),
                        "Type de tir": details.get("shotType", "Unknown"),
                        "Joueur": player_names.get(details.get("scoringPlayerId", details.get("shootingPlayerId")), "Inconnu"),
                        "Gardien de but": player_names.get(details.get("goalieInNetId"), "Inconnu"),
                        "emptyNet": details.get("emptyNet", False),
                        "Situation": self._determine_situation(play, event_team, game)
                    }
                    rows.append(row)

            if rows:
                dataframes.append(pd.DataFrame(rows))

        return dataframes

    def _determine_situation(self, play: Dict, event_team: int, game: Dict) -> str:
        """
        Determine the game situation (e.g., power play, even strength).
        :param play: Dictionary with play details.
        :param event_team: Team that owns the event.
        :param game: Game dictionary with team details.
        :return: String representing the situation.
        """
        home_id = game.get("homeTeam", {}).get("id")
        away_id = game.get("awayTeam", {}).get("id")

        if play["typeDescKey"] == "goal":
            if play["situationCode"][1] == play["situationCode"][2]:
                return "force egale"
            elif play["situationCode"][1] > play["situationCode"][2]:
                return "avantage numerique" if event_team == away_id else "desavantage numerique"
            else:
                return "desavantage numerique" if event_team == away_id else "avantage numerique"
        else:
            return play.get("situationCode", "Inconnu")

if __name__ == "__main__":
    cleaner = PlayByPlayCleaner(base_path="/home/mohamed/project-template/play_by_play_data")

    # Collect and process data incrementally
    dataframes = []
    for game_data in cleaner.load_data():
        cleaned_dataframes = cleaner.clean_raw_data(game_data)
        dataframes.extend(cleaned_dataframes)

    # Combiner toutes les données nettoyées
    combined_data = pd.concat(dataframes, ignore_index=True)

    # Vérifier et gérer les colonnes manquantes
    expected_columns = [
        "idGame", "Type", "Periode", "Temps", "Equipe", "xCoord", "yCoord", 
        "zoneCode", "Type de tir", "Joueur", "Gardien de but", "emptyNet", "Situation"
    ]
    for col in expected_columns:
        if col not in combined_data.columns:
            combined_data[col] = "Inconnu"

    # Sauvegarder les données combinées
    combined_data.to_csv("combined_play_by_play_cleaned.csv", index=False)

    # Afficher les premières lignes pour vérifier
    print(combined_data.head(10))
