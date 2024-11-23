import numpy as np
import pandas as pd

from ift6758.visualizations.visualisations_avancees.utils import get_coor


def v_angle(v1: np.array, v2: np.array) -> float:
    
    dot_product = np.dot(v1, v2)

    
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0

    cos_angle = dot_product / (norm_v1 * norm_v2)

    cos_angle = np.clip(cos_angle, -1.0, 1.0)
    angle_radians = np.arccos(cos_angle)
    angle_degrees = np.degrees(angle_radians)
    return angle_degrees


def zoneshoot(clean_df: pd.DataFrame) -> pd.DataFrame:
    coords_list = [] 
    coords_last_event_list = []

    first_home_team_offensive_event = clean_df[(clean_df['zoneShoot'] == 'O') & (clean_df['teamSide'] == 'home')].iloc[0]
    home_team_initial_side = 'right' if first_home_team_offensive_event['xCoord'] < 0 else 'left'

    for _, row in clean_df.iterrows():
        new_coords, new_last_event_coord = get_coor(row, home_team_initial_side)
        coords_list.append(new_coords) 
        coords_last_event_list.append(new_last_event_coord)

    clean_df['adjustedCoord'] = coords_list
    clean_df['adjustedLastEventCoord'] = coords_last_event_list

    dist_euclidian = lambda x1, x2: np.round(np.linalg.norm(np.array(x1) - np.array(x2)), decimals=1)

    clean_df['distance_to_goal'] = clean_df.apply(
        lambda x: dist_euclidian(x['adjustedCoord'], np.array([0, 89])), axis=1)

    clean_df['distance_since_last_event'] = clean_df.apply(
        lambda x: dist_euclidian(x1=(x['xCoord'], x['yCoord']),
                                 x2=(x['previousXCoord'], x['previousYCoord']))
        if not pd.isnull(x['previousXCoord']) else None, axis=1)

    clean_df['is_rebound'] = clean_df.apply(
        lambda x: True if x['previousEventType'] == 'shot-on-goal' else False, axis=1)

    clean_df['speed_since_last_event'] = clean_df.apply(
        lambda x: x['distance_since_last_event'] / x['timeSinceLastEvent']
        if x['timeSinceLastEvent'] != 0 else 0, axis=1)

    clean_df['angle_to_goal'] = clean_df.apply(
        lambda x: v_angle(x['adjustedCoord'] - np.array([0, 89]), np.array([0, -89])), axis=1)

    clean_df['rebound_angle_to_goal'] = clean_df.apply(
        lambda x: v_angle(x['adjustedLastEventCoord'] - np.array([0, 89]), np.array([0, -89]))
        if x['is_rebound'] else 0, axis=1)

    clean_df.drop(columns=['adjustedCoord', 'adjustedLastEventCoord'], inplace=True)

    clean_df['offensive_time_elapsed'] = clean_df.groupby('eventOwnerTeam')['gameSeconds'].diff().fillna(0)

    return clean_df
