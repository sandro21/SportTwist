from flask import Flask, request, jsonify
from flask_cors import CORS
import nflreadpy as nfl
import pandas as pd
import numpy as np
import json
import re
from datetime import datetime
import logging
from game import Game, Simulator

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
# class NumpyEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if isinstance(obj, (np.integer, np.int64)):
#             return int(obj)
#         elif isinstance(obj, (np.floating, np.float64)):
#             return float(obj)
#         return super().default(obj)

# app.json_encoder = NumpyEncoder
CORS(app)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global data cache
games_cache = None
schedules_cache = None

def load_nfl_data():
    """Load NFL data using nflreadpy"""
    global games_cache, schedules_cache
    
    try:
        logger.info("Loading NFL data...")
        
        pbp = nfl.load_pbp([2023, 2024, 2025])
        df = pbp.to_pandas()
        
        schedules = nfl.load_schedules([2023, 2024, 2025])
        schedule_df = schedules.to_pandas()
        
        games_cache = df
        schedules_cache = schedule_df
        
        logger.info(f"Loaded {len(df)} plays and {len(schedule_df)} scheduled games")
        return True
        
    except Exception as e:
        logger.error(f"Error loading NFL data: {str(e)}")
        return False

def get_game_scores():
    if schedules_cache is None:
        return []
    
    try:
        games_list = []
        
        for _, game in schedules_cache.iterrows():
            if pd.isna(game['home_score']) or pd.isna(game['away_score']):
                continue
                
            game_info = {
                'game_id': game['game_id'],
                'home_team': game['home_team'],
                'away_team': game['away_team'],
                'home_score': int(game['home_score']) if pd.notna(game['home_score']) else 0,
                'away_score': int(game['away_score']) if pd.notna(game['away_score']) else 0,
                'week': game['week'],
                'season': game['season'],
                'gameday': game['gameday'],
                'gametime': game['gametime']
            }
            games_list.append(game_info)
            
        games_list.sort(key=lambda x: (x['season'], x['week']), reverse=True)
        return games_list
        
    except Exception as e:
        logger.error(f"Error getting game scores: {str(e)}")
        return []

