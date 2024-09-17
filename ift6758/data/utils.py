import pandas as pd

EVENTS = ["goal","shot-on-goal"]
EVENT_KEY = "typeDescKey"

def clean_raw_data(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Function that takes play-by-play data and returns a dataframe
    containing only goal and shot events

    :param dataframe: A raw pandas dataframe
    :returns: A dataframe containing only goals and shots 
    """
    # key team_id, value name
    team_names = {
        dataframe["awayTeam"]["id"]:dataframe["awayTeam"]["name"]["default"],
         dataframe["homeTeam"]["id"]:dataframe["homeTeam"]["name"]["default"] }
    
    # key player_id, value name
    player_names = {

    }
    data = []
    for row in dataframe["plays"]:
        if row[EVENT_KEY] in EVENTS:
            data.append(
                row["periodDescriptor"]["number"],
                row["timeInPeriod"],
                team_names[row["details"]["eventOwnerTeamId"]],
                row[EVENT_KEY],
                row["details"]["xCoord"],
                row["details"]["yCoord"],
            )

    return pd.DataFrame(data=data)

# l'heure/la période de jeu
# l'identifiant du jeu
# les informations sur l'équipe (quelle équipe a tiré) 
# s'il s'agit d'un tir ou d'un but
# les coordonnées sur la glace
# le nom du tireur et du gardien de but (ne vous inquiétez pas des assists pour l'instant) 
# le type de tir
# si c'était sur un filet vide
# si un but était à force égale en désavantage numérique ou en avantage numérique.

