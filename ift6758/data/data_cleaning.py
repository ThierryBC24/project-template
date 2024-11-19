import pandas as pd


def clean_data(raw_data):
    """
    Clean the raw data and return dictionaries of cleaned games.
    :param raw_data: NHLData object containing the raw data.
    :return: Tuple of dictionaries (regular season and playoffs).
    """
    regular_season = {
        year: [convert_game_to_dataframe(game) for game in raw_data.regular_season[year]]
        for year in raw_data.regular_season.keys()
    }
    playoff = {
        year: [convert_game_to_dataframe(game) for game in raw_data.playoffs[year]]
        for year in raw_data.playoffs.keys()
    }
    return regular_season, playoff


def convert_game_to_dataframe(game):
    """
    Convert a single game's data to a DataFrame, capturing all required columns.
    :param game: Dictionary containing game data.
    :return: DataFrame with the game's data.
    """
    rows = []
    for play in game.get("plays", []):
        # Filtrer uniquement les événements pertinents
        if play.get("typeDescKey") not in {"shot-on-goal", "goal", "missed-shot", "blocked-shot"}:
            continue

        details = play.get("details", {})
        previous_play = play.get("previousPlay", {})
        
        # Calculs pour les colonnes manquantes ou dérivées
        shot_distance = details.get("distanceToNet", None)
        distance_from_last_event = previous_play.get("distanceFromLastEvent", None)
        speed_from_last_event = (
            distance_from_last_event / previous_play.get("timeSinceLastPlay", 1)
            if distance_from_last_event is not None and previous_play.get("timeSinceLastPlay", 0) > 0
            else 0.0
        )

        row = {
            "Year": game.get("seasonYear"),
            "idGame": game.get("id"),
            "gameType": game.get("type", "regular-season"),
            "periodType": play.get("periodDescriptor", {}).get("type", "Unknown"),
            "numberPeriod": play.get("periodDescriptor", {}).get("number"),
            "typeDescKey": play.get("typeDescKey", "Unknown"),
            "eventOwnerTeam": details.get("eventOwnerTeamId", "Unknown"),
            "gameSeconds": play.get("timeInGame", None),
            "previousEventType": previous_play.get("typeDescKey", "Unknown"),
            "timeSinceLastEvent": previous_play.get("timeSinceLastPlay", 0.0),
            "previousXCoord": previous_play.get("details", {}).get("xCoord", 0.0),
            "previousYCoord": previous_play.get("details", {}).get("yCoord", 0.0),
            "xCoord": details.get("xCoord", 0.0),
            "yCoord": details.get("yCoord", 0.0),
            "zoneShoot": details.get("zoneCode", "Unknown"),
            "shootingPlayer": details.get("scoringPlayerId", details.get("shootingPlayerId")),
            "goaliePlayer": details.get("goalieInNetId"),
            "shotType": details.get("shotType", "Unknown"),
            "teamSide": "home" if play.get("team", {}).get("id") == game.get("homeTeam", {}).get("id") else "away",
            "emptyGoalNet": details.get("emptyNet", 0),
            "isGoalAdvantage": "Advantage" if details.get("goalAdvantage") else "Neutral",
            "isGoal": 1 if play.get("typeDescKey") == "goal" else 0,
            "shotDistance": shot_distance,
            "distanceFromLastEvent": distance_from_last_event,
            "rebound": details.get("rebound", False),
            "speedFromLastEvent": speed_from_last_event,
            "shotAngle": details.get("shotAngle", None),
            "reboundAngleShot": details.get("reboundAngleShot", None),
            "offensivePressureTime": details.get("offensivePressureTime", None),
        }
        rows.append(row)
    
    return pd.DataFrame(rows)




def convert_dictionaries_to_dataframes(data1: dict, data2: dict, years: list) -> pd.DataFrame:
    """
    Combine cleaned dictionaries into a single DataFrame.
    :param data1: Dictionary of regular season games.
    :param data2: Dictionary of playoff games.
    :param years: List of years to include.
    :return: Combined DataFrame.
    """
    df_data1_all = pd.DataFrame()
    df_data2_all = pd.DataFrame()
    df_data12_all = pd.DataFrame()

    for year in years:
        # Concatenate all games for the year
        df_data1 = pd.concat(data1[year], ignore_index=True)
        df_data2 = pd.concat(data2[year], ignore_index=True)

        # Add Year column if it does not exist
        if 'Year' not in df_data1.columns:
            df_data1.insert(0, 'Year', year)
        if 'Year' not in df_data2.columns:
            df_data2.insert(0, 'Year', year)

        # Add gameType column if it does not exist
        if 'gameType' not in df_data1.columns:
            df_data1.insert(2, 'gameType', 'regular-season')
        if 'gameType' not in df_data2.columns:
            df_data2.insert(2, 'gameType', 'playoffs')

        # Combine regular season and playoff data for the year
        df_data12 = pd.concat([df_data1, df_data2], axis=0)

        # Append to cumulative DataFrames
        df_data1_all = pd.concat([df_data1_all, df_data1], axis=0)
        df_data2_all = pd.concat([df_data2_all, df_data2], axis=0)
        df_data12_all = pd.concat([df_data12_all, df_data12], axis=0)

    return df_data12_all
