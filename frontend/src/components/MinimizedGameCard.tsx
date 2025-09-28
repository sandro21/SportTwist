import type { NFLGame } from '../services/nflApi'

interface MinimizedGameCardProps {
  game: NFLGame
  onClick?: () => void
}

// Team data from team_logos_dict.py
const teamData = {
  'ARI': { name: 'Cardinals', logo: 'https://upload.wikimedia.org/wikipedia/en/thumb/7/72/Arizona_Cardinals_logo.svg/179px-Arizona_Cardinals_logo.svg.png' },
  'ATL': { name: 'Falcons', logo: 'https://upload.wikimedia.org/wikipedia/en/thumb/c/c5/Atlanta_Falcons_logo.svg/192px-Atlanta_Falcons_logo.svg.png' },
  'BAL': { name: 'Ravens', logo: 'https://upload.wikimedia.org/wikipedia/en/thumb/1/16/Baltimore_Ravens_logo.svg/193px-Baltimore_Ravens_logo.svg.png' },
  'BUF': { name: 'Bills', logo: 'https://upload.wikimedia.org/wikipedia/en/thumb/7/77/Buffalo_Bills_logo.svg/189px-Buffalo_Bills_logo.svg.png' },
  'CAR': { name: 'Panthers', logo: 'https://upload.wikimedia.org/wikipedia/en/thumb/1/1c/Carolina_Panthers_logo.svg/100px-Carolina_Panthers_logo.svg.png' },
  'CHI': { name: 'Bears', logo: 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Chicago_Bears_logo.svg/100px-Chicago_Bears_logo.svg.png' },
  'CIN': { name: 'Bengals', logo: 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/81/Cincinnati_Bengals_logo.svg/100px-Cincinnati_Bengals_logo.svg.png' },
  'CLE': { name: 'Browns', logo: 'https://upload.wikimedia.org/wikipedia/en/thumb/d/d9/Cleveland_Browns_logo.svg/100px-Cleveland_Browns_logo.svg.png' },
  'DAL': { name: 'Cowboys', logo: 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Dallas_Cowboys.svg/100px-Dallas_Cowboys.svg.png' },
  'DEN': { name: 'Broncos', logo: 'https://upload.wikimedia.org/wikipedia/en/thumb/4/44/Denver_Broncos_logo.svg/100px-Denver_Broncos_logo.svg.png' },
  'DET': { name: 'Lions', logo: 'https://upload.wikimedia.org/wikipedia/en/thumb/7/71/Detroit_Lions_logo.svg/100px-Detroit_Lions_logo.svg.png' },
  'GB': { name: 'Packers', logo: 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Green_Bay_Packers_logo.svg/100px-Green_Bay_Packers_logo.svg.png' },
  'HOU': { name: 'Texans', logo: 'https://upload.wikimedia.org/wikipedia/en/thumb/2/28/Houston_Texans_logo.svg/100px-Houston_Texans_logo.svg.png' },
  'IND': { name: 'Colts', logo: 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/00/Indianapolis_Colts_logo.svg/100px-Indianapolis_Colts_logo.svg.png' },
  'JAX': { name: 'Jaguars', logo: 'https://upload.wikimedia.org/wikipedia/en/thumb/7/74/Jacksonville_Jaguars_logo.svg/100px-Jacksonville_Jaguars_logo.svg.png' },
  'KC': { name: 'Chiefs', logo: 'https://upload.wikimedia.org/wikipedia/en/thumb/e/e1/Kansas_City_Chiefs_logo.svg/100px-Kansas_City_Chiefs_logo.svg.png' },
  'LA': { name: 'Rams', logo: 'https://upload.wikimedia.org/wikipedia/en/thumb/8/8a/Los_Angeles_Rams_logo.svg/100px-Los_Angeles_Rams_logo.svg.png' },
  'LAC': { name: 'Chargers', logo: 'https://upload.wikimedia.org/wikipedia/en/thumb/7/72/NFL_Chargers_logo.svg/100px-NFL_Chargers_logo.svg.png' },
  'MIA': { name: 'Dolphins', logo: 'https://upload.wikimedia.org/wikipedia/en/thumb/3/37/Miami_Dolphins_logo.svg/100px-Miami_Dolphins_logo.svg.png' },
  'MIN': { name: 'Vikings', logo: 'https://upload.wikimedia.org/wikipedia/en/thumb/4/48/Minnesota_Vikings_logo.svg/98px-Minnesota_Vikings_logo.svg.png' },
  'NE': { name: 'Patriots', logo: 'https://upload.wikimedia.org/wikipedia/en/thumb/b/b9/New_England_Patriots_logo.svg/100px-New_England_Patriots_logo.svg.png' },
  'NO': { name: 'Saints', logo: 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/New_Orleans_Saints_logo.svg/98px-New_Orleans_Saints_logo.svg.png' },
  'NYG': { name: 'Giants', logo: 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/60/New_York_Giants_logo.svg/100px-New_York_Giants_logo.svg.png' },
  'NYJ': { name: 'Jets', logo: 'https://upload.wikimedia.org/wikipedia/en/thumb/6/6b/New_York_Jets_logo.svg/100px-New_York_Jets_logo.svg.png' },
  'PHI': { name: 'Eagles', logo: 'https://upload.wikimedia.org/wikipedia/en/thumb/8/8e/Philadelphia_Eagles_logo.svg/100px-Philadelphia_Eagles_logo.svg.png' },
  'PIT': { name: 'Steelers', logo: 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/Pittsburgh_Steelers_logo.svg/100px-Pittsburgh_Steelers_logo.svg.png' },
  'SEA': { name: 'Seahawks', logo: 'https://upload.wikimedia.org/wikipedia/en/thumb/8/8e/Seattle_Seahawks_logo.svg/100px-Seattle_Seahawks_logo.svg.png' },
  'SF': { name: '49ers', logo: 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/San_Francisco_49ers_logo.svg/100px-San_Francisco_49ers_logo.svg.png' },
  'TB': { name: 'Buccaneers', logo: 'https://upload.wikimedia.org/wikipedia/en/thumb/a/a2/Tampa_Bay_Buccaneers_logo.svg/100px-Tampa_Bay_Buccaneers_logo.svg.png' },
  'TEN': { name: 'Titans', logo: 'https://github.com/nflverse/nflverse-pbp/raw/master/titans.png' },
  'WAS': { name: 'Commanders', logo: 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e2/Washington_commanders.svg/100px-Washington_commanders.svg.png' }
}

function MinimizedGameCard({ game, onClick }: MinimizedGameCardProps) {
  // Require real NFL data
  const team1Code = game.away_team
  const team2Code = game.home_team
  const score1 = game.away_score
  const score2 = game.home_score
  const gameDateTime = new Date(game.gameday)
  const options: Intl.DateTimeFormatOptions = { month: 'short', day: 'numeric', year: 'numeric' }
  const gameDate = `${gameDateTime.toLocaleDateString('en-US', options)}  •  Week ${game.week}`
  
  // Get team data or fallback to Eagles vs Cowboys
  const team1Data = teamData[team1Code as keyof typeof teamData] || teamData['PHI']
  const team2Data = teamData[team2Code as keyof typeof teamData] || teamData['DAL']
  
  // Determine winner (higher score)
  const team1Won = score1 > score2

  // Team info styles for layout
  const teamInfoStyles = {
    display: 'flex',
    flexDirection: 'row' as const,
    alignItems: 'center',
    gap: '10px'
  }

  return (
    <div className="h-game-card" onClick={onClick}>
      {/* Team 1 */}
      <div className="h-team-card">
        <div style={teamInfoStyles}>
          <div className="h-team-image">
            <img src={team1Data.logo} alt={team1Data.name} />
          </div>
          <div 
            className="h-team-name" 
            style={{ opacity: team1Won ? '1' : '0.65' }}
          >
            {team1Code}
          </div>
        </div>
        <div 
          className="h-team-score" 
          style={{ opacity: team1Won ? '1' : '0.65' }}
        >
          {score1}
        </div>
      </div>

      {/* Team 2 */}
      <div className="h-team-card">
        <div style={teamInfoStyles}>
          <div className="h-team-image">
            <img src={team2Data.logo} alt={team2Data.name} />
          </div>
          <div 
            className="h-team-name" 
            style={{ opacity: team1Won ? '0.65' : '1' }}
          >
            {team2Code}
          </div>
        </div>
        <div 
          className="h-team-score" 
          style={{ opacity: team1Won ? '0.65' : '1' }}
        >
          {score2}
        </div>
      </div>

      {/* Date */}
      <div className="h-date">
        {gameDate}
      </div>
    </div>
  )
}

export default MinimizedGameCard
