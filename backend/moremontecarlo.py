import sys
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import json
import numpy as np
from collections import Counter
from enum import Enum

class PlayType(Enum):
    PASS = "pass"
    RUSH = "rush"
    PUNT = "punt"
    FIELD_GOAL = "field_goal"
    EXTRA_POINT = "extra_point"
    TWO_POINT = "two_point_conversion"
    KICKOFF = "kickoff"
    PENALTY = "penalty"

class PlayResult(Enum):
    COMPLETE = "complete"
    INCOMPLETE = "incomplete"
    INTERCEPTION = "interception"
    FUMBLE = "fumble"
    TOUCHDOWN = "touchdown"
    FIRST_DOWN = "first_down"
    SUCCESS = "success"
    FAILURE = "failure"
    GOOD = "good"
    MISSED = "missed"
    BLOCKED = "blocked"

@dataclass
class PlayEvent:
    play_id: int
    quarter: int
    time_remaining: int  # seconds
    down: int
    yards_to_go: int
    yard_line: int  # field position (0-100, 50 = midfield)
    team: str
    play_type: PlayType
    
    # Play specifics
    is_pass: bool = False
    is_complete: bool = False
    is_interception: bool = False
    is_fumble: bool = False
    yards_gained: int = 0
    is_touchdown: bool = False
    is_first_down: bool = False
    
    # Conversions
    third_down_converted: bool = False
    fourth_down_converted: bool = False
    go_for_it_on_fourth: bool = False
    punt_result: Optional[str] = None
    
    # Scoring plays
    extra_point_result: Optional[PlayResult] = None
    two_point_result: Optional[PlayResult] = None
    field_goal_result: Optional[PlayResult] = None
    
    # Game management
    penalties: List[str] = field(default_factory=list)
    timeout_called: bool = False
    timeout_team: Optional[str] = None
    
    points_scored: int = 0

    def calculate_points(self):
        """Calculate points based on play outcome"""
        points = 0
        if self.is_touchdown:
            points += 6
        if self.extra_point_result == PlayResult.GOOD:
            points += 1
        if self.two_point_result == PlayResult.SUCCESS:
            points += 2
        if self.field_goal_result == PlayResult.GOOD:  
            points += 3
        
        # Safety (if applicable)
        if self.play_type == PlayType.PENALTY and "safety" in [p.lower() for p in self.penalties]:
            points += 2
            
        self.points_scored = points
        return points

@dataclass
class GameState:
    game_id: str
    home_team: str
    away_team: str
    home_score: int
    away_score: int
    quarter: int
    time_remaining: int
    possession: str  # which team has the ball
    down: int
    yards_to_go: int
    yard_line: int
    home_timeouts: int = 3
    away_timeouts: int = 3
    plays: List[PlayEvent] = field(default_factory=list)
    
    def add_play(self, play: PlayEvent):
        """Add a play and update game state"""
        self.plays.append(play)
        
        # Update score
        if play.team == self.home_team:
            self.home_score += play.calculate_points()
        else:
            self.away_score += play.calculate_points()
            
        # Update timeouts
        if play.timeout_called:
            if play.timeout_team == self.home_team:
                self.home_timeouts = max(0, self.home_timeouts - 1)
            else:
                self.away_timeouts = max(0, self.away_timeouts - 1)
    
    def clone(self):
        """Create a deep copy for what-if scenarios"""
        import copy
        return copy.deepcopy(self)

