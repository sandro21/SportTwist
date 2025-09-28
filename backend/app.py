# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import time
import math
import nflreadpy as nfl
from team_logos_dict import team_logos
from game import Game

app = Flask(__name__)
CORS(app)

# -------------------------
# In-memory cache
# -------------------------
cache = {}
CACHE_EXPIRY = 10 * 60  # 10 minutes

def get_cached_game(game_id):
    entry = cache.get(game_id)
    if not entry:
        return None
    if time.time() - entry['timestamp'] > CACHE_EXPIRY:
        del cache[game_id]
        return None
    return entry['data']

def set_cached_game(game_id, data):
    cache[game_id] = {'timestamp': time.time(), 'data': data}
# -------------------------
# Endpoints
# -------------------------
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/teams", methods=["GET"])
def teams():
    return jsonify(team_logos)


@app.route("/game/<string:game_id>", methods=["GET"])
def get_game(game_id):
    print(game_id)
    year = int(game_id[:4])
    game = Game(game_id, year)
    return jsonify({"plays": game.plays})

@app.route("/game/<string:game_id>/timeline", methods=["GET"])
def get_timeline(game_id):
    try:
        cached = get_cached_game(game_id)
        if cached is None:
            raw = fetch_game_raw(game_id)
            set_cached_game(game_id, raw)
        else:
            raw = cached

        timeline = extract_timeline(raw)
        return jsonify(timeline)
    except Exception as e:
        return jsonify({"error": "Unexpected server error", "details": str(e)}), 500

@app.route("/game/<string:game_id>/progression", methods=["GET"])
def get_progression(game_id):
    try:
        cached = get_cached_game(game_id)
        if cached is None:
            raw = fetch_game_raw(game_id)
            set_cached_game(game_id, raw)
        else:
            raw = cached

        prog = extract_progression(raw)
        return jsonify(prog)
    except Exception as e:
        return jsonify({"error": "Unexpected server error", "details": str(e)}), 500

@app.route("/game/<string:game_id>/insights", methods=["GET"])
def get_insights(game_id):
    try:
        cached = get_cached_game(game_id)
        if cached is None:
            raw = fetch_game_raw(game_id)
            set_cached_game(game_id, raw)
        else:
            raw = cached

        insights = extract_insights(raw)
        return jsonify(insights)
    except Exception as e:
        return jsonify({"error": "Unexpected server error", "details": str(e)}), 500

@app.route("/simulate", methods=["POST"])
def simulate():
    try:
        payload = request.get_json(force=True)
        game_id = payload.get("game_id")
        what_if = payload.get("what_if", {})

        if not game_id or not isinstance(what_if, dict):
            return jsonify({"error": "Missing game_id or what_if body (must be object)"}), 400

        cached = get_cached_game(game_id)
        if cached is None:
            raw = fetch_game_raw(game_id)
            set_cached_game(game_id, raw)
        else:
            raw = cached

        header = extract_header_info(raw)
        timeline = extract_timeline(raw)
        plays = extract_plays(raw)
        progression = extract_progression(raw)

        home_name = header.get("home_team_name")
        away_name = header.get("away_team_name")
        home_score = int(header.get("home_team_score") or 0)
        away_score = int(header.get("away_team_score") or 0)

        new_home = home_score
        new_away = away_score
        applied = False
        reason = None

        team_key = what_if.get("team_abbr") or what_if.get("team") or what_if.get("team_name")
        points = what_if.get("points")
        if team_key and isinstance(points, (int, float)):
            tk = str(team_key).lower()
            if home_name and tk in home_name.lower():
                new_home += int(points)
                applied = True
                reason = f"Applied {points:+d} to home team ({home_name})"
            elif away_name and tk in away_name.lower():
                new_away += int(points)
                applied = True
                reason = f"Applied {points:+d} to away team ({away_name})"

        event_id = what_if.get("event_id")
        if event_id:
            for ev in timeline:
                if ev.get("id") == event_id or ev.get("event_id") == event_id or ev.get("play_id") == event_id:
                    ev["simulated"] = True
                    ev["sim_description"] = what_if.get("description") or "what-if applied"
                    break

        p_orig_home = score_diff_to_winprob(home_score, away_score)
        p_new_home = score_diff_to_winprob(new_home, new_away)

        insights = {
            "phi_score_change": new_home - home_score if home_name and "phi" in home_name.lower() else 0,
            "dal_score_change": new_away - away_score if away_name and "dal" in away_name.lower() else 0,
            "win_probability_change": {
                home_name: f"{int(round((p_new_home - p_orig_home) * 100)):+d}%",
                away_name: f"{int(round(((1 - p_new_home) - (1 - p_orig_home)) * 100)):+d}%"
            },
            "momentum_change": "High" if abs(p_new_home - p_orig_home) > 0.20 else "Medium" if abs(p_new_home - p_orig_home) > 0.07 else "Low"
        }

        header_out = {
            "original": {
                "home_team_name": home_name,
                "away_team_name": away_name,
                "home_team_score": home_score,
                "away_team_score": away_score,
                "win_probability": {
                    home_name: f"{int(round(p_orig_home * 100))}%",
                    away_name: f"{int(round((1 - p_orig_home) * 100))}%"
                }
            },
            "what_if_applied": applied,
            "what_if_reason": reason,
            "what_if_description": what_if.get("description"),
            "new": {
                "home_team_name": home_name,
                "away_team_name": away_name,
                "home_team_score": new_home,
                "away_team_score": new_away,
                "win_probability": {
                    home_name: f"{int(round(p_new_home * 100))}%",
                    away_name: f"{int(round((1 - p_new_home) * 100))}%"
                }
            }
        }

        prog = progression.copy()
        if prog.get("what_if_score_data") and len(prog["what_if_score_data"]) > 0:
            prog["what_if_score_data"][-1] = new_home
        if prog.get("original_score_data") and len(prog["original_score_data"]) > 0:
            prog["original_score_data"][-1] = home_score

        result = {
            "header_info": header_out,
            "timeline": timeline,
            "insights": insights,
            "score_progression": prog,
            "plays": plays,
            "what_if": what_if
        }
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": "Unexpected server error", "details": str(e)}), 500

# Run server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)