@app.route('/api/games', methods=['GET'])
def get_games():
    try:
        if games_cache is None or schedules_cache is None:
            if not load_nfl_data():
                return jsonify({"error": "Failed to load NFL data"}), 500
        
        games = get_game_scores()
        return jsonify({"games": games[:50]})  # Return latest 50 games
        
    except Exception as e:
        logger.error(f"Error in /api/games: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/search', methods=['GET'])
def search_games():
    try:
        query = request.args.get('q', '').strip().lower()
        
        if not query:
            return jsonify({"games": []})
        
        if games_cache is None or schedules_cache is None:
            if not load_nfl_data():
                return jsonify({"error": "Failed to load NFL data"}), 500
        
        games = get_game_scores()
        filtered_games = []
        
        filter_type = None
        filter_value = None
        
        if query.startswith('player:'):
            filter_type = 'player'
            filter_value = query.replace('player:', '').strip()
        elif query.startswith('type:'):
            filter_type = 'gameType'
            filter_value = query.replace('type:', '').strip()
        elif query.startswith('season:'):
            filter_type = 'season'
            filter_value = query.replace('season:', '').strip()
        elif query == 'latest':
            filter_type = 'latest'
        
        # Team name mappings for better search
        team_name_map = {
            'eagles': 'PHI', 'philadelphia': 'PHI',
            'cowboys': 'DAL', 'dallas': 'DAL',
            'chiefs': 'KC', 'kansas': 'KC',
            'bills': 'BUF', 'buffalo': 'BUF',
            'packers': 'GB', 'green bay': 'GB',
            'vikings': 'MIN', 'minnesota': 'MIN',
            'patriots': 'NE', 'new england': 'NE',
            'dolphins': 'MIA', 'miami': 'MIA',
            'steelers': 'PIT', 'pittsburgh': 'PIT',
            'ravens': 'BAL', 'baltimore': 'BAL',
            '49ers': 'SF', 'niners': 'SF', 'san francisco': 'SF',
            'seahawks': 'SEA', 'seattle': 'SEA',
            'rams': 'LA', 'los angeles rams': 'LA',
            'chargers': 'LAC', 'los angeles chargers': 'LAC',
            'giants': 'NYG', 'new york giants': 'NYG',
            'jets': 'NYJ', 'new york jets': 'NYJ',
            'saints': 'NO', 'new orleans': 'NO',
            'falcons': 'ATL', 'atlanta': 'ATL',
            'panthers': 'CAR', 'carolina': 'CAR',
            'buccaneers': 'TB', 'bucs': 'TB', 'tampa bay': 'TB',
            'commanders': 'WAS', 'washington': 'WAS',
            'bears': 'CHI', 'chicago': 'CHI',
            'lions': 'DET', 'detroit': 'DET',
            'titans': 'TEN', 'tennessee': 'TEN',
            'jaguars': 'JAX', 'jacksonville': 'JAX',
            'colts': 'IND', 'indianapolis': 'IND',
            'texans': 'HOU', 'houston': 'HOU',
            'browns': 'CLE', 'cleveland': 'CLE',
            'bengals': 'CIN', 'cincinnati': 'CIN',
            'broncos': 'DEN', 'denver': 'DEN',
            'raiders': 'LV', 'las vegas': 'LV',
            'cardinals': 'ARI', 'arizona': 'ARI'
        }

        # Player name mappings for filtering
        player_team_map = {
            'mahomes': ['KC'], 'allen': ['BUF'], 'rodgers': ['NYJ'], 'jackson': ['BAL'],
            'prescott': ['DAL'], 'herbert': ['LAC'], 'burrow': ['CIN'], 'tua': ['MIA'],
            'lamar': ['BAL'], 'josh allen': ['BUF'], 'patrick mahomes': ['KC'],
            'dak': ['DAL'], 'aaron rodgers': ['NYJ'], 'joe burrow': ['CIN']
        }

        if filter_type == 'latest':
            # Return the most recent game
            filtered_games = games[:1]
        elif filter_type == 'player':
            # Filter by player - find games involving their team
            player_teams = player_team_map.get(filter_value, [])
            for game in games:
                if any(team in [game['home_team'], game['away_team']] for team in player_teams):
                    filtered_games.append(game)
        elif filter_type == 'gameType':
            # Filter by game type (regular season, playoffs, etc.)
            for game in games:
                if filter_value.lower() in ['regular', 'regular season'] and game['week'] <= 18:
                    filtered_games.append(game)
                elif filter_value.lower() in ['playoff', 'playoffs', 'wild card', 'divisional', 'conference'] and game['week'] > 18:
                    filtered_games.append(game)
        elif filter_type == 'season':
            # Filter by season
            season_year = re.search(r'(\d{4})', filter_value)
            if season_year:
                target_season = int(season_year.group(1))
                for game in games:
                    if game['season'] == target_season:
                        filtered_games.append(game)
        else:
            # Regular search
            for game in games:
                # Search by team names, week, or season
                search_text = f"{game['home_team']} {game['away_team']} week {game['week']} {game['season']}".lower()
                
                # Also check for team abbreviations in different formats
                team_variations = [
                    f"{game['home_team']} vs {game['away_team']}",
                    f"{game['away_team']} vs {game['home_team']}",
                    f"{game['home_team']} {game['away_team']}",
                    f"{game['away_team']} {game['home_team']}"
                ]
                
                # Check team name mappings
                team_name_match = False
                for name, abbrev in team_name_map.items():
                    if query in name and (game['home_team'] == abbrev or game['away_team'] == abbrev):
                        team_name_match = True
                        break
                
                # Check if query matches
                if (query in search_text or 
                    any(query in variation.lower() for variation in team_variations) or
                    team_name_match or
                    query in game['gameday'].lower() if game['gameday'] else False):
                    filtered_games.append(game)

        return jsonify({"games": filtered_games[:20]})  # Return top 20 matches
        
    except Exception as e:
        logger.error(f"Error in /api/search: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/popular', methods=['GET'])
def get_popular_games():
    """Get popular/featured games"""
    try:
        if games_cache is None or schedules_cache is None:
            if not load_nfl_data():
                return jsonify({"error": "Failed to load NFL data"}), 500
        
        games = get_game_scores()
        
        # Filter for high-profile matchups and recent games
        popular_games = []
        high_profile_teams = ['KC', 'BUF', 'PHI', 'DAL', 'SF', 'GB', 'MIN', 'BAL', 'PIT']
        
        for game in games:
            if (game['home_team'] in high_profile_teams or 
                game['away_team'] in high_profile_teams):
                popular_games.append(game)
                
        return jsonify({"games": popular_games[:6]})  # Return top 6 popular games
        
    except Exception as e:
        logger.error(f"Error in /api/popular: {str(e)}")
        return jsonify({"error": str(e)}), 500


def safe_convert(value):
    """Convert pandas/numpy values to JSON-safe values"""
    if pd.isna(value) or (isinstance(value, float) and np.isnan(value)):
        return None
    if isinstance(value, (np.integer, np.int64)):
        return int(value)
    if isinstance(value, (np.floating, np.float64)):
        return float(value)
    return value

def clean_description(desc):
    """Remove time stamps and clean up play descriptions"""
    if not desc:
        return desc
    
    # Remove time stamps like (14:50), (:04), (0:12), etc.
    import re
    cleaned = re.sub(r'\(\d*:\d+\)\s*', '', desc)
    
    # Remove extra spaces
    cleaned = ' '.join(cleaned.split())
    
    return cleaned

@app.route('/api/game/<game_id>', methods=['GET'])
def load_game_pbp(game_id):
    try:
        game = Game(game_id, int(game_id[:4]))
        plays = game.plays
        data = {}
        data['game_id'] = game_id
        data['plays'] = {}
        
        logger.info(f"Loaded game {game_id}: {game.away} vs {game.home}, final score {game.away_score}-{game.home_score}")
        
        for i, play in enumerate(plays):
            # Determine play type from the play object
            play_type = 'UNKNOWN'
            if hasattr(play, '__class__'):
                class_name = play.__class__.__name__
                if class_name == 'PassEvent':
                    play_type = 'PASS'
                elif class_name == 'InterceptionEvent':
                    play_type = 'INTERCEPTION'
                elif class_name == 'RushEvent':
                    play_type = 'RUSH'
                elif class_name == 'FieldGoalEvent':
                    play_type = 'FIELD_GOAL'
                elif class_name == 'XPEvent':
                    play_type = 'XP_KICK'
                elif class_name == 'PAT2Event':
                    play_type = 'PAT2'
                elif class_name == 'PuntEvent':
                    play_type = 'PUNT'
                elif class_name == 'PenaltyEvent':
                    play_type = 'PENALTY'
            
            data['plays'][int(i)] = {
                'desc': clean_description(safe_convert(play.desc)),
                'home_score': safe_convert(play.home_score),
                'away_score': safe_convert(play.away_score),
                'qtr': safe_convert(play.qtr),
                'quarter_seconds_remaining': safe_convert(play.quarter_seconds_remaining),
                'half_seconds_remaining': safe_convert(play.half_seconds_remaining),
                'game_seconds_remaining': safe_convert(play.game_seconds_remaining),
                'down': safe_convert(play.down),
                'to_go': safe_convert(play.to_go),
                'yrdln': safe_convert(play.yrdln),
                'yardline_100': safe_convert(play.yardline_100),
                'yards_gained': safe_convert(play.yards_gained),
                'score_differential': safe_convert(play.score_differential),
                'posteam': safe_convert(play.posteam),
                'play_type': play_type,
                'changeable_attributes': play.get_changeable_attributes()
            }
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error loading game {game_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/simulate/', methods=['POST'])
def simulate_rest_of_game():
    print("=" * 80)
    print("🚀 SIMULATION REQUEST RECEIVED")
    print("=" * 80)
    
    data = request.get_json()
    print(f"📥 Raw request data: {data}")
    
    try:
        game_id = data['game_id']
        changeable_attributes = data["changeable_attributes"]
        start_play_index = data['start_play_index']
        
        print(f"🎮 Game ID: {game_id}")
        print(f"🔧 Changeable attributes: {changeable_attributes}")
        print(f"📍 Start play index: {start_play_index}")
        
        print("\n🔄 Creating Game object...")
        game = Game(game_id, int(game_id[:4]))
        print(f"✅ Game created: {game.away} vs {game.home}")
        print(f"📊 Total plays loaded: {len(game.plays)}")
        
        print(f"\n🎯 Getting play at index {start_play_index}...")
        if start_play_index >= len(game.plays):
            print(f"❌ ERROR: Play index {start_play_index} out of range (max: {len(game.plays)-1})")
            return jsonify({"error": f"Play index {start_play_index} out of range"}), 400
            
        target_play = game.plays[start_play_index]
        print(f"✅ Target play: {target_play}")
        print(f"🏷️ Play type: {type(target_play).__name__}")
        print(f"🔧 Play changeable attributes: {target_play.get_changeable_attributes()}")
        
        print(f"\n🎲 Creating Simulator...")
        simulator = Simulator(game)
        print("✅ Simulator created")
        
        print(f"\n🎯 Running simulation from play {start_play_index}...")
        print(f"🔧 With attributes: {changeable_attributes}")
        
        plays = simulator.simulate_from(changeable_attributes, start_play_index, target_play)
        print(f"✅ Simulation completed! Generated {len(plays)} plays")
        
        print(f"\n📊 Running Monte Carlo analysis...")
        avg = simulator.monte_carlo(changeable_attributes, start_play_index, target_play)
        print(f"✅ Monte Carlo completed! Results: {avg}")
        
        print(f"\n📦 Preparing response...")
        response_data = {}
        response_data['game_id'] = game_id
        response_data['plays'] = {}
        response_data['avg_scores'] = avg
        
        if plays:
            last_row = plays[len(plays)-1]
            response_data['final_score'] = {game.home : last_row.home_score, game.away : last_row.away_score}
            print(f"🏆 Final score: {game.home} {last_row.home_score} - {last_row.away_score} {game.away}")
            
            for i, play in enumerate(plays):
                if i < len(plays)-1:
                    response_data['plays'][int(i)] = {
                        'desc': play.desc,
                        'home_score': play.home_score,
                        'away_score': play.away_score,
                        'qtr': play.qtr,
                        'quarter_seconds_remaining': play.quarter_seconds_remaining,
                        'half_seconds_remaining': play.half_seconds_remaining,
                        'game_seconds_remaining': play.game_seconds_remaining,
                        'down': play.down,
                        'to_go': play.to_go,
                        'yrdln': play.yrdln,
                        'yardline_100': play.yardline_100,
                        'yards_gained': play.yards_gained,
                        'score_differential': play.score_differential,
                        'posteam': play.posteam,
                        'changeable_attributes': play.get_changeable_attributes()
                    }
        
        print(f"✅ Response prepared with {len(response_data['plays'])} plays")
        print("=" * 80)
        print("🎉 SIMULATION COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        
        return jsonify(response_data)
        
    except Exception as e:
        print("=" * 80)
        print("❌ SIMULATION FAILED!")
        print("=" * 80)
        print(f"🚨 Error type: {type(e).__name__}")
        print(f"🚨 Error message: {str(e)}")
        print(f"🚨 Full traceback:")
        import traceback
        traceback.print_exc()
        print("=" * 80)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Load data on startup if running directly
    logger.info("Starting NFL API server...")
    load_nfl_data()
    app.run(debug=True, port=5001)  # Different port from your existing app.py