class ComprehensiveMonteCarloSimulator:
    def __init__(self, trials: int = 10000):
        self.trials = trials
        
        # Comprehensive NFL probabilities based on real data
        self.probabilities = {
            "pass_complete": 0.65,
            "pass_incomplete": 0.32,
            "interception": 0.03,
            "rush_success": 0.85,
            "fumble": 0.02,
            "third_down_conversion": 0.42,
            "fourth_down_conversion": 0.55,
            "go_for_it_fourth": 0.15,  # vs punt
            "extra_point_good": 0.94,
            "two_point_success": 0.48,
            "field_goal_success": {
                "under_30": 0.97,
                "30_39": 0.93,
                "40_49": 0.85,
                "50_plus": 0.65
            },
            "punt_touchback": 0.25,
            "penalty_rate": 0.08,
            "timeout_usage": 0.05
        }
        print(f"   Trials per simulation: {trials:,}")

    def simulate_remaining_game(self, game_state: GameState, remaining_drives: int = 8) -> Dict:
        """
        Complete Monte Carlo simulation using all NFL factors with NumPy vectorization
        """
        print(f"Running {self.trials:,} Monte Carlo simulations...")
        print(f"   Starting: {game_state.away_team} {game_state.away_score} - {game_state.home_score} {game_state.home_team}")
        print(f"   Simulating {remaining_drives} remaining drives...")
        
        # ADVANCED: Context-aware probabilities based on game situation
        time_factor = max(0.5, game_state.time_remaining / 900)  # More urgency = more passing
        score_diff = abs(game_state.home_score - game_state.away_score)
        trailing_factor = 1.0 + (score_diff / 20)  # Trailing teams take more risks
        
        # Base drive outcome probabilities (NFL 2023 season averages)
        base_outcomes = {
            "touchdown": 0.195,      # 19.5% - includes 94% XP success
            "field_goal": 0.175,     # 17.5% - includes distance-based success rates
            "turnover_defense": 0.11, # 11% - INT/Fumble lost
            "turnover_offense": 0.09, # 9% - Fumble recovered by offense
            "punt": 0.36,            # 36% - Most common outcome
            "safety": 0.008,         # 0.8% - Rare but game-changing
            "missed_fg": 0.052       # 5.2% - Failed FG attempts
        }
        
        # ADVANCED: Adjust probabilities based on game context
        drive_outcomes = base_outcomes.copy()
        if time_factor < 0.8:  # Late in game = more aggressive
            drive_outcomes["touchdown"] *= (1 + trailing_factor * 0.15)
            drive_outcomes["field_goal"] *= (1 + trailing_factor * 0.1)  
            drive_outcomes["punt"] *= 0.85  # Less punting when behind
        
        # Normalize to ensure probabilities sum to 1
        total = sum(drive_outcomes.values())
        drive_outcomes = {k: v/total for k, v in drive_outcomes.items()}
        
        # Convert to NumPy arrays for vectorized operations
        outcomes = np.array(list(drive_outcomes.keys()))
        weights = np.array(list(drive_outcomes.values()))
        weights = weights / np.sum(weights)  # Normalize
        
        # Point mapping with realistic NFL scoring
        point_map = {
            "touchdown": 7,           # TD + XP
            "field_goal": 3,          # FG
            "turnover_defense": 0,    # No points for offense
            "turnover_offense": 0,    # No points
            "punt": 0,                # No points
            "safety": 2,              # 2 points for defense (opposite team)
            "missed_fg": 0            # No points
        }
        
        point_values = np.array([point_map[outcome] for outcome in outcomes])
        
        # Generate all outcomes at once (VECTORIZED!)
        outcome_indices = np.random.choice(
            len(outcomes),
            size=(self.trials, remaining_drives),
            p=weights
        )
        
        points_per_drive = point_values[outcome_indices]
        
        # Handle safety points (go to opposite team)
        safety_mask = outcomes[outcome_indices] == "safety"
        points_per_drive = np.where(safety_mask, -2, points_per_drive)  # -2 means opponent gets 2
        
        # Alternating possession (0 = home team, 1 = away team)
        possession = np.arange(remaining_drives) % 2
        
        # Calculate points for each team using broadcasting
        home_points_matrix = points_per_drive * (1 - possession)  # Home team drives
        away_points_matrix = points_per_drive * possession        # Away team drives
        
        # Handle safeties (points go to defending team)
        home_points_matrix = np.where(
            (safety_mask) & (possession == 1), 2, home_points_matrix  # Away team drive, home gets safety
        )
        away_points_matrix = np.where(
            (safety_mask) & (possession == 0), 2, away_points_matrix  # Home team drive, away gets safety
        )
        
        # Sum additional points across all drives
        additional_home_points = np.sum(home_points_matrix, axis=1)
        additional_away_points = np.sum(away_points_matrix, axis=1)
        
        # Calculate final scores
        final_home_scores = game_state.home_score + additional_home_points
        final_away_scores = game_state.away_score + additional_away_points
        
        # Win/loss calculations
        home_wins = np.sum(final_home_scores > final_away_scores)
        away_wins = np.sum(final_away_scores > final_home_scores)
        ties = np.sum(final_home_scores == final_away_scores)
        
        # Statistical analysis
        avg_home = np.mean(final_home_scores)
        avg_away = np.mean(final_away_scores)
        std_home = np.std(final_home_scores)
        std_away = np.std(final_away_scores)
        
        home_win_prob = (home_wins + ties * 0.5) / self.trials
        away_win_prob = (away_wins + ties * 0.5) / self.trials
        
        result = {
            "avg_home_score": float(avg_home),
            "avg_away_score": float(avg_away),
            "std_home_score": float(std_home),
            "std_away_score": float(std_away),
            "home_win_probability": float(home_win_prob),
            "away_win_probability": float(away_win_prob),
            "trials_run": self.trials,
            "home_wins": int(home_wins),
            "away_wins": int(away_wins),
            "ties": int(ties),
            "score_differential": float(avg_home - avg_away)
        }
        
        print(f"   Projected final: {game_state.away_team} {avg_away:.1f}±{std_away:.1f} - {avg_home:.1f}±{std_home:.1f} {game_state.home_team}")
        print(f"   Win probability: {game_state.home_team} {home_win_prob:.1%}, {game_state.away_team} {away_win_prob:.1%}")
        print(f"   Outcome distribution: {home_wins} home wins, {away_wins} away wins, {ties} ties")
        
        return result

    def simulate_drive(self, game_state: GameState) -> GameState:
        """Simulate a single drive with all NFL factors"""
        current_state = game_state.clone()
        drive_plays = []
        
        down = 1
        yards_to_go = 10
        yard_line = 25  # Starting field position
        
        while down <= 4 and yard_line < 100:
            # Determine play type
            if down == 4:
                if np.random.random() < self.probabilities["go_for_it_fourth"]:
                    play_type = PlayType.PASS if np.random.random() < 0.6 else PlayType.RUSH
                else:
                    if yard_line > 65:  # Field goal range
                        play_type = PlayType.FIELD_GOAL
                    else:
                        play_type = PlayType.PUNT
            else:
                play_type = PlayType.PASS if np.random.random() < 0.6 else PlayType.RUSH
            
            play = PlayEvent(
                play_id=len(current_state.plays) + len(drive_plays) + 1,
                quarter=current_state.quarter,
                time_remaining=current_state.time_remaining,
                down=down,
                yards_to_go=yards_to_go,
                yard_line=yard_line,
                team=current_state.possession,
                play_type=play_type
            )
            
            # Simulate play outcome
            if play_type == PlayType.PASS:
                play.is_pass = True
                rand = np.random.random()
                if rand < self.probabilities["interception"]:
                    play.is_interception = True
                    break  # Drive over
                elif rand < self.probabilities["pass_complete"]:
                    play.is_complete = True
                    play.yards_gained = np.random.randint(3, 15)
                else:
                    play.is_complete = False
                    play.yards_gained = 0
                    
            elif play_type == PlayType.RUSH:
                if np.random.random() < self.probabilities["fumble"]:
                    play.is_fumble = True
                    break  # Drive over
                else:
                    play.yards_gained = np.random.randint(1, 8)
                    
            elif play_type == PlayType.FIELD_GOAL:
                distance = 100 - yard_line + 17  # Distance to goal posts
                if distance < 30:
                    success_rate = self.probabilities["field_goal_success"]["under_30"]
                elif distance < 40:
                    success_rate = self.probabilities["field_goal_success"]["30_39"]
                elif distance < 50:
                    success_rate = self.probabilities["field_goal_success"]["40_49"]
                else:
                    success_rate = self.probabilities["field_goal_success"]["50_plus"]
                    
                if np.random.random() < success_rate:
                    play.field_goal_result = PlayResult.GOOD
                    play.points_scored = 3
                else:
                    play.field_goal_result = PlayResult.MISSED
                break  # Drive over
                
            elif play_type == PlayType.PUNT:
                play.punt_result = "touchback" if np.random.random() < self.probabilities["punt_touchback"] else "normal"
                break  # Drive over
            
            # Check for penalties
            if np.random.random() < self.probabilities["penalty_rate"]:
                penalties = ["holding", "false_start", "pass_interference", "roughing"]
                play.penalties.append(np.random.choice(penalties))
                
            # Check for timeout
            if np.random.random() < self.probabilities["timeout_usage"]:
                play.timeout_called = True
                play.timeout_team = current_state.possession
            
            # Update field position
            yard_line = min(100, yard_line + play.yards_gained)
            
            # Check for touchdown
            if yard_line >= 100:
                play.is_touchdown = True
                play.points_scored = 6
                
                # Extra point or two-point conversion
                if np.random.random() < 0.95:  # Usually go for extra point
                    if np.random.random() < self.probabilities["extra_point_good"]:
                        play.extra_point_result = PlayResult.GOOD
                        play.points_scored += 1
                    else:
                        play.extra_point_result = PlayResult.MISSED
                else:  # Two-point conversion
                    if np.random.random() < self.probabilities["two_point_success"]:
                        play.two_point_result = PlayResult.SUCCESS
                        play.points_scored += 2
                    else:
                        play.two_point_result = PlayResult.FAILURE
                break
            
            # Update down and distance
            if play.yards_gained >= yards_to_go:
                play.is_first_down = True
                if down == 3:
                    play.third_down_converted = True
                elif down == 4:
                    play.fourth_down_converted = True
                down = 1
                yards_to_go = 10
            else:
                down += 1
                yards_to_go -= play.yards_gained
            
            drive_plays.append(play)
        
        # Add all plays to game state
        for play in drive_plays:
            current_state.add_play(play)
            
        return current_state

