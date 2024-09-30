import pandas as pd
import requests

from  play_by_play_data import PlayByPlayData

EVENTS = ["goal","shot-on-goal"]
EVENT_KEY = "typeDescKey"

#def read_year_play_by_play()

def clean_raw_data(dataframe: pd.DataFrame) -> list[pd.DataFrame]:
    """
    Function that takes play-by-play data and returns a dataframe
    containing only goal and shot events

    :param dataframe: A raw pandas dataframe
    :returns: A dataframe containing only goals and shots 
    """
    #print(pd.json_normalize(dataframe))
    dataframes = []
    #print(dataframe["awayTeam"])
    for i in range(len(dataframe)):
        home_id = dataframe["homeTeam"][i]["id"]
        away_id = dataframe["awayTeam"][i]["id"]
        
        # key team_id, value name
        team_names = {
            dataframe["awayTeam"][i]["id"]:dataframe["awayTeam"][i]["name"]["default"],
            dataframe["homeTeam"][i]["id"]:dataframe["homeTeam"][i]["name"]["default"] }
        
        # key player_id, value name
        player_names = {
            row["playerId"]: " ".join([row["firstName"]["default"],row["lastName"]["default"]]) for row in dataframe["rosterSpots"][i]
        }
        data = []
        for row in dataframe["plays"][i]:
            if row[EVENT_KEY] == "goal":
                # we need to know if away or home goal
                if row["situationCode"][1] == row["situationCode"][2]:
                    situation = "force egale"

                elif row["situationCode"][1] > row["situationCode"][2]:
                    if row["details"]["eventOwnerTeamId"] == away_id:
                        situation = "avantage numerique"
                    else:
                        situation = "desavantage numerique"
                else:
                    if row["details"]["eventOwnerTeamId"] == away_id:
                        situation = "desavantage numerique"
                    else:
                        situation = "avantage numerique"

                data.append({
                    "Type": "But",
                    "Periode" : row["periodDescriptor"]["number"],
                    "Temps": row["timeInPeriod"],
                    "Equipe": team_names[row["details"]["eventOwnerTeamId"]],
                    "xCoord": row["details"].get("xCoord"),
                    "yCoord": row["details"].get("yCoord"),
                    "Type de tir" : row["details"].get("shotType"),
                    "Situation": situation,
                    "Joueur" : player_names[row["details"]["scoringPlayerId"]],
                    "Gardien de but" : player_names.get(row["details"].get("goalieInNetId")),
                    }

                )
            elif row[EVENT_KEY] == "shot-on-goal":
                
                
                data.append({
                    "Type": "Tir au but",
                    "Periode" : row["periodDescriptor"]["number"],
                    "Temps": row["timeInPeriod"],
                    "Equipe": team_names[row["details"]["eventOwnerTeamId"]],
                    "xCoord": row["details"].get("xCoord"),
                    "yCoord": row["details"].get("yCoord"),
                    "Type de tir" :row["details"].get("shotType"),
                    "Situation": row["situationCode"],
                    "Joueur": player_names[row["details"]["shootingPlayerId"]],
                    "Gardien de but" : player_names.get(row["details"].get("goalieInNetId"),None),
                }
                )
        dataframes.append(pd.DataFrame(data=data))
    return dataframes

def fetch_season_data(season: int) -> pd.DataFrame:
        """
        Fetch the play-by-play data of a season from the NHL's API

        :param season: Season (ex: 2022 for the 2022-2023 season)
        :return: DataFrame
        """
        # Only fetch regular season and playoffs
        game_types = ['02', '03']
        data = []

        for game_type in game_types:
            game_number = 1 
            while True:
                # Format the game number as a 4-digit string
                game_number_str = f'{game_number:04d}'
                url = f'https://api-web.nhle.com/v1/gamecenter/{season}{game_type}{game_number_str}/play-by-play'
                response = requests.get(url)

                # Break the loop if the response is a 404 error (no more games)
                if response.status_code == 404:
                    break

                # Append the JSON response data if successful
                elif response.status_code == 200:
                    data.append(response.json())


                game_number += 1

        # Convert data to DataFrame and return
        return pd.DataFrame(data)

if __name__ == "__main__":
    print("lol")
    #print(clean_raw_data(fetch_season_data(2022))[0])
    #print(fetch_season_data(2022)[0])
    play_by_play_data = PlayByPlayData(base_path=".")
    lol = play_by_play_data.get_data(2019)
    #print(lol)
    dfs = clean_raw_data(lol) 
    first = dfs[0]
    print(first.head(10))
    

# l'heure/la période de jeu
# l'identifiant du jeu
# les informations sur l'équipe (quelle équipe a tiré) 
# s'il s'agit d'un tir ou d'un but
# les coordonnées sur la glace
# le nom du tireur et du gardien de but (ne vous inquiétez pas des assists pour l'instant) 
# le type de tir
# si c'était sur un filet vide
# si un but était à force égale en désavantage numérique ou en avantage numérique.


## test

