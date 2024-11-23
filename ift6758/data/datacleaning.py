import pandas as pd

from ift6758.data.vecteurs import *
from ift6758.data.getdata import *
from ift6758.data.dataIng import *
from ift6758.data.utils import *
from ift6758.features.play_by_play import NHLData


def df_convert(game_nhl: dict) -> pd.DataFrame:
    df_pbp = pd.DataFrame(game_nhl['plays'])

    df_players = get_player(game_nhl)
    df_teams = get_teams(game_nhl)

    clean_df = pd.DataFrame(df_pbp[['periodDescriptor', 'timeInPeriod', 'situationCode', 'typeDescKey', 'details']])

    df_period = ing_period(clean_df)
    clean_df.drop('periodDescriptor', axis=1, inplace=True)

    clean_df.insert(0, 'idGame', game_nhl['id'])
    clean_df.insert(1, 'periodType', df_period['periodType'])
    clean_df.insert(3, 'numberPeriod', df_period['numberPeriod'])

    clean_df['gameSeconds'] = time_convert(clean_df, 'timeInPeriod')
    clean_df.drop('timeInPeriod', axis=1, inplace=True)

    clean_df = ing_event_bef(clean_df)

    clean_df = clean_df[(clean_df['typeDescKey'] == 'shot-on-goal') | (clean_df['typeDescKey'] == 'goal')].reset_index(
        drop=True)

    df_details = ing_event(clean_df, df_players)
    clean_df.drop('details', axis=1, inplace=True)

    df_details = pd.merge(df_teams, df_details, left_on='teamId', right_on='eventOwnerTeamId', how='right')

    clean_df['xCoord'] = df_details['xCoord']
    clean_df['yCoord'] = df_details['yCoord']
    clean_df['zoneShoot'] = df_details['zoneCode']
    clean_df['shootingPlayer'] = df_details['shootingPlayer']
    clean_df['goaliePlayer'] = df_details['goaliePlayer']
    clean_df['shotType'] = df_details['shotType']
    clean_df.insert(5, 'eventOwnerTeam', df_details['teamName'])
    clean_df['teamSide'] = df_details['teamSide']

    clean_df['emptyGoalNet'] = empty_goal_func(clean_df).astype(int)
    clean_df['isGoalAdvantage'] = goal_situation(clean_df)

    clean_df['isGoal'] = clean_df['typeDescKey'].apply(lambda x: 1 if x == 'goal' else 0)

    clean_df = zoneshoot(clean_df)

    clean_df.drop('situationCode', axis=1, inplace=True)
    return clean_df



def data_clean(raw_data: NHLData) -> tuple:
    
    regular_season = {} 
    for year in raw_data.regular_season.keys():
        yearly_data = raw_data.regular_season[year]

        regular_season[year] = [df_convert(game) for game in yearly_data]

    del raw_data.regular_season 

    
    playoff = {} 

    for year in raw_data.playoffs.keys():
        yearly_data = raw_data.playoffs[year]

        playoff[year] = [df_convert(game) for game in yearly_data]

    del raw_data.playoffs 

    return regular_season, playoff