def create_comprehensive_sample_game() -> GameState:
    """Create a detailed sample game with all factors"""
    game = GameState(
        game_id="2023_week1_ari_was",
        home_team="WAS",
        away_team="ARI", 
        home_score=20,
        away_score=16,
        quarter=4,
        time_remaining=300,  # 5 minutes left
        possession="ARI",
        down=1,
        yards_to_go=10,
        yard_line=35
    )
    
    # Add comprehensive sample plays
    sample_plays = [
        # Q1 - WAS TD Drive
        PlayEvent(1, 1, 800, 1, 10, 25, "WAS", PlayType.PASS, is_pass=True, is_complete=True, yards_gained=12, is_first_down=True),
        PlayEvent(2, 1, 750, 1, 10, 37, "WAS", PlayType.RUSH, yards_gained=8),
        PlayEvent(3, 1, 700, 2, 2, 45, "WAS", PlayType.RUSH, yards_gained=3, is_first_down=True),
        PlayEvent(4, 1, 650, 1, 10, 48, "WAS", PlayType.PASS, is_pass=True, is_complete=True, yards_gained=25, is_first_down=True),
        PlayEvent(5, 1, 600, 1, 10, 73, "WAS", PlayType.PASS, is_pass=True, is_complete=True, yards_gained=27, is_touchdown=True, points_scored=6),
        PlayEvent(6, 1, 590, 0, 0, 0, "WAS", PlayType.EXTRA_POINT, extra_point_result=PlayResult.GOOD, points_scored=1),
        
        # Q1 - ARI FG Drive  
        PlayEvent(7, 1, 400, 1, 10, 30, "ARI", PlayType.PASS, is_pass=True, is_complete=True, yards_gained=15, is_first_down=True),
        PlayEvent(8, 1, 350, 1, 10, 45, "ARI", PlayType.RUSH , yards_gained=5),
        PlayEvent(9, 1, 300, 2, 5, 50, "ARI", PlayType.PASS, is_pass=True, is_complete=False),
        PlayEvent(10, 1, 250, 3, 5, 50, "ARI", PlayType.PASS, is_pass=True, is_complete=True, yards_gained=8, is_first_down=True, third_down_converted=True),
        PlayEvent(11, 1, 200, 1, 10, 58, "ARI", PlayType.RUSH, yards_gained=12, is_first_down=True),
        PlayEvent(12, 1, 150, 1, 10, 70, "ARI", PlayType.PASS, is_pass=True, is_complete=True, yards_gained=8),
        PlayEvent(13, 1, 100, 2, 2, 78, "ARI", PlayType.RUSH, yards_gained=1),
        PlayEvent(14, 1, 50, 3, 1, 79, "ARI", PlayType.PASS, is_pass=True, is_complete=False),
        PlayEvent(15, 1, 10, 4, 1, 79, "ARI", PlayType.FIELD_GOAL, field_goal_result=PlayResult.GOOD, points_scored=3),
    ]
    
    for play in sample_plays:
        game.add_play(play)
    
    return game

