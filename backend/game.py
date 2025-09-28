import nflreadpy as nfl
import pandas as pd
import math
import random

def get_team_season_stats(team: str, year: int) -> dict:
    pbp = nfl.load_pbp([year]).to_pandas()
    df = pbp[(pbp.posteam == team) | (pbp.defteam == team)].copy()
    off = df[df.posteam == team]

    def n(x): return int(x) if pd.notna(x) else 0
    def f(x): return float(x) if pd.notna(x) else 0.0

    pass_attempts = n(off.pass_attempt.sum())
    pass_completions = n(off.complete_pass.sum())
    interceptions = n(off.interception.sum())
    fumbles = n(df.fumble.sum())
    third_down_attempts = n(off[off.down == 3].shape[0])
    third_down_conversions = n(off.third_down_converted.sum())
    fourth_down_attempts = n(off[off.down == 4].shape[0])
    fourth_down_conversions = n(off.fourth_down_converted.sum())
    punts = n(off.punt_attempt.sum())
    extra_point_attempts = n(off.extra_point_attempt.sum())
    extra_points_made = n((off.extra_point_result == "good").sum())
    two_point_attempts = n(off.two_point_attempt.sum())
    two_point_conversions_successful = n((off.two_point_conv_result == "success").sum())
    field_goals_attempted = n(off.field_goal_attempt.sum())
    field_goals_made = n((off.field_goal_result == "made").sum())
    penalties = n(df.penalty.sum())
    timeouts = n(df[(df.timeout == 1) & (df.timeout_team == team)].shape[0])
    rush_attempts = n(off.rush_attempt.sum())
    rush_yards = f(off[off.rush_attempt == 1].rushing_yards.fillna(0).sum())
    avg_yards_per_carry = f(rush_yards / rush_attempts) if rush_attempts else 0.0
    pass_yards = f(off[off.pass_attempt == 1].passing_yards.fillna(0).sum())
    avg_yards_per_pass = f(pass_yards / pass_attempts) if pass_attempts else 0.0
    yards_per_play = f((rush_yards + pass_yards) / len(off)) if len(off) else 0.0
    # Use a more reliable scoring calculation based on actual scoring plays rather than drives
    # This avoids issues with unreliable drive numbering in NFL data
    total_touchdowns = n(off.td_team.notna().sum())
    total_made_fgs = n((off.field_goal_result == "made").sum())
    total_plays = len(off)
    
    # Estimate scoring rate as percentage of plays that result in scores
    # Multiply by a factor to convert from play-level to drive-level probability
    # Average NFL drive is about 6-8 plays, so multiply by 7
    if total_plays > 0:
        scoring_play_rate = (total_touchdowns + total_made_fgs) / total_plays
        score_prob = min(0.65, scoring_play_rate * 7)  # Cap at realistic 65%
    else:
        score_prob = 0.35
    red_zone_attempts = n(off[off.yardline_100 <= 20].shape[0])
    red_zone_tds = n(off[(off.yardline_100 <= 20) & (off.td_team.notna())].shape[0])
    red_zone_td_prob = f(red_zone_tds / red_zone_attempts) if red_zone_attempts else 0.0
    # Calculate turnover probability as rate per play (more reliable than drive-based)
    total_turnovers = n((off.interception == 1).sum()) + n((off.fumble_lost == 1).sum())
    turnover_prob = f(total_turnovers / total_plays) if total_plays > 0 else 0.0

    return {
        "team": team,
        "season": year,
        "pass_attempts": pass_attempts,
        "pass_completions": pass_completions,
        "completion_prob": f(pass_completions / pass_attempts) if pass_attempts else 0.0,
        "interceptions": interceptions,
        "interception_prob": f(interceptions / pass_attempts) if pass_attempts else 0.0,
        "fumbles": fumbles,
        "fumble_prob": f(fumbles / len(df)) if len(df) else 0.0,
        "third_down_attempts": third_down_attempts,
        "third_down_conversions": third_down_conversions,
        "third_down_conversion_prob": f(third_down_conversions / third_down_attempts) if third_down_attempts else 0.0,
        "fourth_down_attempts": fourth_down_attempts,
        "fourth_down_conversions": fourth_down_conversions,
        "fourth_down_conversion_prob": f(fourth_down_conversions / fourth_down_attempts) if fourth_down_attempts else 0.0,
        "punts": punts,
        "extra_point_attempts": extra_point_attempts,
        "extra_points_made": extra_points_made,
        "extra_point_prob": f(extra_points_made / extra_point_attempts) if extra_point_attempts else 0.0,
        "two_point_conversions_attempted": two_point_attempts,
        "two_point_conversions_successful": two_point_conversions_successful,
        "two_point_conversion_prob": f(two_point_conversions_successful / two_point_attempts) if two_point_attempts else 0.0,
        "field_goals_attempted": field_goals_attempted,
        "field_goals_made": field_goals_made,
        "field_goal_prob": f(field_goals_made / field_goals_attempted) if field_goals_attempted else 0.0,
        "penalties": penalties,
        "timeouts": timeouts,
        "rush_attempts": rush_attempts,
        "rush_yards": rush_yards,
        "avg_yards_per_carry": avg_yards_per_carry,
        "pass_yards": pass_yards,
        "avg_yards_per_pass": avg_yards_per_pass,
        "yards_per_play": yards_per_play,
        "scoring_drive_prob": score_prob,
        "red_zone_attempts": red_zone_attempts,
        "red_zone_td_prob": red_zone_td_prob,
        "turnover_prob": turnover_prob
    }
            

