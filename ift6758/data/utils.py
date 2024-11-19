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

    def load_data(self, seasons: List[int] = None) -> List[Dict]:
        """
        Load and process JSON files for specific seasons.
        If no seasons are specified, load all available data.

        :param seasons: List of seasons to load (e.g., [2016, 2017]).
        :yield: Data from each JSON file for the specified seasons.
        """
        for file in os.listdir(self.base_path):
            if file.endswith('.json'):
                # If seasons are provided, filter files by season; otherwise, load all files
                if seasons is None or any(str(season) in file for season in seasons):
                    file_path = os.path.join(self.base_path, file)
                    try:
                        with open(file_path, 'r') as json_file:
                            data = json.load(json_file)
                            yield data
                    except json.JSONDecodeError as e:
                        print(f"Error reading JSON file {file}: {e}")
                        continue

    def clean_raw_data(self, data: Union[List[Dict], Dict]) -> List[pd.DataFrame]:
        """
        Clean raw play-by-play data by extracting relevant columns and handling missing data.

        :param data: A list of dictionaries representing all games for a season.
        :return: A list of cleaned DataFrames.
        """
        dataframes = []
        for game in data:
            rows = []
            game_id = game.get("id", None)
            season_year = game.get("seasonYear", None)

            for play in game.get("plays", []):
                details = play.get("details", {})
                row = {
                    "Year": season_year,
                    "idGame": game_id,
                    "gameType": game.get("type", "regular-season"),
                    "periodType": play.get("periodDescriptor", {}).get("type", "Unknown"),
                    "numberPeriod": play.get("periodDescriptor", {}).get("number", None),
                    "typeDescKey": play.get("typeDescKey", "Unknown"),
                    "eventOwnerTeam": play.get("eventOwner", {}).get("name", {}).get("default", "Unknown"),
                    "gameSeconds": play.get("timeInGame", None),
                    "previousEventType": play.get("previousPlay", {}).get("typeDescKey", "Unknown"),
                    "timeSinceLastEvent": play.get("previousPlay", {}).get("timeSinceLastPlay", 0.0),
                    "previousXCoord": play.get("previousPlay", {}).get("details", {}).get("xCoord", None),
                    "previousYCoord": play.get("previousPlay", {}).get("details", {}).get("yCoord", None),
                    "xCoord": details.get("xCoord", None),
                    "yCoord": details.get("yCoord", None),
                    "zoneShoot": details.get("zoneCode", "Unknown"),
                    "shootingPlayer": details.get("scoringPlayerId", details.get("shootingPlayerId")),
                    "goaliePlayer": details.get("goalieInNetId"),
                    "shotType": details.get("shotType", "Unknown"),
                    "teamSide": "home" if play.get("team", {}).get("id") == game.get("homeTeam", {}).get("id") else "away",
                    "emptyGoalNet": details.get("emptyNet", 0),
                    "isGoalAdvantage": "Advantage" if details.get("goalAdvantage") else "Neutral",
                    "isGoal": 1 if play.get("typeDescKey") == "goal" else 0,
                    "shotDistance": details.get("distanceToNet", None),
                    "distanceFromLastEvent": play.get("distanceFromLastEvent", None),
                    "rebound": details.get("rebound", False),
                    "speedFromLastEvent": play.get("speedFromLastEvent", None),
                    "shotAngle": details.get("shotAngle", None),
                    "reboundAngleShot": details.get("reboundAngleShot", None),
                    "offensivePressureTime": details.get("offensivePressureTime", None),
                }
                rows.append(row)

            if rows:
                dataframes.append(pd.DataFrame(rows))
        return dataframes

    def combine_dataframes(self, dataframes: List[pd.DataFrame]) -> pd.DataFrame:
        """
        Combine a list of DataFrames into a single DataFrame.

        :param dataframes: List of DataFrames to combine.
        :return: Combined DataFrame.
        """
        if not dataframes:
            print("No dataframes to combine.")
            return pd.DataFrame()

        combined_df = pd.concat(dataframes, ignore_index=True)

        # Ensure all expected columns are present
        expected_columns = [
            "Year", "idGame", "gameType", "periodType", "numberPeriod", "typeDescKey",
            "eventOwnerTeam", "gameSeconds", "previousEventType", "timeSinceLastEvent",
            "previousXCoord", "previousYCoord", "xCoord", "yCoord", "zoneShoot",
            "shootingPlayer", "goaliePlayer", "shotType", "teamSide", "emptyGoalNet",
            "isGoalAdvantage", "isGoal", "shotDistance", "distanceFromLastEvent",
            "rebound", "speedFromLastEvent", "shotAngle", "reboundAngleShot",
            "offensivePressureTime"
        ]
        for col in expected_columns:
            if col not in combined_df.columns:
                combined_df[col] = None

        return combined_df


if __name__ == "__main__":
    cleaner = PlayByPlayCleaner(base_path="/home/mohamed/project-template/play_by_play_data")

    # List of seasons to process
    seasons = [2016, 2017, 2018, 2019]

    # Load and clean data
    dataframes = []
    for season in seasons:
        for game_data in cleaner.load_data([season]):
            cleaned_dataframes = cleaner.clean_raw_data(game_data)
            dataframes.extend(cleaned_dataframes)

    # Combine all cleaned data
    combined_data = cleaner.combine_dataframes(dataframes)

    # Save combined data to a CSV file
    output_path = "/home/mohamed/project-template/combined_play_by_play_1619.csv"
    combined_data.to_csv(output_path, index=False)

    # Display first few rows for verification
    print(combined_data.head(10))
