import pandas as pd

from ift6758.visualizations.visualisations_avancees.allshoots import team_shots_coords


def get_coor(row: pd.Series, home_team_initial_side: str) -> list:
    initial_side = None

    if(row['teamSide'] == 'home'):
        initial_side = home_team_initial_side
    else:
        if home_team_initial_side == 'left':
            initial_side = 'right'
        else:
            initial_side = 'left'


    new_coords = [(0, 0), (0,0)]
    current_side = initial_side
    if str(row['idGame'])[4:6] == '02' and row['numberPeriod'] <= 3:
        if row['numberPeriod'] % 2 == 0:
            # on change le camp
            if initial_side == 'left':
                current_side = 'right'
            else:
                current_side = 'left'
    else:
        if row['numberPeriod'] % 2 == 0:
            if initial_side == 'left':
                current_side = 'right'
            else:
                current_side = 'left'

    if current_side == 'left':
        new_coords = [(-row['yCoord'], row['xCoord']), (-row['previousYCoord'], row['previousXCoord'])]
    else:
        new_coords = [(row['yCoord'], -row['xCoord']), (row['previousYCoord'], -row['previousXCoord'])]

    return new_coords


def get_shoot_by_team(regular_season: dict = None, playoff:dict = None, year: int = 2020) -> dict:

    
    if year in team_shots_coords:
        return team_shots_coords[year] 

    year_shots_coords = {}
    dfs_combined = regular_season[year]
    if playoff is not None:
        dfs_combined += playoff[year]

    df_teams = pd.concat([df['eventOwnerTeam'] for df in dfs_combined])
    unique_teams = df_teams.unique()

    for team in unique_teams:

        team_df = pd.concat([df[df['eventOwnerTeam'] == team] for df in dfs_combined])
        coords_list = []
        first_offensive_zone_event = team_df[team_df['zoneShoot'] == 'O'].iloc[0]
        side = 'right' if first_offensive_zone_event['iceCoord'][0] < 0 else 'left'

        for _, row in team_df.iterrows():
            ice_coord = row['iceCoord']
            if ice_coord is not None and all(pd.notnull(coord) for coord in ice_coord):
                coords_list.append(get_coor(row, side))

        x_coords = [coord[0] for coord in coords_list]
        y_coords = [coord[1] for coord in coords_list]

        year_shots_coords[team] = (x_coords, y_coords)

    team_shots_coords[year] = year_shots_coords

    return year_shots_coords



