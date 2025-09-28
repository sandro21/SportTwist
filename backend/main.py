import nflreadpy as nfl
import pandas as pd
from game import Game, Simulator


# df = nfl.load_teams()
# # Convert Polars → pandas → list of dicts
# df = df.to_pandas()
# df = df[df['season'] == 2025]
# # .to_dict(orient="records")
# df.to_csv('teams.csv', index=False)
game = Game("2025_01_ARI_NO", 2025)
plays = game.plays
sim = Simulator(game)
plays = sim.simulate_from(50, plays[50])