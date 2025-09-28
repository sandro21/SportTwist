import nflreadpy as nfl
import pandas as pd
import numpy as np
import random
import math
from game import (Game, PassEvent, RushEvent, FieldGoalEvent, XPEvent, InterceptionEvent, PenaltyEvent)



def find_game_id(year, team1, team2):
    """Finds the game_id for a matchup in a given year."""
    try:
        schedule = nfl.load_schedules([year]).to_pandas()
        game = schedule[
            ((schedule['home_team'] == team1) & (schedule['away_team'] == team2)) |
            ((schedule['home_team'] == team2) & (schedule['away_team'] == team1))
        ]
        if not game.empty:
            return game.iloc[0]['game_id']
    except Exception as e:
        print(f"Could not fetch schedule data: {e}")
    return None

def display_all_plays(game):
    """Displays ALL plays from the game with filtering options."""
    print("\nALL PLAYS FROM THE GAME:")
    
    # Show filtering options
    print("\nFilter Options:")
    print("1. Show ALL plays")
    print("2. Show only scoring plays")
    print("3. Show only turnovers")
    print("4. Show only big plays (15+ yards)")
    print("5. Show only red zone plays")
    print("6. Show only 3rd/4th down plays")
    print("7. Show only field goals/XPs")
    print("8. Show only penalties")
    
    while True:
        try:
            filter_choice = int(input("\nChoose filter (1-8): "))
            if 1 <= filter_choice <= 8:
                break
            print("Please enter a number between 1 and 8.")
        except ValueError:
            print("Please enter a valid number.")
    
    displayed_plays = []
    print(f"\n{'Index':<6} {'Quarter':<8} {'Time':<8} {'Down':<8} {'Yards':<8} {'Team':<6} {'Description'}")
    print("-" * 120)
    
    for i, play in enumerate(game.plays):
        should_display = False
        
        if filter_choice == 1:  # All plays
            should_display = True
        elif filter_choice == 2:  # Scoring plays
            should_display = (play.points is not None and play.points != 0) or isinstance(play, (FieldGoalEvent, XPEvent))
        elif filter_choice == 3:  # Turnovers
            should_display = isinstance(play, InterceptionEvent) or (hasattr(play, 'is_fumble') and play.is_fumble)
        elif filter_choice == 4:  # Big plays
            should_display = abs(play.yards_gained) >= 15
        elif filter_choice == 5:  # Red zone
            should_display = play.yardline_100 <= 20
        elif filter_choice == 6:  # 3rd/4th down
            should_display = play.down in [3, 4]
        elif filter_choice == 7:  # FG/XP
            should_display = isinstance(play, (FieldGoalEvent, XPEvent))
        elif filter_choice == 8:  # Penalties
            should_display = isinstance(play, PenaltyEvent)
        
        if should_display:
            minutes = int(play.game_seconds_remaining) // 60
            seconds = int(play.game_seconds_remaining) % 60
            down_str = f"{play.down}-{play.to_go}" if play.down else "N/A"
            desc = play.desc.split('\n')[0][:60] + "..." if len(play.desc.split('\n')[0]) > 60 else play.desc.split('\n')[0]
            
            print(f"{i:<6} Q{play.qtr:<7} {minutes}:{seconds:02d}   {down_str:<8} {play.yards_gained:<8} {play.posteam:<6} {desc}")
            displayed_plays.append((i, play))
    
    print(f"\nShowing {len(displayed_plays)} plays out of {len(game.plays)} total plays.")
    return displayed_plays

def get_core_modification(play):
    """Core NFL modification system - ONLY the essential game factors."""
    print(f"\n{'='*80}")
    print(f"SELECTED PLAY: {play.desc.splitlines()[0][:75]}...")
    print(f"{'='*80}")
    print(f"Q{play.qtr} | {int(play.game_seconds_remaining)//60}:{int(play.game_seconds_remaining)%60:02d} | {play.down}-{play.to_go} | {play.posteam} | Yards: {play.yards_gained}")
    
    modifications = []
    
    # Pass Play Modifications
    if isinstance(play, PassEvent):
        print(f"\nPASS PLAY - Current: {'COMPLETE' if play.is_complete else 'INCOMPLETE'}")
        modifications.extend([
            ("make_complete", "Make pass COMPLETE"),
            ("make_incomplete", "Make pass INCOMPLETE"), 
            ("turn_to_interception", "Turn into INTERCEPTION"),
            ("add_fumble", "Add FUMBLE after catch"),
            ("convert_third_down", "Convert 3rd down (if applicable)"),
            ("add_penalty", "Add penalty"),
            ("add_timeout", "Add timeout")
        ])
    
    # Rush Play Modifications  
    elif isinstance(play, RushEvent):
        print(f"\n RUSH PLAY - Current: {play.yards_gained} yards")
        modifications.extend([
            ("add_fumble", "Add FUMBLE"),
            ("remove_fumble", "Remove fumble"),
            ("convert_third_down", "Convert 3rd down (if applicable)"),
            ("convert_fourth_down", "Convert 4th down (if applicable)"),
            ("add_penalty", "Add penalty"),
            ("add_timeout", "Add timeout")
        ])
    
    # Interception Modifications
    elif isinstance(play, InterceptionEvent):
        print(f"\n INTERCEPTION - Current return: {play.yards_gained} yards")
        modifications.extend([
            ("make_incomplete", "Make it INCOMPLETE pass instead"),
            ("make_complete", "Make it COMPLETE pass instead"),
            ("change_return_yards", "Change return yards"),
            ("add_fumble", "Add fumble on return")
        ])
    
    # Field Goal Modifications
    elif isinstance(play, FieldGoalEvent):
        print(f"\n FIELD GOAL - Current: {'GOOD' if play.is_good else 'MISS'}")
        modifications.extend([
            ("make_good", "Make field goal GOOD"),
            ("make_miss", "Make field goal MISS"),
            ("add_timeout", "Add timeout (icing)")
        ])
    
    # Extra Point Modifications
    elif isinstance(play, XPEvent):
        print(f"\n EXTRA POINT - Current: {'GOOD' if play.is_good else 'MISS'}")
        modifications.extend([
            ("make_good", "Make extra point GOOD"),
            ("make_miss", "Make extra point MISS"),
            ("convert_to_2pt", "Convert to 2-POINT conversion")
        ])
    
    # Fourth Down Situations
    if play.down == 4:
        print(f"\n 4TH DOWN SITUATION")
        modifications.extend([
            ("go_for_it", "GO FOR IT (convert 4th down)"),
            ("punt_instead", "PUNT instead")
        ])
    
    # Penalty Modifications
    elif isinstance(play, PenaltyEvent):
        print(f"\n PENALTY - Current: {play.penalty_type}")
        modifications.extend([
            ("remove_penalty", "Remove penalty"),
            ("change_penalty_yards", "Change penalty yardage")
        ])
    
    # Display options
    print(f"\n{'CORE MODIFICATION OPTIONS':^80}")
    for i, (code, description) in enumerate(modifications, 1):
        print(f"{i:2d}. {description}")
    
    
    while True:
        try:
            choice = int(input(f"Choose modification (1-{len(modifications)}): "))
            if 1 <= choice <= len(modifications):
                selected_mod = modifications[choice - 1]
                print(f"\n Selected: {selected_mod[1]}")
                return selected_mod[0], selected_mod[1]
            else:
                print(f"Please enter a number between 1 and {len(modifications)}.")
        except ValueError:
            print("Please enter a valid number.")

