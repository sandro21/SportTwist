import { useState, useEffect } from 'react'
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
  gameId?: string
}

const GamePage = ({ gameId }: GamePageProps) => {
  // State for game data
  const [gameData, setGameData] = useState<NFLGame | null>(null)
  const [gameEvents, setGameEvents] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // State management for card interactions - single layer only
  const [activeCardIndex, setActiveCardIndex] = useState<number | null>(null)
  const [affectedCards, setAffectedCards] = useState<Set<number>>(new Set())

  // Fetch game data from Python backend
  useEffect(() => {
    const fetchGameData = async () => {
      if (!gameId) {
        setLoading(false)
        return
      }

      try {
        setLoading(true)
        setError(null)
        
        // Fetch game details from Python backend
        console.log('Fetching game data for gameId:', gameId)
        const response = await nflApiService.getGameDetails(gameId)
        console.log('Backend response:', response)
        console.log('Response keys:', Object.keys(response))
        
        // The backend returns { game_id, plays } structure
        // We need to extract game info and convert plays to events
        if (response.game_id) {
          console.log('Game ID found:', response.game_id)
          console.log('Plays available:', Object.keys(response.plays || {}).length)
          
          // Create a mock game object from the game_id
          // The game_id format is typically like "2024_01_GB_CLE"
          const gameIdParts = gameId.split('_')
          console.log('Game ID parts:', gameIdParts)
          
          if (gameIdParts.length >= 4) {
            const season = parseInt(gameIdParts[0])
            const week = parseInt(gameIdParts[1])
            const awayTeam = gameIdParts[2]
            const homeTeam = gameIdParts[3]
            console.log('Extracted teams:', { awayTeam, homeTeam, season, week })
            
            // Get final scores from the last play
            const playKeys = Object.keys(response.plays || {})
            const lastPlayKey = playKeys[playKeys.length - 1]
            const lastPlay = response.plays[lastPlayKey]
            console.log('Last play:', lastPlay)
            
            const mockGame: NFLGame = {
              game_id: gameId,
              home_team: homeTeam,
              away_team: awayTeam,
              home_score: lastPlay?.home_score || 0,
              away_score: lastPlay?.away_score || 0,
              week: week,
              season: season,
              gameday: '2024-01-01', // Default date
              gametime: '13:00' // Default time
            }
            
            console.log('Created game data:', mockGame)
            setGameData(mockGame)
            
            // Convert plays to events format
            const events = Object.values(response.plays || {}).map((play: any) => ({
              team: play.posteam || 'TBD',
              score: `${play.away_score}-${play.home_score}`,
              action: play.desc?.split(' ')[0] || 'Play',
              quarter: `${play.qtr}${play.qtr === 1 ? 'st' : play.qtr === 2 ? 'nd' : play.qtr === 3 ? 'rd' : 'th'}`,
              timeRemaining: formatTimeRemaining(play.quarter_seconds_remaining),
              description: play.desc || 'No description',
              downAndDistance: play.down ? `${play.down} & ${play.to_go} at ${play.yrdln}` : 'N/A',
              isFailure: false // Default to not failure
            }))
            
            console.log('Created events:', events.length, 'events')
            console.log('First few events:', events.slice(0, 3))
            
            // Reverse to show latest plays first
            setGameEvents(events.reverse())
          }
        }
        
      } catch (err) {
        console.error('Error fetching game data:', err)
        setError('Failed to load game data')
      } finally {
        setLoading(false)
      }
    }

    fetchGameData()
  }, [gameId])

  // Helper function to format time remaining
  const formatTimeRemaining = (seconds: number) => {
    if (!seconds) return '0:00'
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
  }

  // Extract team data from game data
  const team1Code = gameData?.away_team || 'TBD'
  const team2Code = gameData?.home_team || 'TBD'
  const team1Data = teamData[team1Code as keyof typeof teamData] || { name: 'Team 1', logo: '' }
  const team2Data = teamData[team2Code as keyof typeof teamData] || { name: 'Team 2', logo: '' }
  
  // Extract scores from game data
  const score1 = gameData?.away_score || 0
  const score2 = gameData?.home_score || 0
  const prevScore1 = score1 // You might want to calculate previous scores differently
  const prevScore2 = score2
  const score1Delta = score1 - prevScore1
  const score2Delta = score2 - prevScore2
  const team1Won = score1 > score2

  // Loading state
  if (loading) {
    return (
      <div className="game-page">
        <div className="loading-container">
          <div className="loading-spinner">Loading game data...</div>
        </div>
      </div>
    )
  }

  // Error state
  if (error) {
    return (
      <div className="game-page">
        <div className="error-container">
          <div className="error-message">{error}</div>
        </div>
      </div>
    )
  }

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
              <div className="big-game-city-name">{team1Data.name.split(' ')[0] || 'Team'}</div>
              <div 
                className="big-game-mascot-name" 
                style={{ 
                  opacity: team1Won ? '1' : '0.65',
                  color: team1Won ? '#000000' : '#666666'
                }}
              >
                {team1Data.name.split(' ').slice(1).join(' ') || '1'}
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
            <div className="big-game-week">Week {gameData?.week || 'TBD'}</div>
            <div className="big-game-date">{gameData ? nflApiService.formatGameDate(gameData) : 'Date TBD'}</div>
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
              <div className="big-game-city-name">{team2Data.name.split(' ')[0] || 'Team'}</div>
              <div 
                className="big-game-mascot-name" 
                style={{ 
                  opacity: team1Won ? '0.65' : '1',
                  color: team1Won ? '#666666' : '#000000'
                }}
              >
                {team2Data.name.split(' ').slice(1).join(' ') || '2'}
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

          {/* Right Column - New Content Area (40%) */}
          <div className="right-panel">
            <h3>Game Analysis</h3>
            <div className="analysis-content">
              {/* Summary Section */}
              <div className="analysis-section">
                <div className="input-container">
                  <h4>Summary:</h4>
                  <p className="summary-text">
                    Game analysis will be provided by Python backend.
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
                        <td>TBD</td>
                        <td>TBD</td>
                      </tr>
                      <tr>
                        <td>Simulated Avg Score</td>
                        <td>TBD</td>
                        <td>TBD</td>
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