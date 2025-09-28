from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import time

app = Flask(__name__)
CORS(app)

# In-memory cache
cache = {}
CACHE_EXPIRY = 10 * 60  # 10 minutes in seconds


# Helper function to check cache
def get_cached_game(game_id):
    cached = cache.get(game_id)
    if cached and (time.time() - cached['timestamp'] < CACHE_EXPIRY):
        return cached['data']
    return None


@app.route('/simulate', methods=['POST'])
def simulate_game():
    try:
        data = request.json
        game_id = data.get("game_id")
        what_if = data.get("what_if")

        if not game_id or not what_if:
            return jsonify({"error": "Missing game_id or what_if data"}), 400

        # Check cache
        cached_data = get_cached_game(game_id)
        if cached_data:
            game_data = cached_data
        else:
            # Fetch from NFLverse (adjust endpoint!)
            nflverse_url = f"https://api.nflverse.com/games/{game_id}"
            response = requests.get(nflverse_url)
            if response.status_code != 200:
                return jsonify({"error": "Failed to fetch data from NFLverse"}), 500

            game_data = response.json()
            cache[game_id] = {"timestamp": time.time(), "data": game_data}

        # --------------------------
        # 1. Game Header Information
        # --------------------------
        header_info = {
            "home_team_name": game_data.get("home_team_name"),
            "away_team_name": game_data.get("away_team_name"),
            "home_team_logo": game_data.get("home_team_logo"),
            "away_team_logo": game_data.get("away_team_logo"),
            "home_team_score": game_data.get("home_team_score"),
            "away_team_score": game_data.get("away_team_score"),
            "quarter": game_data.get("quarter"),
            "time_remaining": game_data.get("time_remaining"),
            "win_probability_team": game_data.get("win_probability_team"),
            "win_probability_percentage": game_data.get("win_probability_percentage"),
        }

        # --------------------------
        # 2. Game Timeline
        # --------------------------
        timeline = []
        for event in game_data.get("timeline", []):
            timeline.append({
                "event_quarter": event.get("quarter"),
                "event_time": event.get("time"),
                "event_description": event.get("description"),
                "outcome_type": event.get("outcome_type"),
                "outcome_indicator": event.get("outcome_indicator"),
                "highlight_level": event.get("highlight_level"),
                "points_change": event.get("points_change"),
            })

        # --------------------------
        # 3. Insights Section
        # --------------------------
        insights = {
            "phi_score_change": game_data.get("phi_score_change", 0),
            "dal_score_change": game_data.get("dal_score_change", 0),
            "win_probability_change": game_data.get("win_probability_change", "0%"),
            "momentum_change": game_data.get("momentum_change", "Low"),
        }

        # --------------------------
        # 4. Score Progression Graph
        # --------------------------
        score_progression = {
            "progression_quarter_labels": game_data.get("progression_quarter_labels", []),
            "progression_score_values": game_data.get("progression_score_values", []),
            "original_score_data": game_data.get("original_score_data", []),
            "what_if_score_data": game_data.get("what_if_score_data", []),
        }

        # --------------------------
        # Core Play Variables
        # --------------------------
        plays = {
            "Pass": game_data.get("Pass", {}),
            "Fumble": game_data.get("Fumble", 0),
            "ThirdDownConverted": game_data.get("ThirdDownConverted", 0),
            "FourthDown": game_data.get("FourthDown", {}),
            "ExtraPoint": game_data.get("ExtraPoint", {}),
            "TwoPointConversion": game_data.get("TwoPointConversion", {}),
            "FieldGoal": game_data.get("FieldGoal", {}),
            "Penalties": game_data.get("Penalties", 0),
            "Timeouts": game_data.get("Timeouts", 0),
        }

        # --------------------------
        # Final Response
        # --------------------------
        result = {
            "header_info": header_info,
            "timeline": timeline,
            "insights": insights,
            "score_progression": score_progression,
            "plays": plays,
            "what_if": what_if,
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)