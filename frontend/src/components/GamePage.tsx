import { useState, useEffect } from 'react'
import './GamePage.css'
import GameEvent from './GameEvent'

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

const GamePage = () => {
  // Sample game data
  const teams = "PHI vs DAL"
  const teamCodes = teams.split(' vs ')
  const team1Code = teamCodes[0] || 'PHI'
  const team2Code = teamCodes[1] || 'DAL'
  
  const team1Data = teamData[team1Code as keyof typeof teamData] || teamData['PHI']
  const team2Data = teamData[team2Code as keyof typeof teamData] || teamData['DAL']
  
  const score1 = 28
  const score2 = 24
  const team1Won = score1 > score2

  // State management for card interactions - single layer only
  const [activeCardIndex, setActiveCardIndex] = useState<number | null>(null)
  const [affectedCards, setAffectedCards] = useState<Set<number>>(new Set())

  // Game events data with mixed outcomes (chronological order)
  const gameEvents = [
    { team: "KC", score: "28-24", action: "Touchdown", quarter: "4th", timeRemaining: "0:12", description: "15-P.Mahomes pass short right to 87-T.Kelce for 8 yards, TOUCHDOWN", downAndDistance: "2nd & 8 at BUF 8", isFailure: false },
    { team: "KC", score: "27-24", action: "Field Goal", quarter: "4th", timeRemaining: "2:34", description: "7-H.Butker 45 yard field goal is GOOD", downAndDistance: "4th & 3 at BUF 27", isFailure: false },
    { team: "BUF", score: "24-24", action: "Penalty", quarter: "4th", timeRemaining: "3:45", description: "Defensive Pass Interference on 24-T.White", downAndDistance: "3rd & 7 at KC 23", isFailure: true },
    { team: "BUF", score: "24-21", action: "Pass", quarter: "4th", timeRemaining: "5:12", description: "17-J.Allen pass short middle to 14-S.Diggs for 12 yards", downAndDistance: "1st & 10 at BUF 35", isFailure: false },
    { team: "KC", score: "21-21", action: "Fourth Down", quarter: "3rd", timeRemaining: "1:23", description: "5-T.Townsend punts 42 yards to BUF 18, Center-45-J.Winchester", downAndDistance: "4th & 5 at KC 40", isFailure: true },
    { team: "BUF", score: "21-14", action: "Touchdown", quarter: "3rd", timeRemaining: "4:56", description: "26-J.Cook rush right tackle for 3 yards, TOUCHDOWN", downAndDistance: "1st & Goal at KC 3", isFailure: false },
    { team: "KC", score: "14-14", action: "Pass", quarter: "3rd", timeRemaining: "8:34", description: "15-P.Mahomes pass deep left to 10-R.Rice for 23 yards", downAndDistance: "2nd & 6 at KC 44", isFailure: false },
    { team: "BUF", score: "14-7", action: "Field Goal", quarter: "2nd", timeRemaining: "0:03", description: "2-T.Bass 38 yard field goal is GOOD", downAndDistance: "4th & 2 at KC 20", isFailure: false },
    { team: "KC", score: "14-4", action: "Penalty", quarter: "2nd", timeRemaining: "2:15", description: "Offensive Holding on 65-C.Humphrey", downAndDistance: "1st & 10 at BUF 25", isFailure: true },
    { team: "KC", score: "14-0", action: "Conversion", quarter: "2nd", timeRemaining: "5:42", description: "2-Point conversion attempt", downAndDistance: "After TD", isFailure: false },
    { team: "BUF", score: "7-0", action: "Pass", quarter: "2nd", timeRemaining: "8:17", description: "17-J.Allen pass short right to 2-G.Davis for 7 yards", downAndDistance: "3rd & 4 at KC 12", isFailure: false },
    { team: "KC", score: "0-0", action: "Conversion", quarter: "1st", timeRemaining: "14:56", description: "1-Point conversion attempt", downAndDistance: "After TD", isFailure: true }
  ]

  // Helper function to get card state
  const getCardState = (cardIndex: number) => {
    if (activeCardIndex === cardIndex) {
      return 'changed'
    }
    
    if (affectedCards.has(cardIndex)) {
      return 'affected'
    }
    
    return 'not-affected'
  }

  const handleCardToggle = (cardIndex: number) => {
    if (activeCardIndex === cardIndex) {
      // Untrigger current card - clear everything
      setActiveCardIndex(null)
      setAffectedCards(new Set())
    } else {
      // Set new active card and mark cards above as affected
      setActiveCardIndex(cardIndex)
      const newAffectedCards = new Set<number>()
      for (let i = 0; i < cardIndex; i++) {
        newAffectedCards.add(i)
      }
      setAffectedCards(newAffectedCards)
    }
  }

  return (
    <div className="game-page">
      <div className="game-page-container">
        {/* Big Game Card */}
        <div className="big-game-card">
          {/* Left Team */}
          <div className="big-game-left-team">
            <img src={team1Data.logo} alt={team1Data.name} className="big-game-logo" />
            <div className="big-game-team-names">
              <div className="big-game-city-name">Philadelphia</div>
              <div 
                className="big-game-mascot-name" 
                style={{ 
                  opacity: team1Won ? '1' : '0.65',
                  color: team1Won ? '#000000' : '#666666'
                }}
              >
                Eagles
              </div>
            </div>
            <div 
              className="big-game-score" 
              style={{ 
                opacity: team1Won ? '1' : '0.65',
                color: team1Won ? '#000000' : '#666666'
              }}
            >
              {score1}
            </div>
          </div>

          {/* Middle Date */}
          <div className="big-game-middle">
            <div className="big-game-week">Week 4</div>
            <div className="big-game-date">September 24, 2025</div>
          </div>

          {/* Right Team */}
          <div className="big-game-right-team">
            <div 
              className="big-game-score" 
              style={{ 
                opacity: team1Won ? '0.65' : '1',
                color: team1Won ? '#666666' : '#000000'
              }}
            >
              {score2}
            </div>
            <div className="big-game-team-names">
              <div className="big-game-city-name">Dallas</div>
              <div 
                className="big-game-mascot-name" 
                style={{ 
                  opacity: team1Won ? '0.65' : '1',
                  color: team1Won ? '#666666' : '#000000'
                }}
              >
                Cowboys
              </div>
            </div>
            <img src={team2Data.logo} alt={team2Data.name} className="big-game-logo" />
          </div>
        </div>

        {/* Events Container */}
        <div className="events-container">
          <h3>Game Events</h3>
          
          {/* Color Legend */}
          <div className="color-legend">
            <h4>Card States Guide</h4>
            <div className="color-items">
              <div className="color-item">
                <div className="color-indicator green"></div>
                <div className="color-label">Active Card: Glows pink when triggered, cards above it have pink background</div>
              </div>
              <div className="color-item">
                <div className="color-indicator"></div>
                <div className="color-label">Not Affected: Default white background, no special styling</div>
              </div>
            </div>
          </div>
          
          {/* Render game events with visual quarter dividers */}
          {gameEvents.map((event, index) => {
            const cardState = getCardState(index)
            const prevEvent = index > 0 ? gameEvents[index - 1] : null
            const showQuarterHeader = !prevEvent || prevEvent.quarter !== event.quarter
            
            return (
              <div key={index}>
                {/* Show quarter header when quarter changes */}
                {showQuarterHeader && (
                  <div className="quarter-header">
                    <h2>{event.quarter} Quarter</h2>
                  </div>
                )}
                
                {/* Render the game event */}
                <GameEvent 
                  team={event.team}
                  score={event.score}
                  action={event.action}
                  quarter={event.quarter}
                  timeRemaining={event.timeRemaining}
                  description={event.description}
                  downAndDistance={event.downAndDistance}
                  cardState={cardState}
                  isFailure={event.isFailure}
                  onToggle={() => handleCardToggle(index)}
                />
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

export default GamePage