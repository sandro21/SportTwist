from flask import Flask, request, jsonify
from flask_cors import CORS
import nflreadpy as nfl
import pandas as pd
import re
from datetime import datetime
import logging

app = Flask(__name__)
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
        
        # Load play-by-play data for recent seasons (extended range)
        pbp = nfl.load_pbp([2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025])
        df = pbp.to_pandas()
        
        # Load schedule data
        schedules = nfl.load_schedules([2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025])
        schedule_df = schedules.to_pandas()
        
        games_cache = df
        schedules_cache = schedule_df
        
        logger.info(f"Loaded {len(df)} plays and {len(schedule_df)} scheduled games")
        return True
        
    except Exception as e:
        logger.error(f"Error loading NFL data: {str(e)}")
        return False

def get_game_scores():
    """Get final scores for all games"""
    if schedules_cache is None:
        return []
    
    try:
        # Get unique games with scores
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
            
        # Sort by most recent first
        games_list.sort(key=lambda x: (x['season'], x['week']), reverse=True)
        return games_list
        
    except Exception as e:
        logger.error(f"Error getting game scores: {str(e)}")
        return []

@app.route('/api/games', methods=['GET'])
def get_games():
    """Get all games with scores"""
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
    """Search for games by team, week, player, or other criteria"""
    try:
        query = request.args.get('q', '').strip().lower()
        
        if not query:
            return jsonify({"games": []})
        
        if games_cache is None or schedules_cache is None:
            if not load_nfl_data():
                return jsonify({"error": "Failed to load NFL data"}), 500
        
        games = get_game_scores()
        filtered_games = []
        
        # Handle special filter types
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
            # Return the most recent game - ensure it's the very latest
            if games:
                # Sort games by season and week to get the absolute latest
                latest_games = sorted(games, key=lambda x: (x['season'], x['week']), reverse=True)
                filtered_games = latest_games[:1]
            else:
                filtered_games = []
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
            # Filter by season - handle formats like "2025/26" or "2025"
            season_match = re.search(r'(\d{4})', filter_value)
            if season_match:
                target_season = int(season_match.group(1))
                for game in games:
                    if game['season'] == target_season:
                        filtered_games.append(game)
            else:
                # If no year found, try to match the full string
                for game in games:
                    if str(game['season']) in filter_value:
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

        return jsonify({"games": filtered_games[:50]})  # Return top 50 matches (increased from 20)
        
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
        
        # First, get the most recent games (latest season and week)
        if games:
            latest_season = max(games, key=lambda x: x['season'])['season']
            latest_week = max([g for g in games if g['season'] == latest_season], key=lambda x: x['week'])['week']
            
            # Get all games from the latest week of the latest season first
            latest_week_games = [g for g in games if g['season'] == latest_season and g['week'] == latest_week]
            
            # Then add high-profile matchups from other recent games
            high_profile_teams = ['KC', 'BUF', 'PHI', 'DAL', 'SF', 'GB', 'MIN', 'BAL', 'PIT']
            other_popular_games = []
            
            for game in games:
                # Skip games already in latest_week_games
                if game in latest_week_games:
                    continue
                if (game['home_team'] in high_profile_teams or 
                    game['away_team'] in high_profile_teams):
                    other_popular_games.append(game)
            
            # Combine latest games first, then other popular games
            popular_games = latest_week_games + other_popular_games
        else:
            popular_games = []
                
        return jsonify({"games": popular_games[:6]})  # Return top 6 popular games
        
    except Exception as e:
        logger.error(f"Error in /api/popular: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/game/<game_id>', methods=['GET'])
def get_game_details(game_id):
    """Get detailed information for a specific game"""
    try:
        if games_cache is None or schedules_cache is None:
            if not load_nfl_data():
                return jsonify({"error": "Failed to load NFL data"}), 500
        
        # Get game from schedule
        game_row = schedules_cache[schedules_cache['game_id'] == game_id]
        
        if game_row.empty:
            return jsonify({"error": "Game not found"}), 404
        
        game = game_row.iloc[0]
        
        # Get play-by-play data for this game
        game_plays = games_cache[games_cache['game_id'] == game_id]
        
        game_details = {
            'game_id': game['game_id'],
            'home_team': game['home_team'],
            'away_team': game['away_team'],
            'home_score': int(game['home_score']) if pd.notna(game['home_score']) else 0,
            'away_score': int(game['away_score']) if pd.notna(game['away_score']) else 0,
            'week': game['week'],  
            'season': game['season'],
            'gameday': game['gameday'],
            'gametime': game['gametime'],
            'total_plays': len(game_plays)
        }
        
        return jsonify(game_details)
        
    except Exception as e:
        logger.error(f"Error in /api/game/{game_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Load data on startup if running directly
    logger.info("Starting NFL API server...")
    load_nfl_data()
    app.run(debug=True, port=5001)  # Different port from your existing app.py