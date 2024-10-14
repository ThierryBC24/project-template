import os
import json
import pandas as pd
from typing import List

class PlayByPlayCleaner:
    def __init__(self, base_path: str):
        """
        Initialize with the base path where the JSON data is stored.

        :param base_path: Path to the directory where the JSON files are saved.
        """
        self.base_path = base_path

    def load_data(self) -> list:
        """
        Load all JSON files in the base path and return the combined data as a list.

        :return: Combined data from all seasons
        """
        all_data = []
        for file in os.listdir(self.base_path):
            if file.endswith('.json'):
                file_path = os.path.join(self.base_path, file)
                with open(file_path, 'r') as json_file:
                    data = json.load(json_file)
                    all_data.extend(data)
        return all_data

    def clean_raw_data(self, data: list) -> List[pd.DataFrame]:
        """
        Function that takes play-by-play data (a list of game dictionaries) and returns a list of dataframes
        containing only goal and shot events.

        :param data: A list of dictionaries representing all games for a season.
        :returns: A list of dataframes containing only goals and shots.
        """
        dataframes = []
        for game in data:
            game_id = game["id"]
            home_id = game["homeTeam"]["id"]
            away_id = game["awayTeam"]["id"]
            
            # key team_id, value name
            team_names = {
                game["awayTeam"]["id"]: game["awayTeam"]["name"]["default"],
                game["homeTeam"]["id"]: game["homeTeam"]["name"]["default"]
            }
            
            # key player_id, value name
            player_names = {
                player["playerId"]: " ".join([player["firstName"]["default"], player["lastName"]["default"]])
                for player in game.get("rosterSpots", [])
            }

            data_rows = []
            for play in game["plays"]:
                if play["typeDescKey"] in {"goal", "shot-on-goal"}:
                    event_details = play.get("details", {})
                    event_owner_team_id = event_details.get("eventOwnerTeamId")
                    event_data = {
                        "idGame": game_id,
                        "Type": "But" if play["typeDescKey"] == "goal" else "Tir au but",
                        "Periode": play["periodDescriptor"]["number"],
                        "Temps": play["timeInPeriod"],
                        "Equipe": team_names.get(event_owner_team_id, "Unknown"),
                        "xCoord": event_details.get("xCoord"),
                        "yCoord": event_details.get("yCoord"),
                        "Type de tir": event_details.get("shotType"),
                        "Joueur": player_names.get(
                            event_details.get("scoringPlayerId", event_details.get("shootingPlayerId")),
                            "Inconnu"
                        ),
                        "Gardien de but": player_names.get(event_details.get("goalieInNetId"), "Vide"),
                        "emptyNet": event_details.get("emptyNet", False),
                    }

                    # Déterminer la situation (force égale, avantage numérique, etc.)
                    if play["typeDescKey"] == "goal":
                        if play["situationCode"][1] == play["situationCode"][2]:
                            event_data["Situation"] = "force egale"
                        elif play["situationCode"][1] > play["situationCode"][2]:
                            event_data["Situation"] = (
                                "avantage numerique" if event_owner_team_id == away_id else "desavantage numerique"
                            )
                        else:
                            event_data["Situation"] = (
                                "desavantage numerique" if event_owner_team_id == away_id else "avantage numerique"
                            )
                    else:
                        event_data["Situation"] = play["situationCode"]

                    data_rows.append(event_data)

            dataframes.append(pd.DataFrame(data=data_rows))

        return dataframes

if __name__ == "__main__":
    cleaner = PlayByPlayCleaner(base_path="play_by_play_data")
    data = cleaner.load_data()
    
    cleaned_dataframes = cleaner.clean_raw_data(data)
    combined_data = pd.concat(cleaned_dataframes, ignore_index=True)
    print(combined_data.head(10))
    
    combined_data.to_csv("combined_play_by_play_cleaned.csv", index=False)
