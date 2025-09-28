import { useState } from 'react'

interface GameEventProps {
  team: string
  score: string
  action: string
  quarter: string
  timeRemaining: string
  description: string
  downAndDistance: string
  cardState: 'not-affected' | 'changed' | 'affected'
  isFailure?: boolean
  onToggle?: () => void
}

const GameEvent = ({ 
  team, 
  score, 
  action, 
  quarter, 
  timeRemaining, 
  description, 
  downAndDistance: _downAndDistance,
  cardState,
  isFailure = false,
  onToggle
}: GameEventProps) => {
  // Get status strings based on action type
  const getStatusStrings = (action: string) => {
    switch (action.toLowerCase()) {
      case 'penalty':
        return { worst: 'Penalty', best: 'No Penalty' }
      case 'pass':
        return { options: ['Completed Pass', 'Incomplete Pass', 'Intercepted Pass'] }
      case 'field goal':
        return { worst: 'Missed Field Goal', best: 'Field Goal' }
      case 'fourth down':
        return { worst: 'Punt', best: 'Go For It' }
      case 'conversion':
        return { options: ['2 Point Conversion', '1 Point Conversion', 'Failed Conversion'] }
      default:
        return { worst: 'Failed', best: 'Success' }
    }
  }

  // Check if action has dropdown options
  const hasDropdown = action.toLowerCase() === 'pass' || action.toLowerCase() === 'conversion'
  const dropdownOptions = hasDropdown ? getStatusStrings(action).options : null

  const [isToggled, setIsToggled] = useState(isFailure) // Start with failure state if isFailure is true
  const [dropdownValue, setDropdownValue] = useState(hasDropdown && dropdownOptions ? dropdownOptions[0] : '')
  const [initialDropdownValue] = useState(hasDropdown && dropdownOptions ? dropdownOptions[0] : '') // Store initial value
  const [isDropdownOpen, setIsDropdownOpen] = useState(false)

  const handleToggle = () => {
    setIsToggled(!isToggled)
    if (onToggle) {
      onToggle()
    }
  }

  const handleDropdownChange = (value: string) => {
    // Only trigger toggle if we're changing from initial value or back to initial value
    const isChangingFromInitial = dropdownValue === initialDropdownValue
    const isChangingToInitial = value === initialDropdownValue
    
    setDropdownValue(value)
    setIsDropdownOpen(false)
    
    // Only trigger onToggle if we're changing from initial or back to initial
    if ((isChangingFromInitial && !isChangingToInitial) || (!isChangingFromInitial && isChangingToInitial)) {
      if (onToggle) {
        onToggle()
      }
    }
  }


  // Determine if the card should show as active based on cardState
  const isActive = cardState === 'changed'
  const isAffected = cardState === 'affected'

  const statusStrings = getStatusStrings(action)

  // Get team logo based on team abbreviation
  const getTeamLogo = (team: string) => {
    const logos: { [key: string]: string } = {
      'PHI': 'https://upload.wikimedia.org/wikipedia/en/thumb/8/8e/Philadelphia_Eagles_logo.svg/200px-Philadelphia_Eagles_logo.svg.png',
      'DAL': 'https://upload.wikimedia.org/wikipedia/en/thumb/5/50/Dallas_Cowboys_logo.svg/200px-Dallas_Cowboys_logo.svg.png',
      'KC': 'https://upload.wikimedia.org/wikipedia/en/thumb/e/e1/Kansas_City_Chiefs_logo.svg/200px-Kansas_City_Chiefs_logo.svg.png',
      'BUF': 'https://upload.wikimedia.org/wikipedia/en/thumb/7/77/Buffalo_Bills_logo.svg/200px-Buffalo_Bills_logo.svg.png',
      'SF': 'https://upload.wikimedia.org/wikipedia/en/thumb/3/3a/San_Francisco_49ers_logo.svg/200px-San_Francisco_49ers_logo.svg.png',
      'GB': 'https://upload.wikimedia.org/wikipedia/en/thumb/5/50/Green_Bay_Packers_logo.svg/200px-Green_Bay_Packers_logo.svg.png',
      'NE': 'https://upload.wikimedia.org/wikipedia/en/thumb/b/b9/New_England_Patriots_logo.svg/200px-New_England_Patriots_logo.svg.png',
      'TB': 'https://upload.wikimedia.org/wikipedia/en/thumb/a/a2/Tampa_Bay_Buccaneers_logo.svg/200px-Tampa_Bay_Buccaneers_logo.svg.png'
    }
    return logos[team] || 'https://upload.wikimedia.org/wikipedia/en/thumb/7/72/Arizona_Cardinals_logo.svg/179px-Arizona_Cardinals_logo.svg.png'
  }

  const handleCardClick = () => {
    if (!isAffected && !hasDropdown) {
      handleToggle()
    }
  }

  const handleCardHover = () => {
    if (!isAffected && hasDropdown) {
      setIsDropdownOpen(true)
    }
  }

  const handleCardLeave = () => {
    if (hasDropdown) {
      setIsDropdownOpen(false)
    }
  }

  return (
    <div 
      className={`game-event ${isActive ? 'active' : ''} ${isAffected ? 'affected' : ''} ${!isAffected ? 'clickable' : ''}`}
      onClick={handleCardClick}
      onMouseEnter={handleCardHover}
      onMouseLeave={handleCardLeave}
    >
      <div className="game-event-content">
        <div className="game-event-left">
          <div className="game-event-top-left">
            <img src={getTeamLogo(team)} alt={team} className="event-team-logo" />
            <div className="event-team-name">{team}</div>
            {!hasDropdown ? (
              <div className="toggle-container">
                <div className={`event-action-type ${isToggled ? 'toggled' : ''}`}>
                  {isToggled ? statusStrings.worst : statusStrings.best}
                </div>
                <div 
                  className={`event-toggle-switch ${isToggled ? 'active' : ''}`}
                >
                  <div className="toggle-slider"></div>
                </div>
              </div>
            ) : (
              <div 
                className={`event-action-type dropdown-trigger ${isAffected ? 'disabled' : ''}`}
              >
                {dropdownValue}
                <span className={`dropdown-arrow ${isDropdownOpen ? 'open' : ''}`}>▼</span>
              </div>
            )}
          </div>
          <div className="game-event-bottom-left">
            <div className="event-action-desc">{description}</div>
          </div>
        </div>
        
        <div className="game-event-right">
          <div className="event-time">{quarter} {timeRemaining}</div>
          <div className="event-score">{score}</div>
        </div>
      </div>
      
      {/* Dropdown menu for actions with options */}
      {hasDropdown && dropdownOptions && isDropdownOpen && (
        <div className="dropdown-menu-container">
          <div className="dropdown-menu">
            {dropdownOptions.map((option) => (
              <div 
                key={option}
                className={`dropdown-option ${dropdownValue === option ? 'selected' : ''}`}
                onClick={() => handleDropdownChange(option)}
              >
                {option}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default GameEvent