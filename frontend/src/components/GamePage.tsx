import { useEffect, useState } from 'react'
import './GamePage.css'
import GameEvent from './GameEvent'
import { nflApiService, type NFLGame } from '../services/nflApi'

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

interface GamePageProps {
  game?: NFLGame | null
}

const GamePage = ({ game }: GamePageProps) => {
  // Use real game data if provided, otherwise fallback to sample data
  let team1Code: string, team2Code: string, score1: number, score2: number, weekText: string, dateText: string;
  
  if (game) {
    // Use real NFL data
    team1Code = game.away_team;  // Away team (first in "team vs team" format)
    team2Code = game.home_team;  // Home team (second in "team vs team" format)
    score1 = game.away_score;
    score2 = game.home_score;
    weekText = `Week ${game.week}`;
    
    // Format date from real data
    const gameDateTime = new Date(game.gameday);
    const options: Intl.DateTimeFormatOptions = { 
      month: 'long', 
      day: 'numeric', 
      year: 'numeric' 
    };
    dateText = gameDateTime.toLocaleDateString('en-US', options);
  } else {
    // Fallback to sample data
    team1Code = 'PHI';
    team2Code = 'DAL';
    score1 = 28;
    score2 = 24;
    weekText = 'Week 4';
    dateText = 'September 24, 2025';
  }
  
  const team1Data = teamData[team1Code as keyof typeof teamData] || teamData['PHI']
  const team2Data = teamData[team2Code as keyof typeof teamData] || teamData['DAL']
  
  // Mocked score change for big game card (for demo purposes)
  const prevScore1 = score1 - 1
  const prevScore2 = score2
  const score1Delta = score1 - prevScore1
  const score2Delta = score2 - prevScore2
  const team1Won = score1 > score2

  // State management for card interactions - single layer only
  const [activeCardIndex, setActiveCardIndex] = useState<number | null>(null)
  const [affectedCards, setAffectedCards] = useState<Set<number>>(new Set())

  // Play-by-play events derived from backend
  type UiEvent = {
    team: string
    score: string
    action: string
    quarter: string
    timeRemaining: string
    description: string
    downAndDistance: string
    changeableAttributes?: any
  }

  const [events, setEvents] = useState<UiEvent[]>([])
  const [originalEvents, setOriginalEvents] = useState<UiEvent[]>([]) // Store original events
  const [isLoadingPbp, setIsLoadingPbp] = useState<boolean>(false)
  const [pbpError, setPbpError] = useState<string | null>(null)
  const [isSimulating, setIsSimulating] = useState<boolean>(false)

  const formatQuarter = (qtr: number): string => {
    if (qtr === 1) return '1st'
    if (qtr === 2) return '2nd'
    if (qtr === 3) return '3rd'
    return `${qtr}th`
  }

  const formatTime = (seconds: number): string => {
    const m = Math.floor(seconds / 60)
    const s = Math.floor(seconds % 60)
    const mm = m.toString()
    const ss = s.toString().padStart(2, '0')
    return `${mm}:${ss}`
  }

  const inferAction = (desc: string, changeable: any): string => {
    const d = desc.toLowerCase()
    if (d.includes('touchdown')) return 'Touchdown'
    if (d.includes('field goal')) return 'Field Goal'
    if (d.includes('punt')) return 'Fourth Down'
    if (d.includes('conversion')) return 'Conversion'
    if (d.includes('penalty') || (changeable && changeable.called)) return 'Penalty'
    if (d.includes('pass') || (changeable && (changeable.is_complete !== undefined || changeable.is_interception !== undefined))) return 'Pass'
    return 'Play'
  }

  useEffect(() => {
    const loadPbp = async () => {
      if (!game) {
        setEvents([])
        setPbpError(null)
        return
      }
      
      console.log('Loading PBP for game:', game.game_id)
      setIsLoadingPbp(true)
      setPbpError(null)
      
      try {
        const details: any = await nflApiService.getGameDetails(game.game_id)
        console.log('PBP API response:', details)
        
        setIsLoadingPbp(false)
        
        if (!details) {
          setPbpError('No game data received from API')
          setEvents([])
          return
        }
        
        if (!details.plays) {
          setPbpError('No plays found in game data')
          setEvents([])
          return
        }

        const keys = Object.keys(details.plays)
          .map(k => parseInt(k, 10))
          .filter(n => !Number.isNaN(n))
          .sort((a, b) => a - b) // Chronological order: 1st to 4th quarter

        console.log(`Found ${keys.length} plays for game ${game.game_id}`)

        const toUi: UiEvent[] = keys.map((idx) => {
          const p: any = details.plays[idx]
          const team = typeof p.posteam === 'string' ? p.posteam : ''
          const score = `${Math.floor(p.away_score ?? 0)}-${Math.floor(p.home_score ?? 0)}`
          const quarter = formatQuarter(Math.floor(p.qtr ?? 1))
          const timeRemaining = formatTime(Math.floor(p.quarter_seconds_remaining ?? 0))
          const description = p.desc || ''
          const down = p.down ? Math.floor(p.down) : undefined
          const toGo = p.to_go ? Math.floor(p.to_go) : undefined
          const downText = down ? `${down}${down === 1 ? 'st' : down === 2 ? 'nd' : down === 3 ? 'rd' : 'th'}` : ''
          const yrdln = p.yrdln || ''
          const downAndDistance = down && toGo ? `${downText} & ${toGo} at ${yrdln}` : yrdln
          const action = inferAction(description, p.changeable_attributes)
          const changeableAttributes = p.changeable_attributes
          return { team, score, action, quarter, timeRemaining, description, downAndDistance, changeableAttributes }
        })

        setEvents(toUi)
        setOriginalEvents(toUi) // Store original for reference
        setActiveCardIndex(null)
        setAffectedCards(new Set())
      } catch (error) {
        console.error('Error loading PBP:', error)
        setIsLoadingPbp(false)
        setPbpError(`Failed to load play-by-play: ${error}`)
        setEvents([])
      }
    }

    loadPbp()
  }, [game?.game_id])

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

  // Handle simulation when a play is changed
  const handlePlayChange = async (playIndex: number, newChangeableAttributes: any) => {
    if (!game) return
    
    // Only simulate plays that have supported changeable attributes
    // Skip plays that don't have reroll methods implemented
    const supportedAttributes = ['is_complete', 'is_interception', 'called']
    const hasSupported = supportedAttributes.some(attr => newChangeableAttributes.hasOwnProperty(attr))
    
    if (!hasSupported) {
      console.log('Skipping simulation - play type not supported for changes:', newChangeableAttributes)
      return
    }
    
    try {
      setIsSimulating(true)
      console.log(`Simulating change at play ${playIndex}:`, newChangeableAttributes)
      
      // Make simulation API call directly
      const response = await fetch('http://localhost:5001/api/simulate/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          game_id: game.game_id,
          changeable_attributes: newChangeableAttributes,
          start_play_index: playIndex
        })
      })
      
      if (!response.ok) {
        throw new Error(`Simulation failed: ${response.status} ${response.statusText}`)
      }
      
      const simulationResult = await response.json()
      
      console.log('Simulation result received:', simulationResult)
      
      // Replace ALL plays with simulation results
      if (simulationResult.plays) {
        const simKeys = Object.keys(simulationResult.plays)
          .map(k => parseInt(k, 10))
          .filter(n => !Number.isNaN(n))
          .sort((a, b) => a - b) // Chronological order: 1st to 4th quarter

        const newEvents: UiEvent[] = simKeys.map((simIdx) => {
          const p = simulationResult.plays[simIdx]
          const team = typeof p.posteam === 'string' ? p.posteam : ''
          const score = `${Math.floor(p.away_score ?? 0)}-${Math.floor(p.home_score ?? 0)}`
          const quarter = formatQuarter(Math.floor(p.qtr ?? 1))
          const timeRemaining = formatTime(Math.floor(p.quarter_seconds_remaining ?? 0))
          const description = p.desc || ''
          
          // Debug simulation results
          console.log(`Play ${simIdx} simulation result:`, {
            original_desc: description,
            changeable_attributes: p.changeable_attributes,
            team: team,
            score: score
          })
          
          const down = p.down ? Math.floor(p.down) : undefined
          const toGo = p.to_go ? Math.floor(p.to_go) : undefined
          const downText = down ? `${down}${down === 1 ? 'st' : down === 2 ? 'nd' : down === 3 ? 'rd' : 'th'}` : ''
          const yrdln = p.yrdln || ''
          const downAndDistance = down && toGo ? `${downText} & ${toGo} at ${yrdln}` : yrdln
          const action = inferAction(description, p.changeable_attributes)
          const changeableAttributes = p.changeable_attributes
          
          return {
            team, score, action, quarter, timeRemaining, description, downAndDistance, changeableAttributes
          }
        })
        
        console.log(`Updating all ${newEvents.length} plays from simulation`)
        setEvents(newEvents)
        
        // Clear active card state since we have all new data
        setActiveCardIndex(null)
        setAffectedCards(new Set())
      }
      
      // Update final scores in the big game card
      if (simulationResult.final_score) {
        console.log('Updated final scores:', simulationResult.final_score)
        // The scores will be reflected in the last play's score already
      }
      
    } catch (error) {
      console.error('Simulation failed:', error)
      // Could show an error message to user here
    } finally {
      setIsSimulating(false)
    }
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
              <div className="big-game-city-name">{team1Code}</div>
              <div 
                className="big-game-mascot-name" 
                style={{ 
                  opacity: team1Won ? '1' : '0.65',
                  color: team1Won ? '#000000' : '#666666'
                }}
              >
                {team1Data.name}
              </div>
            </div>
            <div 
              className={`big-game-score ${score1Delta > 0 ? 'score-green' : score1Delta < 0 ? 'score-red' : ''}`}
              style={{ 
                opacity: team1Won ? '1' : '0.65',
                color: team1Won ? undefined : '#666666'
              }}
            >
              {score1}
              <span className="score-old">{prevScore1}</span>
              {score1Delta !== 0 && (
                <span className="score-delta">{score1Delta > 0 ? '▲' : '▼'} {score1Delta > 0 ? `+${score1Delta}` : `${score1Delta}`}</span>
              )}
            </div>
          </div>

          {/* Middle Date */}
          <div className="big-game-middle">
            <div className="big-game-week">{weekText}</div>
            <div className="big-game-date">{dateText}</div>
          </div>

          {/* Right Team */}
          <div className="big-game-right-team">
            <div 
              className={`big-game-score ${score2Delta > 0 ? 'score-green' : score2Delta < 0 ? 'score-red' : ''}`}
              style={{ 
                opacity: team1Won ? '0.65' : '1',
                color: team1Won ? '#666666' : undefined
              }}
            >
              {score2}
              <span className="score-old">{prevScore2}</span>
              {score2Delta !== 0 && (
                <span className="score-delta">{score2Delta > 0 ? '▲' : '▼'} {score2Delta > 0 ? `+${score2Delta}` : `${score2Delta}`}</span>
              )}
            </div>
            <div className="big-game-team-names">
              <div className="big-game-city-name">{team2Code}</div>
              <div 
                className="big-game-mascot-name" 
                style={{ 
                  opacity: team1Won ? '0.65' : '1',
                  color: team1Won ? '#666666' : '#000000'
                }}
              >
                {team2Data.name}
              </div>
            </div>
            <img src={team2Data.logo} alt={team2Data.name} className="big-game-logo" />
          </div>
        </div>

        {/* Main Content Area - Two Column Layout */}
        <div className="main-content">
          {/* Left Column - Events Container (60%) */}
          <div className="events-container">
            <h3>Game Events</h3>
            
            {/* Render game events with visual quarter dividers */}
            {isLoadingPbp && (
              <div className="search-loading">Loading play-by-play...</div>
            )}
            {isSimulating && (
              <div className="simulation-loading-overlay">
                <div className="simulation-loading-content">
                  <div className="simulation-spinner"></div>
                  <div className="simulation-loading-text">Simulating game changes...</div>
                  <div className="simulation-loading-subtext">Please wait while we calculate alternate outcomes</div>
                </div>
              </div>
            )}
            {pbpError && (
              <div className="search-no-results">
                Error: {pbpError}
                <br />
                <small>Game ID: {game?.game_id}</small>
              </div>
            )}
            {!isLoadingPbp && !pbpError && events.length === 0 && (
              <div className="search-no-results">No plays found for this game</div>
            )}
            {!isLoadingPbp && !pbpError && events.map((event, index) => {
              const cardState = getCardState(index)
              const prevEvent = index > 0 ? events[index - 1] : null
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
                    key={`${index}-${JSON.stringify(event.changeableAttributes)}`}
                    team={event.team}
                    score={event.score}
                    action={event.action}
                    quarter={event.quarter}
                    timeRemaining={event.timeRemaining}
                    description={event.description}
                    downAndDistance={event.downAndDistance}
                    cardState={cardState}
                    changeableAttributes={event.changeableAttributes}
                    onToggle={() => handleCardToggle(index)}
                    onPlayChange={(newAttributes) => handlePlayChange(index, newAttributes)}
                    playIndex={index}
                    disabled={isSimulating}
                  />
                </div>
              )
            })}
          </div>

          {/* Right Column - New Content Area (40%) */}
          <div className="right-panel">
            <h3>Game Analysis</h3>
            <div className="analysis-content">
              {/* Summary Section */}
              <div className="analysis-section">
                <div className="input-container">
                  <h4>Summary:</h4>
                  <p className="summary-text">
                    This game featured a close battle between the Eagles and Cowboys, with key plays in the fourth quarter determining the outcome. The Eagles managed to secure a narrow victory with a late touchdown.
                  </p>
                </div>
              </div>

              {/* Simulated Statistics Section */}
              <div className="analysis-section">
                <div className="input-container">
                  <table className="analysis-table">
                    <thead>
                      <tr>
                        <th></th>
                        <th>{team1Code}</th>
                        <th>{team2Code}</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td>Simulated Win %</td>
                        <td>65%</td>
                        <td>35%</td>
                      </tr>
                      <tr>
                        <td>Simulated Avg Score</td>
                        <td>28.5</td>
                        <td>24.2</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default GamePage