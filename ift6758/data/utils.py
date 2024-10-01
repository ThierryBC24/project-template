import pandas as pd

from  play_by_play_data import PlayByPlayData

EVENT_KEY = "typeDescKey"


def clean_raw_data(dataframe: pd.DataFrame) -> list[pd.DataFrame]:
    """
    Function that takes play-by-play data and returns a list of dataframes
    containing only goal and shot events

    :param dataframe: A raw pandas dataframe representing all games for a
    :returns: A dataframe containing only goals and shots 
    """
    dataframes = []
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
                    "Gardien de but" : player_names.get(row["details"].get("goalieInNetId"),"Vide"),
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
                    "Gardien de but" : player_names.get(row["details"].get("goalieInNetId"),"Vide"),
                }
                )
        dataframes.append(pd.DataFrame(data=data))
    return dataframes



if __name__ == "__main__":
    play_by_play_data = PlayByPlayData(base_path=".")
    lol = play_by_play_data.get_data(2019)
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

