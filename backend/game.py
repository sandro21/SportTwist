import nflreadpy as nfl
import pandas as pd
import math
import random

def format_field_position(yardline_100, posteam, home_team, away_team):
        if yardline_100 > 50:
            yard_line = 50 - (yardline_100 - 50)
            return f"{posteam} {yard_line}"
        elif yardline_100 == 50:
            return "50"
        else:
            opponent = away_team if posteam == home_team else home_team
            yard_line = yardline_100
            return f"{opponent} {yard_line}"
        
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
            

class PlayEvent:
    def __init__(self, desc, home_score, away_score, qtr, quarter_seconds_remaining, half_seconds_remaining, game_seconds_remaining, down, to_go, yrdln, yardline_100, yards_gained, score_differential, posteam):
        self.desc = desc
        self.home_score = home_score
        self.away_score = away_score
        self.qtr = qtr
        self.quarter_seconds_remaining = quarter_seconds_remaining
        self.half_seconds_remaining = half_seconds_remaining
        self.game_seconds_remaining = game_seconds_remaining
        self.down = down
        self.to_go = to_go
        self.yrdln = yrdln
        self.yardline_100 = yardline_100
        self.yards_gained = yards_gained
        self.score_differential = score_differential
        self.posteam = posteam

    def get_changeable_attributes(self):
        pass

    def __str__(self):
        minutes = int(self.quarter_seconds_remaining // 60)
        seconds = int(self.quarter_seconds_remaining % 60)
        time_str = f"{minutes}:{seconds:02d}"
        
        quarter_suffixes = {1: "1st", 2: "2nd", 3: "3rd", 4: "4th"}
        quarter_str = quarter_suffixes.get(int(self.qtr), f"{int(self.qtr)}th")
        
        return (f"{self.posteam} ball | {self.home_score}-{self.away_score} | "
                f"{quarter_str} {time_str} | {self.down} & {self.to_go} at {self.yrdln} | "
                f"{self.desc}")
    
class PassEvent(PlayEvent):
    def __init__(self, *args, is_complete,):
        super().__init__(*args)
        self.is_complete = is_complete
    def get_changeable_attributes(self):
        return {'is_complete': self.is_complete, 'is_interception': False}
    def reroll(self, new_attrs, simulator):
        state = GameState(self)
        num = random.random()
        if new_attrs['is_interception']:
            return simulator.simulate_interception(state, num)
        elif new_attrs['is_complete']:
            return simulator.simulate_completion(state, num)
        else:
            return simulator.simulate_incompletion(state, num)
    def __str__(self):
        return super().__str__() + "; " + f"Pass: {'Complete' if self.is_complete else 'Incomplete'}"

class InterceptionEvent(PlayEvent):
    def __init__(self, *args):
        super().__init__(*args)
    def get_changeable_attributes(self):
        return {'is_complete': False, 'is_interception': True}
    def reroll(self, new_attrs, simulator):
        state = GameState(self)
        num = random.random()
        if new_attrs['is_interception']:
            return simulator.simulate_interception(state, num)
        elif new_attrs['is_complete']:
            return simulator.simulate_completion(state, num)
        else:
            return simulator.simulate_incompletion(state, num)
    def __str__(self):   
        return super().__str__() + "; " + f"Interception! Now in possession of the other team."

class RushEvent(PlayEvent):
    def __init__(self, *args, ):
        super().__init__(*args)
    def __str__(self):   
        return super().__str__() + " " + f"Rush"
    
class PuntEvent(PlayEvent):
    def __init__(self, *args, ):
        super().__init__(*args)
    def get_changeable_attributes(self):
        return {'punt_it': False}
    def reroll(self, new_attrs, simulator):
        state = GameState(self)
        num = random.random()
        if new_attrs['punt_it']:
            return simulator.simulate_punt(state, num)
        else:
            if num < .7:
                return simulator.simulate_rush(state, num)
            else:
                if num < self.game.stats[state.posteam]['completion_prob']:
                    return self.simulate_completion(state, num)
                elif num < self.game.stats[state.posteam]['completion_prob'] + self.game.stats[state.posteam]['interception_prob']:
                    return self.simulate_interception(state, num)
                else:
                    return self.simulate_incompletion(state, num)
    def __str__(self):   
        return super().__str__() + " " + f"Punt"

class FieldGoalEvent(PlayEvent):
    def __init__(self, *args, is_good):
        super().__init__(*args)
        self.is_good = is_good
    def get_changeable_attributes(self):
        return {'made': self.is_good}
    def reroll(self, new_attrs, simulator):
            state = GameState(self)
            num = random.random()
            return simulator.simulate_field_goal(state, num, made=True)
    def __str__(self):   
        return super().__str__() + " " + f"Field Goal: {'Good' if self.is_good else 'No Good'}."

class XPEvent(PlayEvent):
    def __init__(self, *args, is_good):
        super().__init__(*args)
        self.is_good = is_good
    def get_changeable_attributes(self):
        return {'made': self.is_good, 'is_one_point': True,}
    def reroll(self, new_attrs, simulator):
        state = GameState(self)
        num = random.random()
        if new_attrs['is_one_point']:
            return simulator.simulate_xpat(state, num, made=new_attrs['made'])
        else:
            return simulator.simulate_2pat(state, num, made=new_attrs['made'])
    def __str__(self):   
        return super().__str__() + " " + f"Extra Point: {'Good' if self.is_good else 'No Good'}."
    
class PAT2Event(PlayEvent):
    def __init__(self, *args, is_good):
        super().__init__(*args)
        self.is_good = is_good
    def get_changeable_attributes(self):
        return {'made': self.is_good, 'is_one_point': False}
    def reroll(self, new_attrs, simulator):
        state = GameState(self)
        num = random.random()
        if new_attrs['is_one_point']:
            return simulator.simulate_xpat(state, num, made=new_attrs['made'])
        else:
            return simulator.simulate_2pat(state, num, made=new_attrs['made'])
    def __str__(self):   
        return super().__str__() + " " + f"2 Point Attempt: {'Good' if self.is_good else 'No Good'}."

class PenaltyEvent(PlayEvent):
    def __init__(self, *args, penalty_type, penalty_yards):
        super().__init__(*args)
        self.penalty_type = penalty_type
        self.penalty_yards = penalty_yards
    def get_changeable_attributes(self):
        return {'called': True}
    def reroll(self, new_attrs, simulator):
        if not new_attrs['called']:
            return simulator.simulate_next_play(GameState(self))
        else:
            return self
    def __str__(self):
        return super().__str__() + " " + f"Penalty: {self.penalty_type} for {self.penalty_yards} yards."

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
        current_game = current_game.query("play_type_nfl in @relevant_types")
        for row in current_game.itertuples():
            base_args = (
                row.desc, row.total_home_score, row.total_away_score, row.qtr, row.quarter_seconds_remaining, row.half_seconds_remaining, row.game_seconds_remaining, row.down,
                row.ydstogo, row.yrdln, row.yardline_100, row.yards_gained, row.score_differential, row.posteam,
            )
            if row.play_type_nfl == "PASS":
                play = PassEvent(*base_args,
                                 is_complete=row.complete_pass,)
            elif row.play_type_nfl == "INTERCEPTION":
                play = InterceptionEvent(*base_args)
            elif row.play_type_nfl == "RUSH":
                play = RushEvent(*base_args,)
            elif row.play_type_nfl == "PUNT":
                play = PuntEvent(*base_args,)
            elif row.play_type_nfl == "FIELD_GOAL":
                play = FieldGoalEvent(*base_args,
                                      is_good=(row.field_goal_result == "GOOD"))
            elif row.play_type_nfl == "XP_KICK":
                play = XPEvent(*base_args,
                               is_good=(row.extra_point_result == "GOOD"))
            elif row.play_type_nfl == "PAT2":
                play = PAT2Event(*base_args,
                               is_good=(row.extra_point_result == "GOOD"))
            elif row.play_type_nfl == "PENALTY":
                play = PenaltyEvent(*base_args,
                                    penalty_type=row.penalty_type,
                                    penalty_yards=row.penalty_yards)
            else:
                continue
            self.plays.append(play)
    def __str__(self):
        return f"Game {self.game_id}: {self.away} vs {self.home}, final score {int(self.away_score)}-{int(self.home_score)}"

class GameState:
    def __init__(self, play_event):
        self.qtr = play_event.qtr
        self.home_score = play_event.home_score
        self.away_score = play_event.away_score
        self.quarter_seconds_remaining = play_event.quarter_seconds_remaining
        self.half_seconds_remaining = play_event.half_seconds_remaining
        self.game_seconds_remaining = play_event.game_seconds_remaining
        self.down = play_event.down
        self.to_go = play_event.to_go
        self.yrdln = play_event.yrdln
        self.yardline_100 = play_event.yardline_100
        self.posteam = play_event.posteam
        self.score_differential = play_event.score_differential
        self.playing = self.game_seconds_remaining > 0 
    
class Simulator:
    def __init__(self, game):
        self.game = game

    def decide_play_type(self, state):
        def pass_or_rush():
            pass_prob_yrds = 1 / (1 + math.exp(-.8 * (state.to_go - 6)))
            pass_prob_team = self.game.stats[state.posteam]['pass_attempts'] / (self.game.stats[state.posteam]['pass_attempts'] + self.game.stats[state.posteam]['rush_attempts'])
            weight_yrds = 0.7  
            weight_team = 0.3
            pass_prob = weight_yrds * pass_prob_yrds + weight_team * pass_prob_team
            if random.random() < pass_prob:
                return "PASS"
            else:
                return "RUSH"
        
        if state.half_seconds_remaining <= 30 and state.score_differential <= 0 and state.score_differential >= -3 and state.yardline_100 <= 45:
            return "FIELD_GOAL"

        if state.down < 4:
            return pass_or_rush()
        else:
            if state.yardline_100 <= 5:
                return pass_or_rush()
            elif state.yardline_100 <= 35:
                fg_prob = 0.7
            elif state.yardline_100 <= 50:
                fg_prob = 0.4
            else:
                fg_prob = 0.1
            if random.random() < fg_prob:
                return "FIELD_GOAL"
            else:
                return "PUNT"
            
    def decide_pat_type(self, state):
        minutes_left = state.game_seconds_remaining / 60.0
        time_urgency = 0.5 + 5.5 / (1 + math.exp(0.3 * (minutes_left - 5)))
        score_center = -5
        score_width = 8   
        score_urgency = math.exp(-0.5 * ((state.score_differential - score_center) / score_width) ** 2)
        
        if state.score_differential < 0:
            trailing_bonus = 1 + 0.8 * (1 - math.exp(0.1 * state.score_differential))
        else:
            trailing_bonus = math.exp(-0.2 * state.score_differential)
        
        base_prob = 0.08
        probability = base_prob * time_urgency * score_urgency * trailing_bonus
        
        max_prob = 0.85
        probability = max_prob * math.tanh(probability / max_prob)
        
        return "PAT2" if random.random() < max(0.01, probability)  else "XP_KICK"
    
    def monte_carlo(self, changeable_attrs, start_play_index, change_play):
        simulations = 5000
        total_home_score = 0
        total_away_score = 0
        home_wins = 0
        for _ in range(simulations):
            simulated_plays = self.simulate_from(changeable_attrs, start_play_index, change_play)
            simulated_plays[len(simulated_plays)-1]
            total_home_score += simulated_plays[len(simulated_plays)-1].home_score
            total_away_score += simulated_plays[len(simulated_plays)-1].away_score
            if simulated_plays[len(simulated_plays)-1].home_score > simulated_plays[len(simulated_plays)-1].away_score:
                home_wins += 1
        avg_home_score = total_home_score / simulations
        avg_away_score = total_away_score / simulations
        home_win_rate = home_wins / simulations
        away_win_rate = 1 - home_win_rate
        return {self.game.home: {'score': avg_home_score, 'win_pct': home_win_rate}, self.game.away: {'score': avg_away_score, 'win_pct': away_win_rate}}

    def simulate_from(self, changeable_attrs, start_play_index, change_play):
        state = GameState(change_play)
        change_play = change_play.reroll(changeable_attrs, self)
        state = GameState(change_play)
        last_plays = self.game.plays[:start_play_index] + [change_play]
        while state.playing:
            next_play = self.simulate_next_play(state)
            if type(next_play) == tuple:
                last_plays.append(next_play[0])
                last_plays.append(next_play[1])
                state = GameState(next_play[1])
            else:
                last_plays.append(next_play)
                state = GameState(next_play)
        return last_plays[:len(last_plays)-1]
        
    def simulate_completion(self, state, num):
        yards_gained = max(-5, int(random.gauss(self.game.stats[state.posteam]['avg_yards_per_pass'], 4)))
        is_complete = True
        if state.yardline_100 - yards_gained <= 0:
            state.home_score += 6 if state.posteam == self.game.home else 0
            state.away_score += 6 if state.posteam == self.game.away else 0
            state.score_differential = state.home_score - state.away_score
            pass_event = PassEvent(
                "Simulated pass play: " + ("complete" if is_complete else "incomplete") + ", gain of " + str(yards_gained) + " yards. Touchdown by " + state.posteam + "!",
                state.home_score,
                state.away_score,
                state.qtr,
                state.quarter_seconds_remaining,
                state.half_seconds_remaining,
                state.game_seconds_remaining,
                1,
                10,
                state.posteam + " " + str(max(0, state.yardline_100 - yards_gained)) if max(0, state.yardline_100 - yards_gained) > 50 else self.game.away if state.posteam == self.game.home else self.game.home  + " " + str(max(0, state.yardline_100 - yards_gained)),
                75,
                yards_gained,
                state.score_differential,
                self.game.away if state.posteam == self.game.home else self.game.home,
                is_complete=True
            )
            pat_type = self.decide_pat_type(state)
            if pat_type == "XP_KICK":
                xp_event = self.simulate_xpat(state, num)
                return (pass_event, xp_event)
            else:
                pat2_event = self.simulate_2pat(state, num)
                return (pass_event, pat2_event)
        else:
            return PassEvent(
                    "Simulated pass play: " + ("complete" if is_complete else "incomplete") + ", gain of " + str(yards_gained) + " yards",
                    state.home_score,
                    state.away_score,
                    state.qtr,
                    state.quarter_seconds_remaining,
                    state.half_seconds_remaining,
                    state.game_seconds_remaining,
                    state.down + 1 if state.to_go > yards_gained else 1,
                    state.to_go - yards_gained if state.to_go > yards_gained else 10,
                    format_field_position(max(0, state.yardline_100 - yards_gained), state.posteam, self.game.home, self.game.away),
                    max(0, state.yardline_100 - yards_gained),
                    yards_gained,
                    state.score_differential,
                    state.posteam,
                    is_complete=is_complete,
                )
        
    def simulate_interception(self, state, num):
        return InterceptionEvent(
            "Simulated interception play",
            state.home_score,
            state.away_score,
            state.qtr,
            state.quarter_seconds_remaining,
            state.half_seconds_remaining,
            state.game_seconds_remaining,
            1,
            10,
            format_field_position(100 - state.yardline_100, self.game.away if state.posteam == self.game.home else self.game.home , self.game.home, self.game.away),
            100 - state.yardline_100,
            0,
            state.score_differential,
            self.game.away if state.posteam == self.game.home else self.game.home ,
        )

    def simulate_incompletion(self, state, num):
        yards_gained = 0
        is_complete = False
        return PassEvent(
            "Simulated pass play: " + ("complete" if is_complete else "incomplete") + ", gain of " + str(yards_gained) + " yards",
            state.home_score,
            state.away_score,
            state.qtr,
            state.quarter_seconds_remaining,
            state.half_seconds_remaining,
            state.game_seconds_remaining,
            state.down + 1 if state.to_go > yards_gained else 1,
            state.to_go - yards_gained if state.to_go > yards_gained else 10,
            format_field_position(max(0, state.yardline_100 - yards_gained), state.posteam, self.game.home, self.game.away),
            max(0, state.yardline_100 - yards_gained),
            yards_gained,
            state.score_differential,
            state.posteam,
            is_complete=is_complete,
        )
    
    def simulate_rush(self, state, num):
        yards_gained = max(-10, int(random.gauss(self.game.stats[state.posteam]['avg_yards_per_carry'], 3)))
        if state.yardline_100 - yards_gained <= 0:
            state.home_score += 6 if state.posteam == self.game.home else 0
            state.away_score += 6 if state.posteam == self.game.away else 0
            state.score_differential = state.home_score - state.away_score

            rush_event = RushEvent(
                "Simulated rush play, gain of " + str(yards_gained) + " yards. Touchdown by " + state.posteam + "!",
                state.home_score,
                state.away_score,
                state.qtr,
                state.quarter_seconds_remaining,
                state.half_seconds_remaining,
                state.game_seconds_remaining,
                1,
                10,
                (self.game.away if state.posteam == self.game.home else self.game.home) + " " + str(25),
                75,
                yards_gained,
                state.score_differential,
                self.game.away if state.posteam == self.game.home else self.game.home
            )
            pat_type = self.decide_pat_type(state)
            if pat_type == "XP_KICK":
                xp_event = self.simulate_xpat(state, num)
                return (rush_event, xp_event)
            else:
                pat2_event = self.simulate_2pat(state, num)
                return (rush_event, pat2_event)
        return RushEvent(
            "Simulated rush play, gain of " + str(yards_gained) + " yards",
            state.home_score,
            state.away_score,
            state.qtr,
            state.quarter_seconds_remaining,
            state.half_seconds_remaining,
            state.game_seconds_remaining,
            state.down + 1 if state.to_go > yards_gained else 1,
            state.to_go - yards_gained if state.to_go > yards_gained else 10,
            format_field_position(max(0, state.yardline_100 - yards_gained), state.posteam, self.game.home, self.game.away),
            max(0, state.yardline_100 - yards_gained),
            yards_gained,
            state.score_differential,
            state.posteam
        )
    
    def simulate_field_goal(self, state, num, made=None):
        fg_distance = state.yardline_100 + 17
        fg_prob = 1 / (1 + math.exp(-.2 * (fg_distance - 35)))
        if made is not None:
            if made:
                num = 0
            else:
                num = 1
        if num < fg_prob * self.game.stats[state.posteam]['field_goal_prob']:
            is_good = True
            state.home_score += 3 if state.posteam == self.game.home else 0
            state.away_score += 3 if state.posteam == self.game.away else 0
            score_differential = state.score_differential + 3 if state.posteam == self.game.away else state.score_differential - 3
        else:
            is_good = False
            score_differential = state.score_differential
        return FieldGoalEvent(
            "Simulated field goal attempt from " + str(fg_distance) + " yards, by " + state.posteam + ", " + ("good" if is_good else "no good"),
            state.home_score,
            state.away_score,
            state.qtr,
            state.quarter_seconds_remaining,
            state.half_seconds_remaining,
            state.game_seconds_remaining,
            1,
            10,
            format_field_position(100 - state.yardline_100 if not is_good else 75, self.game.away if state.posteam == self.game.home else self.game.home, self.game.home, self.game.away),
            100 - state.yardline_100 if not is_good else 75,
            0,
            score_differential,
            self.game.away if state.posteam == self.game.home else self.game.home,
            is_good=is_good
        )
    
    def simulate_punt(self, state, num):
        punt_distance = max(20, int(random.gauss(45, 10)))
        new_yardline = 25 if state.yardline_100 - punt_distance <= 0 else state.yardline_100 - punt_distance
        return PuntEvent(
            "Simulated punt, distance of " + str(punt_distance) + " yards",
            state.home_score,
            state.away_score,
            state.qtr,
            state.quarter_seconds_remaining,
            state.half_seconds_remaining,
            state.game_seconds_remaining,
            1,
            10,
            format_field_position(max(0, 100 - new_yardline), self.game.away if state.posteam == self.game.home else self.game.home, self.game.home, self.game.away),
            100 - new_yardline,
            0,
            state.score_differential,
            self.game.away if state.posteam == self.game.home else self.game.home
        )

    def simulate_xpat(self, state, num, made=None):
        xp_distance = 33
        xp_prob = 0.95
        is_good = num < xp_prob * self.game.stats[state.posteam]['extra_point_prob']
        if made is not None:
            is_good = made
        if is_good:
            state.home_score += 1 if state.posteam == self.game.home else 0
            state.away_score += 1 if state.posteam == self.game.away else 0
            state.score_differential = state.home_score - state.away_score
        return XPEvent(
            "Simulated extra point attempt from " + str(xp_distance) + " yards, by " + state.posteam + ", " + ("good" if is_good else "no good"),
            state.home_score,
            state.away_score,
            state.qtr,
            state.quarter_seconds_remaining,
            state.half_seconds_remaining,
            state.game_seconds_remaining,
            1,
            10,
            format_field_position(75, state.posteam, self.game.home, self.game.away),
            75,
            0,
            state.score_differential,
            self.game.away if state.posteam == self.game.home else self.game.home,
            is_good=is_good
        )
    def simulate_2pat(self, state, num, made=None):
        pat2_distance = 3
        pat2_prob = 0.45
        is_good = num < pat2_prob * self.game.stats[state.posteam]['two_point_conversion_prob']
        if made is not None:
            is_good = made
        if is_good:
            state.home_score += 2 if state.posteam == self.game.home else 0
            state.away_score += 2 if state.posteam == self.game.away else 0
            state.score_differential = state.home_score - state.away_score
        return PAT2Event(
            "Simulated 2 point attempt from " + str(pat2_distance) + " yards, by " + state.posteam + ", " + ("converted" if is_good else "not converted"),
            state.home_score,
            state.away_score,
            state.qtr,
            state.quarter_seconds_remaining,
            state.half_seconds_remaining,
            state.game_seconds_remaining,
            1,
            10,
            format_field_position(75, state.posteam, self.game.home, self.game.away),
            75,
            0,
            state.score_differential,
            self.game.away if state.posteam == self.game.home else self.game.home,
            is_good=is_good
        )
                    
    def simulate_next_play(self, state):
        play_type = self.decide_play_type(state)
        time_lost = random.randint(20, 40)
        state.quarter_seconds_remaining = state.quarter_seconds_remaining - time_lost
        if state.quarter_seconds_remaining <= 0:
            state.qtr += 1
            if state.qtr in [2, 4]:
                state.half_seconds_remaining = 900
            else:
                state.half_seconds_remaining = 1800
            state.quarter_seconds_remaining = 900
            state.game_seconds_remaining = 3600 - (state.qtr - 1) * 900
        
        num = random.random()
        
        if play_type == "PASS":
            if num < self.game.stats[state.posteam]['completion_prob']:
                return self.simulate_completion(state, num)
            elif num < self.game.stats[state.posteam]['completion_prob'] + self.game.stats[state.posteam]['interception_prob']:
                return self.simulate_interception(state, num)
            else:
                return self.simulate_incompletion(state, num)
        elif play_type == "RUSH":
            return self.simulate_rush(state, num)
        elif play_type == "FIELD_GOAL":
           return self.simulate_field_goal(state, num)
        elif play_type == "PUNT":
            return self.simulate_punt(state, num)