class PlayEvent:
    def __init__(self, desc, qtr, half_seconds_remaining, game_seconds_remaining, down, to_go, yardline_100, yards_gained, score_differential, posteam, points=None):
        self.half_seconds_remaining = half_seconds_remaining
        self.desc = desc
        self.qtr = qtr
        self.game_seconds_remaining = game_seconds_remaining
        self.down = down
        self.to_go = to_go
        self.yardline_100 = yardline_100
        self.yards_gained = yards_gained
        self.score_differential = score_differential
        self.posteam = posteam
        self.points = points

class PassEvent(PlayEvent):
    def __init__(self, desc, qtr, half_seconds_remaining, game_seconds_remaining, down, to_go, yardline_100, yards_gained, score_differential, posteam, points=None, is_complete=False, is_fumble=False):
        super().__init__(desc, qtr, half_seconds_remaining, game_seconds_remaining, down, to_go, yardline_100, yards_gained, score_differential, posteam, points)
        self.is_complete = is_complete
        self.is_fumble = is_fumble
        self.is_touchdown = False

class InterceptionEvent(PlayEvent):
    def __init__(self, desc, qtr, half_seconds_remaining, game_seconds_remaining, down, to_go, yardline_100, yards_gained, score_differential, posteam, points=None, is_interception=True, is_fumble=False):
        super().__init__(desc, qtr, half_seconds_remaining, game_seconds_remaining, down, to_go, yardline_100, yards_gained, score_differential, posteam, points)
        self.is_interception = is_interception
        self.is_fumble = is_fumble

class RushEvent(PlayEvent):
    def __init__(self, desc, qtr, half_seconds_remaining, game_seconds_remaining, down, to_go, yardline_100, yards_gained, score_differential, posteam, points=None, is_fumble=False):
        super().__init__(desc, qtr, half_seconds_remaining, game_seconds_remaining, down, to_go, yardline_100, yards_gained, score_differential, posteam, points)
        self.is_fumble = is_fumble
        self.is_touchdown = False

class FieldGoalEvent(PlayEvent):
    def __init__(self, desc, qtr, half_seconds_remaining, game_seconds_remaining, down, to_go, yardline_100, yards_gained, score_differential, posteam, points=None, is_good=False):
        super().__init__(desc, qtr, half_seconds_remaining, game_seconds_remaining, down, to_go, yardline_100, yards_gained, score_differential, posteam, points)
        self.is_good = is_good

class XPEvent(PlayEvent):
    def __init__(self, desc, qtr, half_seconds_remaining, game_seconds_remaining, down, to_go, yardline_100, yards_gained, score_differential, posteam, points=None, is_good=False):
        super().__init__(desc, qtr, half_seconds_remaining, game_seconds_remaining, down, to_go, yardline_100, yards_gained, score_differential, posteam, points)
        self.is_good = is_good

