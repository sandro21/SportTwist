import nflreadpy as nfl
import pandas as pd
from game import Game, Simulator


# df = nfl.load_teams()
# # Convert Polars → pandas → list of dicts
# df = df.to_pandas()
# df = df[df['season'] == 2025]
# # .to_dict(orient="records")
# df.to_csv('teams.csv', index=False)
game = Game("2025_01_KC_LAC", 2025)
plays = game.plays
# for i, play in enumerate(plays):
#     print(str(i) + ":" + str(play))
sim = Simulator(game)
avgs = sim.monte_carlo({"is_complete": False, "is_interception": True}, 104, plays[104])
print(avgs)
