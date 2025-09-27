import nfl_data_py as nfl

teams = nfl.import_team_desc()
logos = teams[["team_abbr", "team_logo_wikipedia"]].copy()
logo_dict = dict(zip(logos["team_abbr"], logos["team_logo_wikipedia"]))

with open("team_logos_dict.py", "w", encoding="utf-8") as f:
    f.write("team_logos = {\n")
    for abbr, url in logo_dict.items():
        f.write(f"    '{abbr}': '{url}',\n")
    f.write("}\n")
