from play_by_play_data import PlayByPlayData

play_by_play_data = PlayByPlayData(base_path=".")

# Download data for the seasons 2016 to 2023
for season in range(2016, 2024):
    play_by_play_data.get_data(season)

# Combine the data for all downloaded seasons
combined_data = play_by_play_data.get_all_data()
print(combined_data.head())