def interactive_play_modifier(play: PlayEvent) -> PlayEvent:
    """Allow user to interactively modify any aspect of a play"""
    print(f"\n MODIFYING PLAY {play.play_id}")
    print(f"Current: Q{play.quarter}, {play.team} {play.play_type.value}")
    print(f"Down: {play.down}, Yards to go: {play.yards_to_go}, Yard line: {play.yard_line}")
    print("Enter new values (press Enter to keep current):")
    
    modified_play = play.clone() if hasattr(play, 'clone') else PlayEvent(**play.__dict__)
    
    # Pass completion
    if play.play_type == PlayType.PASS:
        current = "complete" if play.is_complete else "incomplete"
        if play.is_interception:
            current = "interception"
        
        new_result = input(f"Pass result [{current}] (complete/incomplete/int): ").strip().lower()
        if new_result:
            if new_result in ["int", "interception"]:
                modified_play.is_interception = True
                modified_play.is_complete = False
            elif new_result == "complete":
                modified_play.is_complete = True
                modified_play.is_interception = False
            elif new_result == "incomplete":
                modified_play.is_complete = False
                modified_play.is_interception = False
    
    # Fumble
    current_fumble = "yes" if play.is_fumble else "no"
    fumble_input = input(f"Fumble [{current_fumble}] (yes/no): ").strip().lower()
    if fumble_input:
        modified_play.is_fumble = fumble_input == "yes"
    
    # Third down conversion
    if play.down == 3:
        current_3rd = "yes" if play.third_down_converted else "no"
        third_input = input(f"Third down converted [{current_3rd}] (yes/no): ").strip().lower()
        if third_input:
            modified_play.third_down_converted = third_input == "yes"
    
    # Fourth down
    if play.down == 4:
        current_4th = "yes" if play.fourth_down_converted else "no"
        fourth_input = input(f"Fourth down converted [{current_4th}] (yes/no): ").strip().lower()
        if fourth_input:
            modified_play.fourth_down_converted = fourth_input == "yes"
            
        current_go = "yes" if play.go_for_it_on_fourth else "no"
        go_input = input(f"Go for it on fourth [{current_go}] (yes/no): ").strip().lower()
        if go_input:
            modified_play.go_for_it_on_fourth = go_input == "yes"
    
    # Extra point
    if play.extra_point_result:
        current_xp = play.extra_point_result.value
        xp_input = input(f"Extra point [{current_xp}] (good/missed): ").strip().lower()
        if xp_input:
            modified_play.extra_point_result = PlayResult.GOOD if xp_input == "good" else PlayResult.MISSED
    
    # Two point conversion
    if play.two_point_result:
        current_2pt = play.two_point_result.value
        twopoint_input = input(f"Two point conversion [{current_2pt}] (success/failure): ").strip().lower()
        if twopoint_input:
            modified_play.two_point_result = PlayResult.SUCCESS if twopoint_input == "success" else PlayResult.FAILURE
    
    # Field goal
    if play.field_goal_result:
        current_fg = play.field_goal_result.value
        fg_input = input(f"Field goal [{current_fg}] (good/missed/blocked): ").strip().lower()
        if fg_input:
            if fg_input == "good":
                modified_play.field_goal_result = PlayResult.GOOD
            elif fg_input == "missed":
                modified_play.field_goal_result = PlayResult.MISSED
            elif fg_input == "blocked":
                modified_play.field_goal_result = PlayResult.BLOCKED
    
    # Penalties
    current_penalties = ", ".join(play.penalties) if play.penalties else "none"
    penalty_input = input(f"Penalties [{current_penalties}] (comma separated or 'none'): ").strip()
    if penalty_input:
        if penalty_input.lower() == "none":
            modified_play.penalties = []
        else:
            modified_play.penalties = [p.strip() for p in penalty_input.split(",")]
    
    # Timeouts
    current_timeout = f"{play.timeout_team}" if play.timeout_called else "none"
    timeout_input = input(f"Timeout called [{current_timeout}] (team name or 'none'): ").strip()
    if timeout_input:
        if timeout_input.lower() == "none":
            modified_play.timeout_called = False
            modified_play.timeout_team = None
        else:
            modified_play.timeout_called = True
            modified_play.timeout_team = timeout_input.upper()
    
    # Recalculate points
    modified_play.calculate_points()
    
    return modified_play