def apply_core_modification(modification_code, play, game_stats):
    """Apply ONLY core NFL game factor modifications based on team statistics."""
    print(f"\nApplying: {modification_code}")
    
    # Get team statistics for realistic modifications
    team_stats = game_stats[play.posteam]
    
    # Create a copy of the original play
    if isinstance(play, PassEvent):
        new_play = PassEvent(
            play.desc, play.qtr, play.half_seconds_remaining, play.game_seconds_remaining,
            play.down, play.to_go, play.yardline_100, play.yards_gained, 
            play.score_differential, play.posteam, play.points,
            is_complete=play.is_complete, is_fumble=play.is_fumble
        )
    elif isinstance(play, RushEvent):
        new_play = RushEvent(
            play.desc, play.qtr, play.half_seconds_remaining, play.game_seconds_remaining,
            play.down, play.to_go, play.yardline_100, play.yards_gained, 
            play.score_differential, play.posteam, play.points,
            is_fumble=play.is_fumble
        )
    elif isinstance(play, InterceptionEvent):
        new_play = InterceptionEvent(
            play.desc, play.qtr, play.half_seconds_remaining, play.game_seconds_remaining,
            play.down, play.to_go, play.yardline_100, play.yards_gained, 
            play.score_differential, play.posteam, play.points,
            is_interception=True, is_fumble=getattr(play, 'is_fumble', False)
        )
    elif isinstance(play, FieldGoalEvent):
        new_play = FieldGoalEvent(
            play.desc, play.qtr, play.half_seconds_remaining, play.game_seconds_remaining,
            play.down, play.to_go, play.yardline_100, play.yards_gained, 
            play.score_differential, play.posteam, play.points,
            is_good=play.is_good
        )
    elif isinstance(play, XPEvent):
        new_play = XPEvent(
            play.desc, play.qtr, play.half_seconds_remaining, play.game_seconds_remaining,
            play.down, play.to_go, play.yardline_100, play.yards_gained, 
            play.score_differential, play.posteam, play.points,
            is_good=play.is_good
        )
    elif isinstance(play, PenaltyEvent):
        new_play = PenaltyEvent(
            play.desc, play.qtr, play.half_seconds_remaining, play.game_seconds_remaining,
            play.down, play.to_go, play.yardline_100, play.yards_gained, 
            play.score_differential, play.posteam, play.points,
            penalty_type=play.penalty_type, penalty_yards=play.penalty_yards
        )
    else:
        new_play = play
    
    # CORE MODIFICATIONS BASED ON NFL GAME FACTORS
    
    # PASS MODIFICATIONS
    if modification_code == "make_complete":
        avg_yards = int(team_stats['avg_yards_per_pass'])
        new_play = PassEvent(
            play.desc, play.qtr, play.half_seconds_remaining, play.game_seconds_remaining,
            play.down, play.to_go, play.yardline_100, avg_yards, 
            play.score_differential, play.posteam, play.points,
            is_complete=True, is_fumble=False
        )
        print(f"Made pass COMPLETE for {avg_yards} yards (team average)")
    
    elif modification_code == "make_incomplete":
        new_play = PassEvent(
            play.desc, play.qtr, play.half_seconds_remaining, play.game_seconds_remaining,
            play.down, play.to_go, play.yardline_100, 0, 
            play.score_differential, play.posteam, play.points,
            is_complete=False, is_fumble=False
        )
        print(" Made pass INCOMPLETE")
    
    elif modification_code == "turn_to_interception":
        return_yards = random.randint(0, 25)  # Typical INT return
        new_play = InterceptionEvent(
            play.desc, play.qtr, play.half_seconds_remaining, play.game_seconds_remaining,
            play.down, play.to_go, play.yardline_100, return_yards, 
            play.score_differential, play.posteam, 0,  # No points for interception
            is_interception=True, is_fumble=False
        )
        print(f" Turned into INTERCEPTION with {return_yards} yard return")
    
    # FUMBLE MODIFICATIONS  
    elif modification_code == "add_fumble":
        if isinstance(new_play, PassEvent):
            new_play.is_fumble = True
            new_play.yards_gained = min(new_play.yards_gained, 3)  # Limited gain before fumble
            new_play.points = 0  # Remove any points from touchdown
        elif isinstance(new_play, RushEvent):
            new_play.is_fumble = True
            new_play.yards_gained = min(new_play.yards_gained, 3)  # Limited gain before fumble
            new_play.points = 0  # Remove any points from touchdown
        elif isinstance(new_play, InterceptionEvent):
            new_play.is_fumble = True  # Fumbled on the return
            new_play.yards_gained = min(new_play.yards_gained, 3)  # Limited return before fumble  
            new_play.points = 0  # Remove any points from touchdown
        print(f" Added FUMBLE (limited to {new_play.yards_gained} yards, removed {(play.points or 0)} points)")
    
    elif modification_code == "remove_fumble":
        if isinstance(new_play, RushEvent):
            new_play.is_fumble = False
            if new_play.yards_gained <= 0:
                new_play.yards_gained = int(team_stats['avg_yards_per_carry'])
        print(" Removed fumble")
    
    # THIRD DOWN CONVERSION
    elif modification_code == "convert_third_down":
        if play.down == 3:
            yards_needed = play.to_go
            new_play.yards_gained = yards_needed + random.randint(1, 5)
            print(f" Converted 3rd down (+{new_play.yards_gained} yards)")
        else:
            print(" Not a 3rd down play")
    
    # FOURTH DOWN MODIFICATIONS
    elif modification_code == "convert_fourth_down":
        if play.down == 4:
            yards_needed = play.to_go  
            new_play.yards_gained = yards_needed + random.randint(0, 3)
            print(f" Converted 4th down (+{new_play.yards_gained} yards)")
        else:
            print(" Not a 4th down play")
    
    elif modification_code == "go_for_it":
        if play.down == 4:
            # Base on team's 4th down conversion rate
            success_rate = team_stats.get('fourth_down_conversions', 0) / max(1, team_stats.get('fourth_down_attempts', 1))
            if random.random() < success_rate:
                new_play.yards_gained = play.to_go + random.randint(0, 3)
                print(f" GO FOR IT - SUCCESSFUL (+{new_play.yards_gained} yards)")
            else:
                new_play.yards_gained = random.randint(-2, play.to_go - 1)
                print(f" GO FOR IT - FAILED ({new_play.yards_gained} yards)")
    
    elif modification_code == "punt_instead":
        # Convert to punt (simplified)
        new_play.yards_gained = 0
        print(" Changed to PUNT")
    
    # FIELD GOAL MODIFICATIONS
    elif modification_code == "make_good" and isinstance(new_play, FieldGoalEvent):
        new_play.is_good = True
        new_play.points = 3
        print(" Field goal GOOD!")
    
    elif modification_code == "make_miss" and isinstance(new_play, FieldGoalEvent):
        new_play.is_good = False
        new_play.points = 0
        print(" Field goal MISSED")
    
    # EXTRA POINT MODIFICATIONS
    elif modification_code == "make_good" and isinstance(new_play, XPEvent):
        new_play.is_good = True
        new_play.points = 1
        print(" Extra point GOOD!")
    
    elif modification_code == "make_miss" and isinstance(new_play, XPEvent):
        new_play.is_good = False
        new_play.points = 0
        print(" Extra point MISSED")
    
    elif modification_code == "convert_to_2pt":
        # 2-point conversion success rate ~47% in NFL
        success = random.random() < 0.47
        new_play.points = 2 if success else 0
        new_play.yards_gained = 2 if success else 0
        print(f" 2-point conversion: {'SUCCESSFUL' if success else 'FAILED'}")
    
    # PENALTY MODIFICATIONS
    elif modification_code == "add_penalty":
        penalty_yards = random.choice([-10, -5, 5, 10, 15])  # Common penalty yardages
        new_play.yards_gained += penalty_yards
        penalty_type = "holding" if penalty_yards < 0 else "defensive penalty"
        print(f" Added {penalty_type} ({penalty_yards:+d} yards)")
    
    elif modification_code == "remove_penalty" and isinstance(new_play, PenaltyEvent):
        # Convert penalty to normal play
        new_play = PassEvent(
            play.desc, play.qtr, play.half_seconds_remaining, play.game_seconds_remaining,
            play.down, play.to_go, play.yardline_100, 5, 
            play.score_differential, play.posteam, play.points,
            is_complete=True, is_fumble=False
        )
        print(" Removed penalty")
    
    # TIMEOUT
    elif modification_code == "add_timeout":
        print(" Added timeout")
    
    # INTERCEPTION MODIFICATIONS
    elif modification_code == "change_return_yards" and isinstance(new_play, InterceptionEvent):
        try:
            new_return = int(input(f"Current return: {new_play.yards_gained}. Enter new return yards: "))
            new_play.yards_gained = new_return
            print(f" Changed return to {new_return} yards")
        except ValueError:
            print("❌ Invalid input, keeping original return")
    
    else:
        print(f"⚠️ Modification '{modification_code}' not fully implemented")
    
    return new_play

    if isinstance(play, PassEvent):
        # After the patch, we can be sure it's not an interception
        if play.is_complete:
            return "make_incomplete"
        else:
            return "make_complete"
    elif isinstance(play, InterceptionEvent):
        return "remove_interception" # Add a new modification option
    elif isinstance(play, FieldGoalEvent) or isinstance(play, XPEvent):
        if play.is_good:
            return "make_miss"
        else:
            return "make_good"
    elif isinstance(play, RushEvent) and play.is_fumble:
        return "remove_fumble"
        
    print("This play type doesn't have a simple modification available.")
    return None

