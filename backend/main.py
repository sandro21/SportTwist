import nflreadpy as nfl
import pandas as pd

# Load current season play-by-play data
pbp = nfl.load_pbp()
df = pbp.to_pandas()
# df.to_csv('pbp_2018.csv', index=False)
# will be id
current_game = df[df['game_id'] == "2025_01_BAL_BUF"]
current_game = current_game.query("play_type_nfl == 'PASS' or play_type_nfl == 'RUSH' or play_type_nfl == 'FIELD_GOAL' or play_type_nfl == 'EXTRA_POINT' or play_type_nfl == 'PUNT' or play_type_nfl == 'PENALTY'")
current_game.to_csv('current_game.csv', index=False)