def main():
    
    # Create comprehensive sample game
    game = create_comprehensive_sample_game()
    
    print(f"\n SAMPLE GAME: {game.away_team} @ {game.home_team}")
    print(f"Current Score: {game.away_team} {game.away_score} - {game.home_score} {game.home_team}")
    print(f"Game State: Q{game.quarter}, {game.time_remaining}s remaining")
    print(f"Possession: {game.possession}, {game.down} & {game.yards_to_go} at {game.yard_line}")
    
    print(f"\nRECENT SCORING PLAYS:")
    scoring_plays = [p for p in game.plays if p.points_scored > 0]
    for i, play in enumerate(scoring_plays[-5:], 1):  # Last 5 scoring plays
        play_desc = f"{play.play_type.value}"
        if play.field_goal_result:
            play_desc += f" {play.field_goal_result.value}"
        elif play.is_touchdown:
            play_desc += " touchdown"
        print(f"  {i}. Q{play.quarter}: {play.team} {play_desc} (+{play.points_scored})")
    
    # Set up comprehensive simulator
    simulator = ComprehensiveMonteCarloSimulator(trials=5000)
    
    print("set baseline")
    
    # Run baseline simulation
    print("BASELINE SIMULATION (Current Game State)")
    original_result = simulator.simulate_remaining_game(game)
    
    print("INTERACTIVE PLAY MODIFICATION")
    
    # Let user choose which plays to modify
    print("Available plays to modify:")
    for i, play in enumerate(game.plays[-10:], 1):  # Last 10 plays
        desc = f"{play.play_type.value}"
        if play.is_touchdown:
            desc += " (TD)"
        elif play.field_goal_result:
            desc += f" ({play.field_goal_result.value})"
        print(f"  {i}. Play {play.play_id}: Q{play.quarter} {play.team} {desc}")
    
    try:
        choice = input(f"\nWhich play to modify (1-{min(10, len(game.plays))})? ")
        if choice.isdigit():
            play_index = int(choice) - 1
            if 0 <= play_index < min(10, len(game.plays)):
                selected_play = game.plays[-(10-play_index)]
                
                # Modify the play interactively
                modified_play = interactive_play_modifier(selected_play)
                
                # Create modified game
                modified_game = game.clone()
                # Replace the play in the modified game
                for i, play in enumerate(modified_game.plays):
                    if play.play_id == selected_play.play_id:
                        modified_game.plays[i] = modified_play
                        break
                
                # Recalculate score
                modified_game.home_score = 0
                modified_game.away_score = 0
                for play in modified_game.plays:
                    if play.team == modified_game.home_team:
                        modified_game.home_score += play.points_scored
                    else:
                        modified_game.away_score += play.points_scored
                
                print(f"Original Score:  {game.away_team} {game.away_score} - {game.home_score} {game.home_team}")
                print(f"Modified Score:  {modified_game.away_team} {modified_game.away_score} - {modified_game.home_score} {modified_game.home_team}")
                
                print(f"   Score difference: {abs(modified_game.away_score + modified_game.home_score - game.away_score - game.home_score)} points")
                
                # Run modified simulation
                print("MODIFIED SIMULATION")
                modified_result = simulator.simulate_remaining_game(modified_game)
                
                # Compare results
                print("IMPACT ANALYSIS")
                print(f"Projected Finals:")
                print(f"Original:  {game.away_team} {original_result['avg_away_score']:.1f} - {original_result['avg_home_score']:.1f} {game.home_team}")
                print(f"Modified:  {modified_game.away_team} {modified_result['avg_away_score']:.1f} - {modified_result['avg_home_score']:.1f} {modified_game.home_team}")
                
                print(f"\nWin Probability Changes:")
                home_change = modified_result['home_win_probability'] - original_result['home_win_probability']
                away_change = modified_result['away_win_probability'] - original_result['away_win_probability']
                print(f"{game.home_team}: {original_result['home_win_probability']:.1%} → {modified_result['home_win_probability']:.1%} ({home_change:+.1%})")
                print(f"{game.away_team}: {original_result['away_win_probability']:.1%} → {modified_result['away_win_probability']:.1%} ({away_change:+.1%})")
                
                print(f"\n INSIGHT:")
                if abs(home_change) > 0.05:  # 5% threshold
                    impact_team = game.home_team if home_change > 0 else game.away_team
                    print(f"   This change significantly helps {impact_team} win by {abs(home_change):.1%}!")
                else:
                    print(f"   This change has minimal impact on the game outcome.")
                
    except (ValueError, IndexError):
        print("Invalid selection. Using default modification...")

if __name__ == "__main__":
    main()