import pandas as pd


def get_player(game_nhl: dict) -> pd.DataFrame:
    
    df_players = pd.DataFrame(game_nhl['rosterSpots'])[['playerId', 'firstName', 'lastName']]
    df_players['firstName'] = df_players['firstName'].apply(lambda x: x['default'])
    df_players['lastName'] = df_players['lastName'].apply(lambda x: x['default'])
    return df_players


def get_teams(game_nhl: dict) -> pd.DataFrame:
    home_team = {'teamId': game_nhl['homeTeam']['id'], 'teamName': game_nhl['homeTeam']['name']['default'],
                 'teamSide': 'home'}
    away_team = {'teamId': game_nhl['awayTeam']['id'], 'teamName': game_nhl['awayTeam']['name']['default'],
                 'teamSide': 'away'}
    return pd.DataFrame([home_team, away_team])
