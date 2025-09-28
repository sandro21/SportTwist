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
  changeableAttributes?: any // The changeable_attributes from backend
  onToggle?: () => void
  onPlayChange?: (newAttributes: any) => void // Callback for when play changes
  playIndex?: number // Index of this play
  disabled?: boolean // Disable interactions during simulation
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
  changeableAttributes,
  onToggle,
  onPlayChange,
  playIndex,
  disabled = false
}: GameEventProps) => {
  // Get options based on changeable_attributes from backend
  const getOptionsFromAttributes = (attrs: any) => {
    if (!attrs) {
      return { hasOptions: false, isToggleable: false }
    }

    // Handle pass plays
    if (attrs.is_complete !== undefined || attrs.is_interception !== undefined) {
      if (attrs.is_interception !== undefined) {
        return {
          hasOptions: true,
          isToggleable: false,
          options: ['Complete', 'Incomplete', 'Interception'],
          currentValue: attrs.is_interception ? 'Interception' : (attrs.is_complete ? 'Complete' : 'Incomplete')
        }
      } else {
        return {
          hasOptions: false,
          isToggleable: true,
          successState: 'Complete',
          failureState: 'Incomplete',
          currentState: attrs.is_complete ? 'success' : 'failure'
        }
      }
    }

    // Handle penalties
    if (attrs.called !== undefined) {
      return {
        hasOptions: false,
        isToggleable: true,
        successState: 'No Penalty',
        failureState: 'Penalty',
        currentState: attrs.called ? 'failure' : 'success'
      }
    }

    // Handle other boolean attributes
    const booleanAttrs = Object.keys(attrs).filter(key => typeof attrs[key] === 'boolean')
    if (booleanAttrs.length > 0) {
      const key = booleanAttrs[0]
      return {
        hasOptions: false,
        isToggleable: true,
        successState: 'Success',
        failureState: 'Failure',
        currentState: attrs[key] ? 'success' : 'failure'
      }
    }

    return { hasOptions: false, isToggleable: false }
  }

  const playOptions = getOptionsFromAttributes(changeableAttributes)
  const hasDropdown = playOptions.hasOptions
  const dropdownOptions = playOptions.options || null

  const [isToggled, setIsToggled] = useState(
    playOptions.isToggleable ? playOptions.currentState === 'failure' : false
  )
  const [dropdownValue, setDropdownValue] = useState(
    hasDropdown && playOptions.currentValue ? playOptions.currentValue : (dropdownOptions ? dropdownOptions[0] : '')
  )
  const [initialDropdownValue] = useState(
    hasDropdown && playOptions.currentValue ? playOptions.currentValue : (dropdownOptions ? dropdownOptions[0] : '')
  )
  const [isDropdownOpen, setIsDropdownOpen] = useState(false)

  const handleToggle = () => {
    const newToggleState = !isToggled
    setIsToggled(newToggleState)
    
    if (onToggle) {
      onToggle()
    }
    
    // Trigger simulation with updated changeable attributes
    if (onPlayChange && changeableAttributes) {
      const newAttributes = { ...changeableAttributes } // Start with complete original attributes
      
      // Update the appropriate attribute based on play type
      if (changeableAttributes.is_complete !== undefined) {
        newAttributes.is_complete = !newToggleState // Success = complete, failure = incomplete
      } else if (changeableAttributes.called !== undefined) {
        newAttributes.called = newToggleState // Toggled on = penalty called
      } else {
        // For other boolean attributes, flip the value
        const booleanKeys = Object.keys(changeableAttributes).filter(key => 
          typeof changeableAttributes[key] === 'boolean'
        )
        if (booleanKeys.length > 0) {
          newAttributes[booleanKeys[0]] = newToggleState
        }
      }
      
      console.log('Sending complete changeable attributes:', newAttributes)
      onPlayChange(newAttributes)
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
    
    // Trigger simulation with updated changeable attributes
    if (onPlayChange && changeableAttributes) {
      const newAttributes = { ...changeableAttributes } // Start with complete original attributes
      
      // Update pass completion/interception attributes
      if (changeableAttributes.is_complete !== undefined || changeableAttributes.is_interception !== undefined) {
        if (value === 'Complete') {
          newAttributes.is_complete = true
          newAttributes.is_interception = false
        } else if (value === 'Incomplete') {
          newAttributes.is_complete = false
          newAttributes.is_interception = false
        } else if (value === 'Interception') {
          newAttributes.is_complete = false
          newAttributes.is_interception = true
        }
      }
      
      console.log('Sending complete changeable attributes:', newAttributes)
      onPlayChange(newAttributes)
    }
  }


  // Determine if the card should show as active based on cardState
  const isActive = cardState === 'changed'
  const isAffected = cardState === 'affected'

  // Get status strings based on play options
  const statusStrings = playOptions.isToggleable 
    ? { worst: playOptions.failureState, best: playOptions.successState }
    : { worst: 'Failure', best: 'Success' }

  // Complete team data from team_logos_dict.py
  const teamData: { [key: string]: { name: string, logo: string } } = {
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

  // Get team logo based on team abbreviation
  const getTeamLogo = (team: string) => {
    const teamInfo = teamData[team as keyof typeof teamData]
    return teamInfo ? teamInfo.logo : teamData['ARI'].logo // Fallback to Cardinals logo
  }

  const handleCardClick = () => {
    if (!disabled && !isAffected && playOptions.isToggleable && !playOptions.hasOptions) {
      handleToggle()
    }
  }

  const handleCardHover = () => {
    if (!disabled && !isAffected && playOptions.hasOptions) {
      setIsDropdownOpen(true)
    }
  }

  const handleCardLeave = () => {
    if (playOptions.hasOptions) {
      setIsDropdownOpen(false)
    }
  }

  return (
    <div 
      className={`game-event ${isActive ? 'active' : ''} ${isAffected ? 'affected' : ''} ${!disabled && !isAffected && (playOptions.isToggleable || playOptions.hasOptions) ? 'clickable' : ''} ${disabled ? 'disabled' : ''}`}
      onClick={handleCardClick}
      onMouseEnter={handleCardHover}
      onMouseLeave={handleCardLeave}
    >
      <div className="game-event-content">
        <div className="game-event-left">
          <div className="game-event-top-left">
            <img src={getTeamLogo(team)} alt={team} className="event-team-logo" />
            <div className="event-team-name">{team}</div>
            {!playOptions.hasOptions && playOptions.isToggleable ? (
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
            ) : playOptions.hasOptions ? (
              <div 
                className={`event-action-type dropdown-trigger ${isAffected ? 'disabled' : ''}`}
              >
                {dropdownValue}
                <span className={`dropdown-arrow ${isDropdownOpen ? 'open' : ''}`}>▼</span>
              </div>
            ) : (
              <div className="event-action-type">
                {action}
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
      {playOptions.hasOptions && dropdownOptions && isDropdownOpen && (
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