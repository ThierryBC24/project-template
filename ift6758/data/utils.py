import pandas as pd


def empty_goal_func(df: pd.DataFrame) -> pd.Series:
    return df.apply(lambda x: x['situationCode'][3] if x['teamSide'] == 'away' else x['situationCode'][0] if len(x['situationCode']) == 4 else 0
                    , axis=1).map(
        {'0': True, '1': False})


def goal_situation(df: pd.DataFrame) -> pd.Series:
    return df.apply(lambda x: "Advantage" if (int(x['situationCode'][1]) > int(x['situationCode'][2]) and x[
        'teamSide'] == 'away') or (int(x['situationCode'][2]) > int(x['situationCode'][1]) and x[
        'teamSide'] == 'home')
    else "Disadvantage" if (int(x['situationCode'][1]) < int(x['situationCode'][2]) and x['teamSide'] == 'away') or
                           (int(x['situationCode'][2]) < int(x['situationCode'][1]) and x['teamSide'] == 'home')
    else 'Neutral', axis=1)


def time_convert(df: pd.DataFrame, column: str) -> pd.Series:

    df['minutes'] = df[column].str.split(':').str[0].astype(int)
    df['seconds'] = df[column].str.split(':').str[1].astype(int)
    df['numberPeriod'] = df['numberPeriod'].astype(int)

    df[column] = df['minutes'] * 60 + df['seconds'] + 20 * 60 * (df['numberPeriod'] - 1)

    df.drop(['minutes', 'seconds'], axis=1, inplace=True)

    return df[column]
