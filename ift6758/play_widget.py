import requests
import json
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import ipywidgets as widgets
from IPython.display import display, clear_output
import ast

class PlayWidget:
    def __init__(self, data):
        self.data = data

        # Widgets
        self.season_slider = widgets.IntSlider(
            min=2016, max=2023, description='Season'
        )
        
        self.game_type_toggle = widgets.ToggleButtons(
            options=['Regular Season', 'Playoffs'], description='Game Type:'
        )
        
        self.id_slider = widgets.Dropdown(
            options=self.get_valid_game_ids(self.season_slider.value, self.game_type_toggle.value),
            description='Game ID',
        )
        
        self.event_id_slider = widgets.Dropdown(
            options=self.get_valid_event_ids(self.season_slider.value, self.game_type_toggle.value, self.id_slider.value),
            description='Event ID',
        )

        # Interactive widget display
        self.interactive_display = widgets.interactive(
            self.update_display, 
            season=self.season_slider,
            game_type=self.game_type_toggle,
            id=self.id_slider,
            event_id=self.event_id_slider
        )
    
    def display(self):
        """Display the interactive widgets."""
        display(self.interactive_display)
    
    def get_game_type_code(self, game_type):
        return 2 if game_type == 'Regular Season' else 3
    
    def get_season_code(self, season):
        return int(f'{season}{season + 1}')
    
    def get_player_name(self, player_id):
        url = f'https://api-web.nhle.com/v1/player/{player_id}/landing'
        response = requests.get(url).json()
        player_name = f"{response['firstName']['default']} {response['lastName']['default']}"
        
        return player_name
    
    def get_valid_game_ids(self, season, game_type):
        """Get valid game IDs for a specific season and game type."""
        game_type_code = self.get_game_type_code(game_type)
        season_code = self.get_season_code(season)
        filtered_data = self.data[(self.data['season'] == season_code) & (self.data['gameType'] == game_type_code)]
        
        return filtered_data['id']
    
    def get_valid_event_ids(self, season, game_type, game_id):
        """Get valid event IDs for a specific game."""
        game_type_code = self.get_game_type_code(game_type)
        season_code = self.get_season_code(season)
        filtered_data = self.data[(self.data['season'] == season_code) & (self.data['gameType'] == game_type_code) & (self.data['id'] == game_id)]
        plays_str = filtered_data["plays"].iloc[0].replace("'", '"')
        plays = json.loads(plays_str)
        
        return [play['eventId'] for play in plays]
    
    def get_valid_plays(self, game_id, season, game_type):
        """Get valid plays for a specific game."""
        game_type_code = self.get_game_type_code(game_type)
        season_code = self.get_season_code(season)
        filtered_data = self.data[(self.data['id'] == game_id) & (self.data['season'] == season_code) & (self.data['gameType'] == game_type_code)]
        plays_str = filtered_data["plays"].iloc[0].replace("'", '"')
        plays = json.loads(plays_str)
        
        return plays
    
    def draw_event(self, play):
        """Visualize a play on a hockey rink."""
        plt.figure(figsize=(10, 6))
        rink_image = mpimg.imread("../figures/nhl_rink.png")
        plt.imshow(rink_image, extent=[-100, 100, -42.5, 42.5])
        rink_center_x = rink_image.shape[1] / 2
        rink_center_y = rink_image.shape[0] / 2

        # Draw coordinate if applicable
        if 'details' in play and 'xCoord' in play['details']:
            x = play['details']['xCoord']
            y = play['details']['yCoord']
            plt.scatter(x, y, color='green', s=100)

        # Generate title
        play_type = play['typeDescKey']
        match play_type:
            case "period-start":
                plt.title("Period start", fontsize=12)
                
            case "game-end":
                plt.title("Game end", fontsize=12)
                
            case "shot-on-goal":
                shooting_player_id = play['details']['shootingPlayerId']
                shooting_player = self.get_player_name(shooting_player_id)
    
                goaler_id = play['details']['goalieInNetId']
                goaler = self.get_player_name(goaler_id)
                plt.title(f'{shooting_player} shot on goal on {goaler}', fontsize=12)
    
            case "goal":
                scoring_player_id = play['details']['scoringPlayerId']
                scoring_player = self.get_player_name(scoring_player_id)
    
                goaler_id = play['details']['goalieInNetId']
                goaler = self.get_player_name(goaler_id)
                plt.title(f'{scoring_player} goal agaisnt goaler {goaler}', fontsize=12)
                
            case "blocked-shot":
                shooting_player_id = play['details']['shootingPlayerId']
                shooting_player = self.get_player_name(shooting_player_id)
    
                blocking_player_id = play['details']['blockingPlayerId']
                blocking_player = self.get_player_name(blocking_player_id)
                plt.title(f'{blocking_player} blocked shot from {shooting_player}', fontsize=12)
    
            case "missed-shot":
                shooting_player_id = play['details']['shootingPlayerId']
                shooting_player = self.get_player_name(shooting_player_id)
    
                goaler_id = play['details']['goalieInNetId']
                goaler = self.get_player_name(goaler_id)
                plt.title(f'{shooting_player} missed shot on {goaler}', fontsize=12)
                
            case "hit":
                hitting_player_id = play['details']['hittingPlayerId']
                hitting_player = self.get_player_name(hitting_player_id)
    
                hittee_layer_id = play['details']['hitteePlayerId']
                hittee_layer = self.get_player_name(hittee_layer_id)
                plt.title(f'{hitting_player} hit {hittee_layer}', fontsize=12)
    
            case "faceoff":
                winning_player_id = play['details']['winningPlayerId']
                winning_player = self.get_player_name(winning_player_id)
    
                losing_player_id = play['details']['losingPlayerId']
                losing_player = self.get_player_name(losing_player_id)
                plt.title(f'{winning_player} won faceoff against {losing_player}', fontsize=12)
    
            case "stoppage":
                reason = play['details']['reason']
                plt.title(f'Stoppage (reason: {reason})', fontsize=12)
    
            case "takeaway":
                player_id = play['details']['playerId']
                player = self.get_player_name(player_id)
    
                plt.title(f'{player} takeaway', fontsize=12)
    
            case "giveaway":
                player_id = play['details']['playerId']
                player = self.get_player_name(player_id)
    
                plt.title(f'{player} giveaway', fontsize=12)
    
            case "penalty":
                if play['details']['committedByPlayerId']:
                    player_id = play['details']['committedByPlayerId']
                else:
                    player_id = play['details']['servedByPlayerId']
                player = self.get_player_name(player_id)
    
                reason = play['details']['descKey']
    
                plt.title(f'{player} penalty (reason: {reason}')
        
        plt.xlim(-100, 100)
        plt.ylim(-42.5, 42.5)
        
        plt.xlabel('feet')
        plt.ylabel('feet')
        plt.grid(True, linestyle='--')
        plt.show()

    def print_game_infos(self, season, game_type, id):
        game_type_code = self.get_game_type_code(game_type)
        season_code = self.get_season_code(season)
        filtered_data = self.data[(self.data['season'] == season_code) & (self.data['gameType'] == game_type_code) & (self.data['id'] == id)]
        home_team_info = ast.literal_eval(filtered_data['homeTeam'].iloc[0])
        away_team_info = ast.literal_eval(filtered_data['awayTeam'].iloc[0])
    
        home_team_name = home_team_info['abbrev']
        away_team_name = away_team_info['abbrev']
    
        home_score = home_team_info['score']
        away_score = away_team_info['score']

        home_sog = home_team_info['sog']
        away_sog = away_team_info['sog']

        print(f"Date: {filtered_data["gameDate"].iloc[0]}")
        print(f"Home Team: {home_team_name}, Score: {home_score}, SOG: {home_sog}")
        print(f"Away Team: {away_team_name}, Score: {away_score}, SOG: {away_sog}")

    def update_display(self, season, game_type, id, event_id):
        """Update the displayed data based on widget inputs."""        
        # Update sliders options
        self.id_slider.options = self.get_valid_game_ids(season, game_type)
        self.event_id_slider.options = self.get_valid_event_ids(season, game_type, id)

        # Update valid plays
        plays = self.get_valid_plays(self.id_slider.value, season, game_type)
        selected_play = next(play for play in plays if play['eventId'] == event_id)

        # Display usefull infos
        clear_output()
        self.print_game_infos(season, game_type, id)

        # Draw selected play
        self.draw_event(selected_play)