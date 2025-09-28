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
  // New props for changeable events
  playIndex?: number
  playType?: string
  changeableAttributes?: any
  onSimulate?: (playIndex: number, changeableAttributes: any) => void
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
  onToggle,
  playIndex,
  playType,
  changeableAttributes: _changeableAttributes,
  onSimulate
}: GameEventProps) => {
  // Determine if this play is changeable based on play type
  const isChangeable = (playType: string) => {
    const changeableTypes = [
      'PASS', 'INTERCEPTION', 'RUSH', 'FIELD_GOAL', 'XP_KICK', 'PAT2', 'PUNT', 'PENALTY'
    ]
    return changeableTypes.includes(playType?.toUpperCase() || '')
  }

  // Get changeable options based on play type
  const getChangeableOptions = (playType: string) => {
    switch (playType?.toUpperCase()) {
      case 'PASS':
        return {
          type: 'dropdown',
          options: [
            { value: 'complete', label: '✅ Complete Pass', attributes: { is_complete: true, is_interception: false } },
            { value: 'incomplete', label: '❌ Incomplete Pass', attributes: { is_complete: false, is_interception: false } },
            { value: 'interception', label: '🏈 Interception', attributes: { is_complete: false, is_interception: true } },
            { value: 'fumble', label: '💥 Add Fumble', attributes: { is_fumble: true } }
          ]
        }
      case 'INTERCEPTION':
        return {
          type: 'dropdown',
          options: [
            { value: 'incomplete', label: '❌ Incomplete Pass', attributes: { is_complete: false, is_interception: false } },
            { value: 'complete', label: '✅ Complete Pass', attributes: { is_complete: true, is_interception: false } },
            { value: 'fumble', label: '💥 Fumble on Return', attributes: { is_fumble: true } }
          ]
        }
      case 'RUSH':
        return {
          type: 'dropdown',
          options: [
            { value: 'fumble', label: '💥 Add Fumble', attributes: { is_fumble: true } },
            { value: 'no_fumble', label: '🚫 Remove Fumble', attributes: { is_fumble: false } },
            { value: 'convert_3rd', label: '🏈 Convert 3rd Down', attributes: { convert_down: true } },
            { value: 'convert_4th', label: '🏈 Convert 4th Down', attributes: { convert_down: true } }
          ]
        }
      case 'FIELD_GOAL':
        return {
          type: 'toggle',
          options: [
            { value: 'good', label: '✅ Field Goal Good', attributes: { is_good: true } },
            { value: 'miss', label: '❌ Field Goal Miss', attributes: { is_good: false } }
          ]
        }
      case 'XP_KICK':
        return {
          type: 'dropdown',
          options: [
            { value: 'good', label: '✅ Extra Point Good', attributes: { is_good: true, is_one_point: true } },
            { value: 'miss', label: '❌ Extra Point Miss', attributes: { is_good: false, is_one_point: true } },
            { value: 'two_point', label: '🔄 Convert to 2-Point', attributes: { is_one_point: false } }
          ]
        }
      case 'PAT2':
        return {
          type: 'dropdown',
          options: [
            { value: 'good', label: '✅ 2-Point Good', attributes: { is_good: true, is_one_point: false } },
            { value: 'miss', label: '❌ 2-Point Miss', attributes: { is_good: false, is_one_point: false } },
            { value: 'extra_point', label: '🔄 Convert to Extra Point', attributes: { is_one_point: true } }
          ]
        }
      case 'PUNT':
        return {
          type: 'toggle',
          options: [
            { value: 'go_for_it', label: '🏈 Go For It', attributes: { punt_it: false } },
            { value: 'punt', label: '🏈 Punt', attributes: { punt_it: true } }
          ]
        }
      case 'PENALTY':
        return {
          type: 'toggle',
          options: [
            { value: 'remove', label: '🚫 Remove Penalty', attributes: { called: false } },
            { value: 'keep', label: '📏 Keep Penalty', attributes: { called: true } }
          ]
        }
      default:
        return null
    }
  }

  // Get status strings based on action type (legacy function for non-changeable events)
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

  // Determine if this play is changeable and get options
  const changeableOptions = getChangeableOptions(playType || '')
  const isPlayChangeable = isChangeable(playType || '')
  
  // Legacy dropdown check for non-changeable events
  const hasDropdown = action.toLowerCase() === 'pass' || action.toLowerCase() === 'conversion'
  const dropdownOptions = hasDropdown ? getStatusStrings(action).options : null

  // State management
  const [isToggled, setIsToggled] = useState(isFailure) // Start with failure state if isFailure is true
  const [dropdownValue, setDropdownValue] = useState(hasDropdown && dropdownOptions ? dropdownOptions[0] : '')
  const [initialDropdownValue] = useState(hasDropdown && dropdownOptions ? dropdownOptions[0] : '') // Store initial value
  const [isDropdownOpen, setIsDropdownOpen] = useState(false)
  
  // New state for changeable events
  const [selectedOption, setSelectedOption] = useState<string>('')
  const [isChangeableDropdownOpen, setIsChangeableDropdownOpen] = useState(false)

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

  // New handlers for changeable events
  const handleChangeableOptionSelect = (option: any) => {
    setSelectedOption(option.value)
    setIsChangeableDropdownOpen(false)
    
    // Trigger simulation if callback provided
    if (onSimulate && playIndex !== undefined) {
      onSimulate(playIndex, option.attributes)
    }
    
    // Also trigger the general toggle for card state management
    if (onToggle) {
      onToggle()
    }
  }

  const handleChangeableToggle = () => {
    if (changeableOptions && changeableOptions.type === 'toggle') {
      const currentOption = isToggled ? changeableOptions.options[1] : changeableOptions.options[0]
      setSelectedOption(currentOption.value)
      
      // Trigger simulation if callback provided
      if (onSimulate && playIndex !== undefined) {
        onSimulate(playIndex, currentOption.attributes)
      }
      
      // Also trigger the general toggle for card state management
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
    if (!isAffected) {
      if (isPlayChangeable && changeableOptions?.type === 'toggle') {
        handleChangeableToggle()
      } else if (!hasDropdown && !isPlayChangeable) {
        handleToggle()
      }
    }
  }

  const handleCardHover = () => {
    if (!isAffected && (hasDropdown || (isPlayChangeable && changeableOptions?.type === 'dropdown'))) {
      if (isPlayChangeable) {
        setIsChangeableDropdownOpen(true)
      } else {
        setIsDropdownOpen(true)
      }
    }
  }

  const handleCardLeave = () => {
    if (hasDropdown || isPlayChangeable) {
      setIsDropdownOpen(false)
      setIsChangeableDropdownOpen(false)
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
            {/* Render changeable event controls */}
            {isPlayChangeable ? (
              changeableOptions?.type === 'toggle' ? (
                <div className="toggle-container">
                  <div className={`event-action-type ${isToggled ? 'toggled' : ''}`}>
                    {isToggled ? changeableOptions.options[1].label : changeableOptions.options[0].label}
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
                  {selectedOption ? 
                    changeableOptions?.options.find(opt => opt.value === selectedOption)?.label || 'Select Option' :
                    'Select Option'
                  }
                  <span className={`dropdown-arrow ${isChangeableDropdownOpen ? 'open' : ''}`}>▼</span>
                </div>
              )
            ) : !hasDropdown ? (
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
      
      {/* Dropdown menu for legacy actions with options */}
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

      {/* Dropdown menu for changeable events */}
      {isPlayChangeable && changeableOptions?.type === 'dropdown' && isChangeableDropdownOpen && (
        <div className="dropdown-menu-container">
          <div className="dropdown-menu">
            {changeableOptions.options.map((option) => (
              <div 
                key={option.value}
                className={`dropdown-option ${selectedOption === option.value ? 'selected' : ''}`}
                onClick={() => handleChangeableOptionSelect(option)}
              >
                {option.label}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default GameEvent