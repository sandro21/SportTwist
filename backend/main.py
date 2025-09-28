import nflreadpy as nfl
import pandas as pd
from game import Game, Simulator


# df = nfl.load_teams()
# # Convert Polars → pandas → list of dicts
# df = df.to_pandas()
# df = df[df['season'] == 2025]
# # .to_dict(orient="records")
# df.to_csv('teams.csv', index=False)
# game = Game("2025_03_MIA_BUF", 2025)
# plays = game.plays
# sim = Simulator(game)
# plays = sim.simulate_from({"is_one_point": False, "made": True}, 11, plays[11])
# for play in plays:
#     print(play)
