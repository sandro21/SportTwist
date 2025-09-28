import React, { useState, useEffect, useRef } from 'react'
import './App.css'
import MinimizedGameCard from './components/MinimizedGameCard'

function App() {
  const [isSearchOverlayOpen, setIsSearchOverlayOpen] = useState(false)
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

  return (
    <div className="h-container">
      {/* Blur overlay */}
      {isSearchOverlayOpen && (
        <div className="search-blur-overlay" onClick={() => setIsSearchOverlayOpen(false)} />
      )}
      
      {/* Search overlay */}
      {isSearchOverlayOpen && (
        <div className="search-overlay">
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
              <div className="filter-button">
                <span>Season</span>
                <span className="filter-chevron">▼</span>
              </div>
              <div className="filter-button">
                <span>Team</span>
                <span className="filter-chevron">▼</span>
              </div>
              <div className="filter-button">
                <span>Player</span>
                <span className="filter-chevron">▼</span>
              </div>
              <div className="filter-button">
                <span>Game Type</span>
                <span className="filter-chevron">▼</span>
              </div>
            </div>
            <div className="search-overlay-results"></div>
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
        </div>
      </div>
    </div>
  )
}

export default App