class PenaltyEvent(PlayEvent):
    def __init__(self, desc, qtr, half_seconds_remaining, game_seconds_remaining, down, to_go, yardline_100, yards_gained, score_differential, posteam, points=None, penalty_type=None, penalty_yards=0):
        super().__init__(desc, qtr, half_seconds_remaining, game_seconds_remaining, down, to_go, yardline_100, yards_gained, score_differential, posteam, points)
        self.penalty_type = penalty_type
        self.penalty_yards = penalty_yards

class Game:
    def __init__(self, game_id, year):
        self.game_id = game_id
        self.plays = []
        pbp = nfl.load_pbp([year]).to_pandas()
        current_game = pbp[pbp['game_id'] == self.game_id]
        last_row = current_game[current_game['game_seconds_remaining'] == 0]
        self.home = last_row['home_team'].values[0]
        self.away = last_row['away_team'].values[0]
        self.home_score = last_row['home_score'].values[0]
        self.away_score = last_row['away_score'].values[0]
        self.stats = {self.home: get_team_season_stats(self.home, year), self.away: get_team_season_stats(self.away, year)}
        print(f"Loaded game {self.game_id}: {self.away} vs {self.home}, final score {self.away_score}-{self.home_score}")
        relevant_types = [
            'PASS', 'RUSH', 'INTERCEPTION', 'FIELD_GOAL', 'XP_KICK', 'PUNT', 'PENALTY', 'PAT2'
        ]
        # Include touchdown plays regardless of type OR any play with points
        current_game = current_game.query("play_type_nfl in @relevant_types or touchdown == 1 or field_goal_result == 'made' or extra_point_result == 'good' or two_point_conv_result == 'success'")
        for row in current_game.itertuples():
            # Calculate points for this play
            points_scored = 0
            if hasattr(row, 'touchdown') and row.touchdown == 1:
                points_scored = 6
            elif hasattr(row, 'field_goal_result') and row.field_goal_result == "made":
                points_scored = 3
            elif hasattr(row, 'extra_point_result') and row.extra_point_result == "good":
                points_scored = 1
            elif hasattr(row, 'two_point_conv_result') and row.two_point_conv_result == "success":
                points_scored = 2
                
            base_args = (
                row.desc, row.qtr, row.half_seconds_remaining, row.game_seconds_remaining, row.down,
                row.ydstogo, row.yardline_100, row.yards_gained, row.score_differential, row.posteam, points_scored
            )
            if row.play_type_nfl == "PASS" or (hasattr(row, 'pass_touchdown') and row.pass_touchdown == 1):
                is_td = hasattr(row, 'touchdown') and row.touchdown == 1
                play = PassEvent(*base_args, is_complete=row.complete_pass or is_td, is_fumble=row.fumble)
                if is_td:
                    play.is_touchdown = True
            elif row.play_type_nfl == "INTERCEPTION":
                play = InterceptionEvent(*base_args, is_interception=True)
            elif row.play_type_nfl == "RUSH" or (hasattr(row, 'rush_touchdown') and row.rush_touchdown == 1):
                is_td = hasattr(row, 'touchdown') and row.touchdown == 1
                play = RushEvent(*base_args, is_fumble=row.fumble)
                if is_td:
                    play.is_touchdown = True
            elif row.play_type_nfl == "FIELD_GOAL":
                play = FieldGoalEvent(*base_args, is_good=(row.field_goal_result == "made"))
            elif row.play_type_nfl == "XP_KICK":
                play = XPEvent(*base_args, is_good=(row.extra_point_result == "good"))
            elif row.play_type_nfl == "PENALTY":
                play = PenaltyEvent(*base_args, penalty_type=row.penalty_type, penalty_yards=row.penalty_yards)
            else:
                continue
            self.plays.append(play)

class GameState:
    def __init__(self, play_event):
        self.qtr = play_event.qtr
        self.half_seconds_remaining = play_event.half_seconds_remaining
        self.game_seconds_remaining = play_event.game_seconds_remaining
        self.down = play_event.down
        self.to_go = play_event.to_go
        self.yardline_100 = play_event.yardline_100
        self.posteam = play_event.posteam
        self.score_differential = play_event.score_differential
        self.playing = self.game_seconds_remaining > 0 