import pandas as pd
from play_by_play_data import PlayByPlayData

EVENT_KEY = "typeDescKey"

def clean_raw_data(data: list) -> list[pd.DataFrame]:
    """
    Function that takes play-by-play data (a list of game dictionaries) and returns a list of dataframes
    containing only goal and shot events.

    :param data: A list of dictionaries representing all games for a season.
    :returns: A list of dataframes containing only goals and shots.
    """
    dataframes = []
    for game in data:
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
            for player in game["rosterSpots"]
        }

        data_rows = []
        for play in game["plays"]:
            if play[EVENT_KEY] == "goal":
                # Determine the situation (even strength, power play, etc.)
                if play["situationCode"][1] == play["situationCode"][2]:
                    situation = "force egale"
                elif play["situationCode"][1] > play["situationCode"][2]:
                    if play["details"]["eventOwnerTeamId"] == away_id:
                        situation = "avantage numerique"
                    else:
                        situation = "desavantage numerique"
                else:
                    if play["details"]["eventOwnerTeamId"] == away_id:
                        situation = "desavantage numerique"
                    else:
                        situation = "avantage numerique"

                data_rows.append({
                    "Type": "But",
                    "Periode": play["periodDescriptor"]["number"],
                    "Temps": play["timeInPeriod"],
                    "Equipe": team_names[play["details"]["eventOwnerTeamId"]],
                    "xCoord": play["details"].get("xCoord"),
                    "yCoord": play["details"].get("yCoord"),
                    "Type de tir": play["details"].get("shotType"),
                    "Situation": situation,
                    "Joueur": player_names[play["details"]["scoringPlayerId"]],
                    "Gardien de but": player_names.get(play["details"].get("goalieInNetId"), "Vide"),
                })
            elif play[EVENT_KEY] == "shot-on-goal":
                data_rows.append({
                    "Type": "Tir au but",
                    "Periode": play["periodDescriptor"]["number"],
                    "Temps": play["timeInPeriod"],
                    "Equipe": team_names[play["details"]["eventOwnerTeamId"]],
                    "xCoord": play["details"].get("xCoord"),
                    "yCoord": play["details"].get("yCoord"),
                    "Type de tir": play["details"].get("shotType"),
                    "Situation": play["situationCode"],
                    "Joueur": player_names[play["details"]["shootingPlayerId"]],
                    "Gardien de but": player_names.get(play["details"].get("goalieInNetId"), "Vide"),
                })

        dataframes.append(pd.DataFrame(data=data_rows))

    return dataframes

if __name__ == "__main__":
    play_by_play_data = PlayByPlayData(base_path=".")
    
    # Liste pour stocker les DataFrames de toutes les saisons
    all_seasons_data = []

    # Boucle sur les saisons de 2016 à 2023
    for season in range(2016, 2024):
        print(f"Processing season {season}...")
        season_data = play_by_play_data.get_data(season)
        
        if season_data is None:
            print(f"No data found for the season {season}.")
        else:
            # Nettoyer les données de la saison en cours
            season_cleaned_dfs = clean_raw_data(season_data)
            
            # Concaténer toutes les DataFrames d'une saison dans une seule DataFrame
            full_season_df = pd.concat(season_cleaned_dfs, ignore_index=True)
            
            # Ajouter cette DataFrame à la liste de toutes les saisons
            all_seasons_data.append(full_season_df)
    
    # Concaténer les données de toutes les saisons
    combined_data = pd.concat(all_seasons_data, ignore_index=True)

    # Afficher les premières lignes des données combinées
    print(combined_data.head(10))
    
    # Si besoin, enregistrer les données combinées dans un fichier CSV
    combined_data.to_csv("combined_play_by_play_2016_2023.csv", index=False)
