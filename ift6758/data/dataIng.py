import pandas as pd


def ing_period(df: pd.DataFrame) -> pd.DataFrame:
    
    df_period = pd.DataFrame(df['periodDescriptor'].tolist())

    df_period[['number', 'maxRegulationPeriods']] = df_period[['number', 'maxRegulationPeriods']].astype(str)

    df_period['numberPeriod'] = df_period['number']

    return df_period


def ing_event(df: pd.DataFrame, df_players: pd.DataFrame) -> pd.DataFrame:
    df_details = pd.DataFrame(df['details'].tolist())

    df_details['shootingPlayerId'] = df_details['shootingPlayerId'].fillna(0) + df_details['scoringPlayerId'].fillna(0)

    df_details['goalieInNetId'] = df_details['goalieInNetId'].fillna(0)

    df_details['shootingPlayerId'] = df_details['shootingPlayerId'].astype(int)
    df_details['goalieInNetId'] = df_details['goalieInNetId'].astype('Int64')  

    df_details = pd.merge(df_players, df_details, left_on='playerId', right_on='shootingPlayerId', how='right').drop(
        columns=['playerId'])
    df_details['shootingPlayer'] = df_details['firstName'] + ' ' + df_details['lastName']
    df_details.drop(['firstName', 'lastName'], axis=1, inplace=True)

    df_details = pd.merge(df_players, df_details, left_on='playerId', right_on='goalieInNetId', how='right').drop(
        columns=['playerId'])

    df_details['goaliePlayer'] = df_details['firstName'] + ' ' + df_details['lastName']
    df_details.drop(['firstName', 'lastName'], axis=1, inplace=True)

    return df_details

def ing_event_bef(df: pd.DataFrame):
    df_copy = df.copy().shift(1)
    df['previousEventType'] = df_copy['typeDescKey']

    df['timeSinceLastEvent'] = df['gameSeconds'].diff()
    df['timeSinceLastEvent'] = df.apply(lambda x: 0
    if pd.isnull(x['timeSinceLastEvent']) else abs(x['timeSinceLastEvent']), axis=1)

    details = df_copy['details'].apply(pd.Series)
    df["previousXCoord"] = details['xCoord']
    df["previousYCoord"] = details['yCoord']

    return df

def ing_event_bef(df: pd.DataFrame):
    df_copy = df.copy().shift(1)
    df['last_event_type'] = df_copy['typeDescKey']

    df['time_since_last_event'] = df['gameSeconds'].diff()
    df['time_since_last_event'] = df.apply(lambda x: 0
                                           if pd.isnull(x['time_since_last_event']) else abs(x['time_since_last_event']),
                                           axis=1)

    details = df_copy['details'].apply(pd.Series)
    df["last_x_coord"] = details['xCoord']
    df["last_y_coord"] = details['yCoord']

    return df


