import nflreadpy as nfl

def get_team_season_stats(team: str, year: int) -> dict:
    import pandas as pd
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
    drives = n(off.drive.nunique())
    scores = n(off[off.td_team.notna() | (off.field_goal_attempt == 1)].drive.nunique())
    score_prob = f(scores / drives) if drives else 0.0
    red_zone_attempts = n(off[off.yardline_100 <= 20].shape[0])
    red_zone_tds = n(off[(off.yardline_100 <= 20) & (off.td_team.notna())].shape[0])
    red_zone_td_prob = f(red_zone_tds / red_zone_attempts) if red_zone_attempts else 0.0
    turnover_drives = n(off[(off.interception == 1) | (off.fumble_lost == 1)].drive.nunique())
    turnover_prob = f(turnover_drives / drives) if drives else 0.0

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

year = int(input("Season year: ").strip())
team = input("Team abbreviation: ").strip().upper()

stats_dict = get_team_season_stats(team, year)
with open(f"{team}_{year}_season_stats.py", "w", encoding="utf-8") as f:
    f.write("team_stats = ")
    f.write(repr(stats_dict))