# Old function removed - now using apply_comprehensive_modification

class GameSimulator:
    """Full game simulator using Markov chains and Monte Carlo methods."""
    
    def __init__(self, game):
        self.game = game
        self.home_stats = game.stats[game.home]
        self.away_stats = game.stats[game.away]
    
    def get_team_stats(self, team):
        """Get stats for a specific team."""
        return self.home_stats if team == self.game.home else self.away_stats
    
    def simulate_play_outcome(self, down, distance, yard_line, team, play_type=None):
        """Simulate a single play outcome based on team stats and game situation."""
        stats = self.get_team_stats(team)
        
        # Determine play type if not specified
        if not play_type:
            play_type = self.decide_play_type(down, distance, yard_line, stats)
        
        if play_type == "PASS":
            return self.simulate_pass(stats, distance)
        elif play_type == "RUSH":
            return self.simulate_rush(stats, distance)
        elif play_type == "FIELD_GOAL":
            return self.simulate_field_goal(stats, yard_line)
        elif play_type == "PUNT":
            return self.simulate_punt(yard_line)
        else:
            return {"type": "UNKNOWN", "yards": 0, "turnover": False, "score": 0}
    
    def decide_play_type(self, down, distance, yard_line, stats):
        """Decide what type of play to call based on situation."""
        # Fourth down logic
        if down == 4:
            if yard_line <= 35:  # Field goal range
                return "FIELD_GOAL" if random.random() < 0.7 else "PUNT"
            elif distance <= 2:  # Short yardage, go for it
                return "RUSH" if random.random() < 0.6 else "PUNT"
            else:
                return "PUNT"
        
        # Red zone logic
        if yard_line <= 20:
            pass_prob = 0.65
        # Normal field position
        elif distance > 7:
            pass_prob = 0.7  # More likely to pass on long distance
        else:
            pass_prob = 0.55
        
        return "PASS" if random.random() < pass_prob else "RUSH"
    
    def simulate_pass(self, stats, distance):
        """Simulate a pass play."""
        completion_prob = stats.get('completion_prob', 0.6)
        interception_prob = stats.get('interception_prob', 0.02)
        avg_yards = stats.get('avg_yards_per_pass', 7.0)
        
        rand = random.random()
        
        if rand < interception_prob:
            return {"type": "INTERCEPTION", "yards": 0, "turnover": True, "score": 0}
        elif rand < completion_prob:
            yards = max(0, int(random.normalvariate(avg_yards, 5)))
            return {"type": "PASS_COMPLETE", "yards": yards, "turnover": False, "score": 0}
        else:
            return {"type": "PASS_INCOMPLETE", "yards": 0, "turnover": False, "score": 0}
    
    def simulate_rush(self, stats, distance):
        """Simulate a rush play."""
        fumble_prob = stats.get('fumble_prob', 0.015)
        avg_yards = stats.get('avg_yards_per_carry', 4.0)
        
        if random.random() < fumble_prob:
            return {"type": "FUMBLE", "yards": 0, "turnover": True, "score": 0}
        
        yards = max(-3, int(random.normalvariate(avg_yards, 3)))
        return {"type": "RUSH", "yards": yards, "turnover": False, "score": 0}
    
    def simulate_field_goal(self, stats, yard_line):
        """Simulate a field goal attempt."""
        base_prob = stats.get('field_goal_prob', 0.85)
        
        # Adjust probability based on distance
        distance = yard_line + 17  # Add end zone and holder position
        if distance <= 30:
            prob = min(0.95, base_prob + 0.1)
        elif distance <= 40:
            prob = base_prob
        elif distance <= 50:
            prob = max(0.3, base_prob - 0.2)
        else:
            prob = max(0.1, base_prob - 0.4)
        
        if random.random() < prob:
            return {"type": "FIELD_GOAL_GOOD", "yards": 0, "turnover": False, "score": 3}
        else:
            return {"type": "FIELD_GOAL_MISS", "yards": 0, "turnover": True, "score": 0}
    
    def simulate_punt(self, yard_line):
        """Simulate a punt."""
        # Simple punt model - opponent gets ball around their 20-30 yard line
        return {"type": "PUNT", "yards": 0, "turnover": True, "score": 0}
    
    def simulate_drive(self, start_yard_line, start_down, start_distance, team):
        """Simulate an entire drive."""
        yard_line = start_yard_line
        down = start_down
        distance = start_distance
        drive_plays = []
        total_score = 0
        
        while True:
            # Simulate the play
            result = self.simulate_play_outcome(down, distance, yard_line, team)
            drive_plays.append(result)
            
            # Handle scoring
            if result["score"] > 0:
                total_score += result["score"]
                break
            
            # Handle turnovers
            if result["turnover"]:
                break
            
            # Update field position
            yard_line = max(1, yard_line - result["yards"])
            
            # Check for touchdown
            if yard_line <= 0:
                total_score += 7  # TD + XP
                break
            
            # Update down and distance
            if result["yards"] >= distance:  # First down
                down = 1
                distance = 10
            else:
                down += 1
                distance -= result["yards"]
                
                # Turnover on downs
                if down > 4:
                    break
        
        return total_score, drive_plays
    
    def simulate_game_from_point(self, current_play_index, modified_play, num_simulations=100):
        """
        VISUAL simulation that shows exactly what happens play by play from modification point.
        """
        results = []
        original_play = self.game.plays[current_play_index]
        time_remaining = original_play.game_seconds_remaining
        
        # STEP 1: Calculate scores BEFORE the modification point (not including the play we're changing)
        home_score_before_mod = 0
        away_score_before_mod = 0
        
        print(f"\n🐛 DEBUG: Checking scoring plays up to index {current_play_index}:")
        for i in range(current_play_index):  # Don't include the play we're modifying
            play = self.game.plays[i]
            if play.points and play.points > 0:
                print(f"   Play {i}: {play.posteam} scored {play.points} points - {play.desc[:60]}...")
                if play.posteam == self.game.home:
                    home_score_before_mod += play.points
                else:
                    away_score_before_mod += play.points
        
        print(f"🐛 Total scoring plays found: {sum(1 for i in range(current_play_index) if self.game.plays[i].points and self.game.plays[i].points > 0)}")
        
        # Cross-check with actual game score at this time
        current_time = original_play.game_seconds_remaining
        print(f"🐛 Play {current_play_index} is at {int(current_time//60)}:{int(current_time%60):02d} in Q{original_play.qtr}")
        print(f"🐛 Based on loaded plays: {self.game.home} {home_score_before_mod} - {self.game.away} {away_score_before_mod}")
        print(f"🐛 Game final was: {self.game.home} {self.game.home_score} - {self.game.away} {self.game.away_score}")
        
        # STEP 2: Show what the score was AFTER the original play
        home_score_after_original = home_score_before_mod
        away_score_after_original = away_score_before_mod
        
        original_play = self.game.plays[current_play_index]
        if original_play.points and original_play.points > 0:
            if original_play.posteam == self.game.home:
                home_score_after_original += original_play.points
            else:
                away_score_after_original += original_play.points
        
        # STEP 3: Calculate what happens with the MODIFIED play instead
        home_score_after_modified = home_score_before_mod
        away_score_after_modified = away_score_before_mod
        
        if modified_play.points and modified_play.points > 0:
            if modified_play.posteam == self.game.home:
                home_score_after_modified += modified_play.points
            else:
                away_score_after_modified += modified_play.points
        
        print(f"\n🔍 SCORE DEBUGGING:")
        print(f"   Home team: {self.game.home}, Away team: {self.game.away}")
        print(f"   Modified play team: {modified_play.posteam}")
        print(f"   Original play points: {original_play.points}")
        print(f"   Modified play points: {modified_play.points}")
        print(f"   Score before ANY play: {self.game.home} {home_score_before_mod} - {self.game.away} {away_score_before_mod}")
        print(f"   Score after ORIGINAL: {self.game.home} {home_score_after_original} - {self.game.away} {away_score_after_original}")
        print(f"   Score after MODIFIED: {self.game.home} {home_score_after_modified} - {self.game.away} {away_score_after_modified}")
        
        print(f"\n🏈 SIMULATION STARTING POINT:")
        print(f"Original game final: {self.game.home} {self.game.home_score} - {self.game.away} {self.game.away_score}")
        print(f"Score after modification: {self.game.home} {home_score_after_modified} - {self.game.away} {away_score_after_modified}")
        print(f"Time remaining: {int(time_remaining//60)}:{int(time_remaining%60):02d}")
        
        # The impact is the difference
        immediate_home_change = home_score_after_modified - home_score_after_original
        immediate_away_change = away_score_after_modified - away_score_after_original
        
        print(f"\n⚡ MODIFICATION IMPACT:")
        if immediate_home_change != 0:
            print(f"  {self.game.home}: {immediate_home_change:+.1f} points")
        if immediate_away_change != 0:
            print(f"  {self.game.away}: {immediate_away_change:+.1f} points")
        if immediate_home_change == 0 and immediate_away_change == 0:
            print("  No immediate scoring impact")
        
        # Run all simulations silently first
        print(f"\n🔄 Running {num_simulations} simulations...")
        for _ in range(num_simulations):
            sim_result = self.simulate_detailed_game(
                home_score_after_modified, away_score_after_modified, 
                time_remaining, 0, 0,  # Impact already applied to the starting scores
                verbose=False
            )
            results.append(sim_result)
        
        # After getting results, show what an average simulation would look like
        analysis = self.analyze_results(results)
        print(f"\n🎮 SHOWING WHAT AN AVERAGE SIMULATION LOOKS LIKE:")
        print(f"\n--- REPRESENTATIVE GAME SIMULATION ---")
        
        # Run one detailed simulation that represents the average
        average_sim = self.simulate_detailed_game(
            home_score_after_modified, away_score_after_modified, 
            time_remaining, 0, 0,  # Impact already applied to the starting scores
            verbose=True, debug=True, target_home_score=analysis['avg_home_score'], 
            target_away_score=analysis['avg_away_score']
        )
        
        return analysis
    
    def simulate_detailed_game(self, start_home_score, start_away_score, time_remaining, 
                              home_impact, away_impact, verbose=True, debug=False, 
                              target_home_score=None, target_away_score=None):
        """
        Simulate the remainder of the game with detailed play-by-play output.
        """
        # Apply immediate modification impact (but don't go below 0)
        home_score = max(0, start_home_score + home_impact)
        away_score = max(0, start_away_score + away_impact)
        
        if verbose:
            print(f"Simulating from: {self.game.home} {home_score:.0f} - {self.game.away} {away_score:.0f}")
        
        # Determine who has possession based on the original play
        current_possession = self.game.home  # Start with home team (will be more sophisticated later)
        
        # Simulate remaining time in chunks (drives) - more realistic number
        drives_simulated = 0
        max_drives = min(8, max(1, int(time_remaining / 300)))  # About 5 minutes per drive, max 8 drives
        
        while time_remaining > 0 and drives_simulated < max_drives:
            drives_simulated += 1
            
            if verbose:
                mins = int(time_remaining // 60)
                secs = int(time_remaining % 60)
                print(f"  📍 Drive {drives_simulated}: {current_possession} has ball, {mins}:{secs:02d} left")
            
            # Simulate this drive
            drive_result = self.simulate_drive(current_possession, time_remaining, verbose)
            
            # Apply drive results
            if drive_result['points'] > 0:
                if current_possession == self.game.home:
                    home_score += drive_result['points']
                    if verbose:
                        if drive_result['points'] == 7:
                            print(f"    🏈 {self.game.home} TD → {home_score:.0f}")
                        elif drive_result['points'] == 3:
                            print(f"    🥅 {self.game.home} FG → {home_score:.0f}")
                        else:
                            print(f"    ⚡ {self.game.home} +{drive_result['points']} → {home_score:.0f}")
                else:
                    away_score += drive_result['points']
                    if verbose:
                        if drive_result['points'] == 7:
                            print(f"    🏈 {self.game.away} TD → {away_score:.0f}")
                        elif drive_result['points'] == 3:
                            print(f"    🥅 {self.game.away} FG → {away_score:.0f}")
                        else:
                            print(f"    ⚡ {self.game.away} +{drive_result['points']} → {away_score:.0f}")
            else:
                if verbose:
                    print(f"    ❌ {current_possession} no points")
            
            # Update time and possession
            time_remaining -= drive_result['time_used']
            current_possession = self.game.away if current_possession == self.game.home else self.game.home
        
        if verbose:
            print(f"  🏁 FINAL: {self.game.home} {home_score:.0f} - {self.game.away} {away_score:.0f}")
        
        return {
            "home_score": max(0, round(home_score)), 
            "away_score": max(0, round(away_score))
        }
    
    def simulate_drive(self, team, time_remaining, verbose=True):
        """
        SIMPLIFIED drive simulation - just use basic team stats.
        """
        team_stats = self.game.stats[team]
        
        # Simple drive time: 3-7 minutes
        drive_time = random.uniform(180, 420)
        
        # Simple scoring probability from team stats
        scoring_prob = team_stats.get('scoring_drive_prob', 0.35)
        
        # Simple scoring decision
        if random.random() < scoring_prob:
            # 60% chance TD, 40% chance FG
            if random.random() < 0.6:
                points = 7  # TD + XP
            else:
                points = 3  # FG
        else:
            points = 0  # No score
        
        return {
            'points': points,
            'time_used': min(drive_time, time_remaining)
        }
    
    def calculate_modification_impact(self, original_play, modified_play):
        """
        Calculate realistic impact of play modification.
        Returns impact as {'home_delta': X, 'away_delta': Y}
        """
        impact = {'home_delta': 0.0, 'away_delta': 0.0}
        
        # 1. DIRECT SCORING CHANGES (immediate points difference)
        original_points = original_play.points or 0
        modified_points = modified_play.points or 0
        direct_points_change = modified_points - original_points
        
        if direct_points_change != 0:
            if original_play.posteam == self.game.home:
                impact['home_delta'] += direct_points_change
            else:
                impact['away_delta'] += direct_points_change
        
        # 2. TURNOVER IMPACT (possession change = expected points swing)
        original_is_turnover = self.is_turnover(original_play)
        modified_is_turnover = self.is_turnover(modified_play)
        
        # SPECIAL CASE: Adding fumble to an interception return = double turnover = ball goes back
        # This effectively cancels out the original turnover
        double_turnover = (isinstance(original_play, InterceptionEvent) and 
                          isinstance(modified_play, InterceptionEvent) and
                          hasattr(modified_play, 'is_fumble') and modified_play.is_fumble)
        
        if double_turnover:
            # Double turnover: ball goes back to original offense
            # This is like removing the original turnover + getting better field position
            field_pos_value = (100 - original_play.yardline_100) / 100.0
            base_turnover_value = 3.0 + (field_pos_value * 4.0)
            
            if original_play.posteam == self.game.home:
                impact['home_delta'] += base_turnover_value * 1.2  # Better than just avoiding turnover
                impact['away_delta'] -= base_turnover_value * 0.6
            else:
                impact['away_delta'] += base_turnover_value * 1.2
                impact['home_delta'] -= base_turnover_value * 0.6
                
        elif original_is_turnover != modified_is_turnover:
            # Field position matters for turnover value
            field_pos_value = (100 - original_play.yardline_100) / 100.0  # 0.0 to 1.0
            base_turnover_value = 3.0 + (field_pos_value * 4.0)  # 3-7 points based on field position
            
            if not original_is_turnover and modified_is_turnover:
                # Added a turnover - offense loses possession
                if original_play.posteam == self.game.home:
                    impact['home_delta'] -= base_turnover_value
                    impact['away_delta'] += base_turnover_value * 0.6  # Defense gets some benefit
                else:
                    impact['away_delta'] -= base_turnover_value
                    impact['home_delta'] += base_turnover_value * 0.6
            
            elif original_is_turnover and not modified_is_turnover:
                # Removed a turnover - offense keeps possession
                if original_play.posteam == self.game.home:
                    impact['home_delta'] += base_turnover_value
                    impact['away_delta'] -= base_turnover_value * 0.6
                else:
                    impact['away_delta'] += base_turnover_value
                    impact['home_delta'] -= base_turnover_value * 0.6
        
        # 3. FIELD POSITION CHANGES (yardage difference)
        yards_diff = modified_play.yards_gained - original_play.yards_gained
        if abs(yards_diff) > 0:
            # Each yard is worth about 0.05-0.07 expected points
            yard_value = yards_diff * 0.06
            
            if original_play.posteam == self.game.home:
                impact['home_delta'] += yard_value
            else:
                impact['away_delta'] += yard_value
        
        # 4. DOWN AND DISTANCE IMPACT (affects drive continuation probability)
        # This is more complex but for now we'll keep it simple
        
        return impact
    
    def is_turnover(self, play):
        """Check if a play is a turnover (interception or fumble lost)."""
        if isinstance(play, InterceptionEvent):
            return True
        if hasattr(play, 'is_fumble') and play.is_fumble:
            return True
        return False
    
    def simulate_simple_remaining_time(self, time_remaining):
        """Simple remaining time simulation based on final scores."""
        if time_remaining <= 0:
            return {'home': 0, 'away': 0}
        
        # Use actual final scores to calibrate
        time_fraction = time_remaining / 3600.0
        
        # Estimate how many points were scored in remaining time of actual game
        # This is a rough approximation
        home_remaining = max(0, random.gauss(self.game.home_score * time_fraction * 0.8, 3))
        away_remaining = max(0, random.gauss(self.game.away_score * time_fraction * 0.8, 3))
        
        return {'home': home_remaining, 'away': away_remaining}
    

    

        
    def get_field_position_value(self, yard_line):
        """Get scoring value based on field position (0-7 points)."""
        # Red zone is most valuable
        if yard_line <= 20:
            return 6 + (20 - yard_line) * 0.05  # 6-7 points
        elif yard_line <= 40:
            return 4 + (40 - yard_line) * 0.1   # 4-6 points  
        else:
            return max(1, 4 - (yard_line - 40) * 0.05)  # 1-4 points
        
    def simulate_remaining_game_time(self, time_remaining, home_possessing):
        """Simulate remaining game time more realistically."""
        remaining_scores = {'home': 0, 'away': 0}
        
        # Estimate number of possessions remaining
        avg_possession_time = 180  # 3 minutes per possession
        possessions_left = max(1, int(time_remaining / avg_possession_time))
        
        for _ in range(possessions_left):
            if time_remaining <= 0:
                break
                
            # Determine possessing team
            team = self.game.home if home_possessing else self.game.away
            stats = self.get_team_stats(team)
            
            # Simulate drive outcome
            drive_score = self.simulate_drive_score(stats, time_remaining)
            
            if team == self.game.home:
                remaining_scores['home'] += drive_score
            else:
                remaining_scores['away'] += drive_score
            
            # Switch possession and reduce time
            home_possessing = not home_possessing
            time_remaining -= avg_possession_time
        
        return remaining_scores
    
    def simulate_drive_score(self, team_stats, time_remaining):
        """Simulate expected points from a drive."""
        scoring_prob = team_stats.get('scoring_drive_prob', 0.35)
        
        # Time pressure affects scoring
        if time_remaining < 120:  # Less than 2 minutes
            scoring_prob *= 1.2  # More aggressive
        elif time_remaining > 1800:  # More than 30 minutes
            scoring_prob *= 0.9   # More conservative
        
        if random.random() < scoring_prob:
            # Decide type of score
            td_prob = team_stats.get('red_zone_td_prob', 0.6)
            if random.random() < td_prob:
                return 7  # Touchdown + XP
            else:
                return 3  # Field goal
        
        return 0  # No score
    
    def get_field_position_value(self, yardline_100):
        """Convert field position to expected points value."""
        # Closer to goal line = higher value
        if yardline_100 <= 10:
            return 6  # Very high scoring probability
        elif yardline_100 <= 20:
            return 4  # Red zone
        elif yardline_100 <= 40:
            return 2  # Good field position
        else:
            return 1  # Normal field position
    
    def apply_modification(self, play_index, modified_play):
        """Apply the modification and return new game state - SIMPLIFIED."""
        original_play = self.game.plays[play_index]
        
        return {
            "time_remaining": original_play.game_seconds_remaining,
            "yard_line": original_play.yardline_100,
            "down": original_play.down,
            "distance": original_play.to_go,
            "possession": original_play.posteam,
            "modified_play": modified_play
        }
    
    def analyze_results(self, results):
        """Analyze simulation results."""
        home_wins = sum(1 for r in results if r["home_score"] > r["away_score"])
        away_wins = sum(1 for r in results if r["away_score"] > r["home_score"])
        ties = len(results) - home_wins - away_wins
        
        avg_home_score = np.mean([r["home_score"] for r in results])
        avg_away_score = np.mean([r["away_score"] for r in results])
        
        return {
            "home_win_prob": home_wins / len(results),
            "away_win_prob": away_wins / len(results),
            "tie_prob": ties / len(results),
            "avg_home_score": avg_home_score,
            "avg_away_score": avg_away_score,
            "total_simulations": len(results)
        }

def get_user_modification(play):
    """Enhanced modification options for all play types."""
    print(f"\nSelected Play: {play.desc.splitlines()[0]}")
    print("\nAvailable modifications:")
    
    options = []
    
    if isinstance(play, PassEvent):
        if play.is_complete:
            options.extend([
                ("make_incomplete", "Make pass incomplete"),
                ("make_interception", "Turn into interception"),
                ("add_fumble_after_catch", "Add fumble after catch"),
                ("change_pass_yards", "Change yards gained"),
            ])
        else:
            options.extend([
                ("make_complete", "Make pass complete"),
                ("make_interception", "Turn into interception"),
            ])
    
    elif isinstance(play, InterceptionEvent):
        options.extend([
            ("remove_interception_incomplete", "Make it an incomplete pass"),
            ("remove_interception_complete", "Make it a completed pass"),
            ("change_interception_return", "Change return yards"),
        ])
    
    elif isinstance(play, RushEvent):
        if hasattr(play, 'is_fumble') and play.is_fumble:
            options.extend([
                ("remove_fumble", "Remove fumble"),
                ("change_fumble_recovery", "Change who recovers fumble"),
            ])
        else:
            options.extend([
                ("add_fumble", "Add fumble"),
                ("change_rush_yards", "Change yards gained"),
                ("add_penalty_holding", "Add holding penalty"),
                ("add_penalty_false_start", "Add false start penalty"),
            ])
    
    elif isinstance(play, FieldGoalEvent):
        if play.is_good:
            options.extend([
                ("make_miss", "Make field goal miss"),
                ("add_penalty_roughing", "Add roughing the kicker penalty"),
            ])
        else:
            options.extend([
                ("make_good", "Make field goal good"),
                ("add_penalty_offsides", "Add offsides penalty (retry)"),
            ])
    
    elif isinstance(play, XPEvent):
        if play.is_good:
            options.extend([
                ("make_miss", "Make extra point miss"),
                ("convert_to_2pt", "Convert to 2-point attempt"),
            ])
        else:
            options.extend([
                ("make_good", "Make extra point good"),
                ("convert_to_2pt", "Convert to 2-point attempt"),
            ])
    
    else:
        options.extend([
            ("add_penalty", "Add generic penalty"),
            ("add_timeout", "Add timeout"),
        ])
    
    # Display options
    for i, (code, desc) in enumerate(options, 1):
        print(f"{i}. {desc}")
    
    # Get user choice
    try:
        choice = int(input(f"\nEnter choice (1-{len(options)}): ")) - 1
        if 0 <= choice < len(options):
            return options[choice][0]
        else:
            print("Invalid choice.")
            return None
    except ValueError:
        print("Invalid input.")
        return None

def main():
    
    try:
        year = int(input("Enter the season year (e.g., 2023): "))
        team1_abbr = input("Enter the first team's abbreviation: ").upper()
        team2_abbr = input("Enter the second team's abbreviation: ").upper()
    except ValueError:
        print("Invalid year. Please enter a number.")
        return

    game_id = find_game_id(year, team1_abbr, team2_abbr)
    if not game_id:
        print(f"No game found between {team1_abbr} and {team2_abbr} in {year}.")
        return

    try:
        game = Game(game_id, year)
    except Exception as e:
        print(f"Error loading game data: {e}")
        return
    # DEBUG: verify play-by-play data
    print(f"\n[DEBUG] Total plays loaded: {len(game.plays)}")
    print("[DEBUG] Sample plays:")
    for idx, play in enumerate(game.plays[:20]):  # first 20 plays
        print(f"{idx}: qtr={play.qtr}, time_rem={play.game_seconds_remaining}, down={play.down}-{play.to_go}, "
              f"ydline={play.yardline_100}, yds_gained={play.yards_gained}, score_diff={play.score_differential}, "
              f"posteam={play.posteam}, points={play.points}")
    print("[DEBUG] End sample plays\n")

    # Display ALL plays with filtering options
    displayed_plays = display_all_plays(game)
    if not displayed_plays:
        print("No plays found to modify in this game.")
        return

    # Let user select ANY play from the filtered list
    try:
        play_index_str = input(f"\nEnter the INDEX number of the play you want to change (0-{len(game.plays)-1}): ")
        selected_index = int(play_index_str)
        
        # Validate the index is within range
        if not (0 <= selected_index < len(game.plays)):
            print(f"Invalid play index. Please enter a number between 0 and {len(game.plays)-1}.")
            return
        
        original_play = game.plays[selected_index]

    except (ValueError, IndexError):
        print("Invalid input. Please enter a valid play index number.")
        return

    # Get core modification from user
    modification_code, modification_description = get_core_modification(original_play)
    if not modification_code:
        return

    # Apply the core modification using team statistics
    modified_play = apply_core_modification(modification_code, original_play, game.stats)

    print(f"\n{'='*100}")
    print(f"ORIGINAL PLAY: {original_play.desc.splitlines()[0]}")
    print(f"MODIFICATION: {modification_description}")
    print(f"{'='*100}")
    
    # Initialize simulator
    simulator = GameSimulator(game)
    
    print("\nRunning Monte Carlo simulation...")
    
    # Run simulation with modification
    results = simulator.simulate_game_from_point(selected_index, modified_play, num_simulations=5000)
    
    print("\n--- SIMULATION RESULTS ---")
    print(f"Original Final Score: {game.away} {game.away_score} - {game.home} {game.home_score}")
    print(f"\nWith your modification:")
    print(f"Average Final Score: {game.away} {results['avg_away_score']:.1f} - {game.home} {results['avg_home_score']:.1f}")
    print(f"{game.home} Win Probability: {results['home_win_prob']:.1%}")
    print(f"{game.away} Win Probability: {results['away_win_prob']:.1%}")
    print(f"Simulations run: {results['total_simulations']}")
    
    # Show impact
    original_home_advantage = 1 if game.home_score > game.away_score else 0
    new_home_advantage = results['home_win_prob']
    
    if original_home_advantage == 1:
        if new_home_advantage > 0.5:
            impact = f"Your change strengthened {game.home}'s victory (Win prob: {new_home_advantage:.1%})"
        else:
            impact = f"Your change could have changed the outcome! {game.away} now favored"
    else:
        if new_home_advantage < 0.5:
            impact = f"Your change strengthened {game.away}'s victory (Win prob: {results['away_win_prob']:.1%})"
        else:
            impact = f"Your change could have changed the outcome! {game.home} now favored"
    
    print(f"\nImpact: {impact}")


if __name__ == "__main__":
    main()
