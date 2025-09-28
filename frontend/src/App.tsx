import React, { useState, useEffect, useRef } from 'react'
import './App.css'
import MinimizedGameCard from './components/MinimizedGameCard'
import SearchResultGameCard from './components/SearchResultGameCard'
import GamePage from './components/GamePage'

function App() {
  const [isSearchOverlayOpen, setIsSearchOverlayOpen] = useState(false)
  const [activeDropdown, setActiveDropdown] = useState<string | null>(null)
  const [currentPage, setCurrentPage] = useState<'home' | 'game'>('home')
  const searchInputRef = useRef<HTMLInputElement>(null)

  // Handle keyboard events
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Open search overlay when '/' is pressed
      if (event.key === '/' && !isSearchOverlayOpen) {
        event.preventDefault()
        setIsSearchOverlayOpen(true)
        // Clear the home page input and focus the overlay input
        setTimeout(() => {
          const homeInput = document.querySelector('.h-search-bar input') as HTMLInputElement
          if (homeInput) {
            homeInput.value = ''
            homeInput.blur()
          }
          searchInputRef.current?.focus()
        }, 100)
      }
      
      // Close search overlay when Escape is pressed
      if (event.key === 'Escape' && isSearchOverlayOpen) {
        setIsSearchOverlayOpen(false)
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isSearchOverlayOpen])

  // Handle input focus to open overlay
  const handleInputFocus = () => {
    setIsSearchOverlayOpen(true)
    // Clear the home page input and focus the overlay input
    setTimeout(() => {
      const homeInput = document.querySelector('.h-search-bar input') as HTMLInputElement
      if (homeInput) {
        homeInput.value = ''
        homeInput.blur()
      }
      searchInputRef.current?.focus()
    }, 100)
  }

  // Handle input change to keep overlay open while typing
  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    // Keep overlay open while typing
    if (event.target.value.length > 0) {
      setIsSearchOverlayOpen(true)
    }
  }

  // Handle dropdown toggle
  const toggleDropdown = (dropdownName: string) => {
    setActiveDropdown(activeDropdown === dropdownName ? null : dropdownName)
  }

  // Sample dropdown data
  const dropdownData = {
    season: ['2024/25', '2023/24', '2022/23', '2021/22'],
    team: ['Eagles', 'Cowboys', 'Chiefs', 'Bills', 'Packers', 'Vikings'],
    player: ['Mahomes', 'Allen', 'Rodgers', 'Brady', 'Prescott'],
    gameType: ['Regular Season', 'Playoffs', 'Super Bowl', 'Preseason']
  }

  // Demo navigation
  if (currentPage === 'game') {
    return (
      <div>
        <button 
          onClick={() => setCurrentPage('home')}
          style={{
            position: 'fixed',
            top: '20px',
            left: '20px',
            zIndex: 1000,
            padding: '10px 20px',
            background: 'rgba(255, 255, 255, 0.9)',
            border: '2px solid #8000FF',
            borderRadius: '25px',
            fontFamily: 'GT Standard',
            fontSize: '16px',
            fontWeight: '600',
            color: '#8000FF',
            cursor: 'pointer',
            backdropFilter: 'blur(10px)'
          }}
        >
          ← Back to Home
        </button>
        <GamePage />
      </div>
    )
  }

  return (
    <div className="h-container">
      {/* Blur overlay */}
      {isSearchOverlayOpen && (
        <div className="search-blur-overlay" onClick={() => setIsSearchOverlayOpen(false)} />
      )}
      
      {/* Search overlay */}
      {isSearchOverlayOpen && (
        <div className="search-overlay">
          <button 
            className="search-overlay-close-btn"
            onClick={() => setIsSearchOverlayOpen(false)}
            title="Close search (ESC)"
          >
            ESC
          </button>
          <div className="search-overlay-content">
            <div className="search-overlay-search">
              <img src="/search.png" alt="Search" className="h-search-icon" />
              <input 
                ref={searchInputRef}
                type="text" 
                placeholder="Search for past games, teams, weeks, or dates..." 
                onFocus={handleInputFocus}
                onChange={handleInputChange}
              />
            </div>
            <div className="search-overlay-filter">
              <div className={`filter-button ${activeDropdown === 'season' ? 'active' : ''}`} onClick={() => toggleDropdown('season')}>
                <span>Season</span>
                <span className="filter-chevron">▼</span>
                {activeDropdown === 'season' && (
                  <div className="dropdown-menu">
                    {dropdownData.season.map((item, index) => (
                      <div key={index} className="dropdown-item">{item}</div>
                    ))}
                  </div>
                )}
              </div>
              <div className={`filter-button ${activeDropdown === 'team' ? 'active' : ''}`} onClick={() => toggleDropdown('team')}>
                <span>Team</span>
                <span className="filter-chevron">▼</span>
                {activeDropdown === 'team' && (
                  <div className="dropdown-menu">
                    {dropdownData.team.map((item, index) => (
                      <div key={index} className="dropdown-item">{item}</div>
                    ))}
                  </div>
                )}
              </div>
              <div className={`filter-button ${activeDropdown === 'player' ? 'active' : ''}`} onClick={() => toggleDropdown('player')}>
                <span>Player</span>
                <span className="filter-chevron">▼</span>
                {activeDropdown === 'player' && (
                  <div className="dropdown-menu">
                    {dropdownData.player.map((item, index) => (
                      <div key={index} className="dropdown-item">{item}</div>
                    ))}
                  </div>
                )}
              </div>
              <div className={`filter-button ${activeDropdown === 'gameType' ? 'active' : ''}`} onClick={() => toggleDropdown('gameType')}>
                <span>Game Type</span>
                <span className="filter-chevron">▼</span>
                {activeDropdown === 'gameType' && (
                  <div className="dropdown-menu">
                    {dropdownData.gameType.map((item, index) => (
                      <div key={index} className="dropdown-item">{item}</div>
                    ))}
                  </div>
                )}
              </div>
            </div>
            <div className="search-overlay-results">
              <div className="season-indicator">2024/25</div>
              <SearchResultGameCard teams="PHI vs DAL" date="Week 3" />
              <SearchResultGameCard teams="KC vs BUF" date="Week 5" />
              <SearchResultGameCard teams="GB vs MIN" date="Week 6" />
              <SearchResultGameCard teams="NE vs MIA" date="Week 7" />
              
              <div className="season-indicator">2022/23</div>
              <SearchResultGameCard teams="PIT vs BAL" date="Week 8" />
              <SearchResultGameCard teams="SF vs SEA" date="Week 9" />
            </div>
          </div>
        </div>
      )}

      <div className={`h-scale-wrapper ${isSearchOverlayOpen ? 'blurred' : ''}`}>
        <div className="h-header">
          <h1>Sport<span className="h-header-twist">Twist</span></h1>
          <h2>Change a <span className="h-header-highlight">play</span>. See the alternate <span className="h-header-highlight">outcome</span>.</h2>
        </div>
        <div className="h-search">
          <div className="h-search-border">
            <div className="h-search-bar">
              <img src="/search.png" alt="Search" className="h-search-icon" />
              <input 
                ref={searchInputRef}
                type="text" 
                placeholder="Search for past games, teams, weeks, or dates..." 
                onFocus={handleInputFocus}
                onChange={handleInputChange}
              />
              <span className="h-search-slash">/</span>
            </div>
          </div>
          <div className="h-trending-container">
            <p className="h-trending-text">Trending Searches:</p>
            <div className="h-trending-labels">
              <div className="h-trending-tag">Eagles vs Cowboys</div>
              <div className="h-trending-tag">Week 3</div>
            </div>
          </div>
        </div>
        <div className="h-popular-container">
          <p className="h-popular-text">Popular Searches:</p>
          <div className="h-game-cards">
            <MinimizedGameCard teams="PHI vs DAL" date="Week 3" />
            <MinimizedGameCard teams="KC vs BUF" date="Week 5" />
            <MinimizedGameCard teams="GB vs MIN" date="Week 6" />
            <MinimizedGameCard teams="NE vs MIA" date="Week 7" />
            <MinimizedGameCard teams="PIT vs BAL" date="Week 8" />
            <MinimizedGameCard teams="SF vs SEA" date="Week 9" />
          </div>
          
          {/* Demo Button */}
          <div style={{ textAlign: 'center', marginTop: '2rem' }}>
            <button 
              onClick={() => setCurrentPage('game')}
              style={{
                padding: '15px 30px',
                background: 'linear-gradient(90deg, #8000FF 0%, #A000FF 100%)',
                border: 'none',
                borderRadius: '30px',
                fontFamily: 'GT Standard',
                fontSize: '18px',
                fontWeight: '600',
                color: 'white',
                cursor: 'pointer',
                boxShadow: '0 4px 15px rgba(128, 0, 255, 0.3)',
                transition: 'all 0.2s ease'
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.transform = 'scale(1.05)'
                e.currentTarget.style.boxShadow = '0 6px 20px rgba(128, 0, 255, 0.4)'
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.transform = 'scale(1)'
                e.currentTarget.style.boxShadow = '0 4px 15px rgba(128, 0, 255, 0.3)'
              }}
            >
              Demo Game Page →
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App