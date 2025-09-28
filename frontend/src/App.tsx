import React, { useState, useEffect, useRef } from 'react'
import './App.css'
import MinimizedGameCard from './components/MinimizedGameCard'
import SearchResultGameCard from './components/SearchResultGameCard'
import { nflApiService, type NFLGame } from './services/nflApi'
import GamePage from './components/GamePage'

function App() {
  const [isSearchOverlayOpen, setIsSearchOverlayOpen] = useState(false)
  const [activeDropdown, setActiveDropdown] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<NFLGame[]>([])
  const [popularGames, setPopularGames] = useState<NFLGame[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [selectedFilters, setSelectedFilters] = useState<{
    season?: string
    team?: string
    player?: string
    gameType?: string
  }>({})
  const [currentWeek, setCurrentWeek] = useState<number>(3) // Current week
  const [currentPage, setCurrentPage] = useState<'home' | 'game'>('home')
  const [selectedGame, setSelectedGame] = useState<NFLGame | null>(null)
  const searchInputRef = useRef<HTMLInputElement>(null)

  // Load latest games (6) on component mount
  useEffect(() => {
    const loadLatestGames = async () => {
      try {
        const games = await nflApiService.fetchGames()
        const latestSix = [...games]
          .sort((a, b) => new Date(b.gameday).getTime() - new Date(a.gameday).getTime())
          .slice(0, 6)
        setPopularGames(latestSix)
      } catch (error) {
        console.error('Failed to load latest games:', error)
      }
    }
    
    loadLatestGames()
  }, [])

  // Handle search with debouncing
  useEffect(() => {
    const performSearch = async () => {
      if (searchQuery.trim() === '') {
        setSearchResults([])
        return
      }

      setIsLoading(true)
      try {
        const results = await nflApiService.searchGames(searchQuery)
        setSearchResults(results)
      } catch (error) {
        console.error('Search failed:', error)
        setSearchResults([])
      } finally {
        setIsLoading(false)
      }
    }

    const timeoutId = setTimeout(performSearch, 300) // Debounce search
    return () => clearTimeout(timeoutId)
  }, [searchQuery])

  // Load latest games and set initial results
  useEffect(() => {
    const loadLatestGames = async () => {
      console.log('Loading latest games...')
      setIsLoading(true)
      try {
        const games = await nflApiService.fetchGames()
        const latestSix = [...games]
          .sort((a, b) => new Date(b.gameday).getTime() - new Date(a.gameday).getTime())
          .slice(0, 6)
        console.log('Loaded latest games:', latestSix.length)
        setPopularGames(latestSix)
        // Also set initial search results to recent games (top 10 from full list)
        if (games.length > 0) {
          const topTen = [...games]
            .sort((a, b) => new Date(b.gameday).getTime() - new Date(a.gameday).getTime())
            .slice(0, 10)
          setSearchResults(topTen)
        }
      } catch (error) {
        console.error('Failed to load latest games:', error)
      } finally {
        setIsLoading(false)
      }
    }
    
    loadLatestGames()
  }, [])

  // Handle search functionality
  useEffect(() => {
    const performSearch = async () => {
      if (!searchQuery.trim()) {
        // Reset to popular games when search is cleared
        setSearchResults(popularGames.slice(0, 10))
        return
      }

      setIsLoading(true)
      try {
        const results = await nflApiService.searchGames(searchQuery)
        setSearchResults(results)
      } catch (error) {
        console.error('Search failed:', error)
        setSearchResults([])
      } finally {
        setIsLoading(false)
      }
    }

    // Debounce search to avoid too many API calls
    const timeoutId = setTimeout(performSearch, 300)
    return () => clearTimeout(timeoutId)
  }, [searchQuery, popularGames])

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

  // Handle input change to keep overlay open while typing and perform search
  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value
    
    // Reset filters when user starts typing
    if (Object.keys(selectedFilters).length > 0) {
      resetFilters()
    }
    
    setSearchQuery(value)
    
    // Keep overlay open while typing
    if (value.length > 0) {
      setIsSearchOverlayOpen(true)
    }
  }

  // Handle dropdown toggle
  const toggleDropdown = (dropdownName: string) => {
    setActiveDropdown(activeDropdown === dropdownName ? null : dropdownName)
  }

  // Reset filters function
  const resetFilters = () => {
    setSelectedFilters({})
    setSearchQuery('')
  }

  // Handle filter selection
  const handleFilterSelect = (filterType: string, value: string) => {
    // Reset all other filters when a new one is selected
    setSelectedFilters({ [filterType]: value })
    setActiveDropdown(null) // Close dropdown after selection
    
    // Apply the filter based on type
    if (filterType === 'team') {
      setSearchQuery(value.toLowerCase())
    } else if (filterType === 'season') {
      // Handle season filter
      setSearchQuery(`season:${value}`)
    } else if (filterType === 'player') {
      // Handle player filter
      setSearchQuery(`player:${value}`)
    } else if (filterType === 'gameType') {
      // Handle game type filter
      setSearchQuery(`type:${value}`)
    }
  }

  // Handle trending search clicks
  const handleTrendingSearch = (searchType: string) => {
    resetFilters() // Reset any existing filters
    
    if (searchType === 'latest') {
      // Show the most recent game
      setSearchQuery('latest')
    } else if (searchType === 'currentWeek') {
      // Filter by current week
      setSelectedFilters({ season: `Week ${currentWeek}` })
      setSearchQuery(`week ${currentWeek}`)
    }
    
    setIsSearchOverlayOpen(true)
    setTimeout(() => searchInputRef.current?.focus(), 100)
  }

  // Dropdown data with real NFL teams
  const dropdownData = {
    season: ['2025/26', '2024/25', '2023/24', '2022/23', '2021/22', '2020/21', '2019/20', '2018/19', '2017/18'],
    team: ['Eagles', 'Cowboys', 'Chiefs', 'Bills', 'Packers', 'Vikings', 'Patriots', 'Dolphins', 'Steelers', 'Ravens', '49ers', 'Seahawks', 'Rams', 'Cardinals', 'Saints', 'Falcons'],
    player: ['Mahomes', 'Allen', 'Rodgers', 'Jackson', 'Prescott', 'Herbert', 'Burrow', 'Tua'],
    gameType: ['Regular', 'Playoffs']
  }

  // Handle game selection and navigation
  const handleGameSelect = (game: NFLGame) => {
    setSelectedGame(game)
    setCurrentPage('game')
  }

  // Demo navigation
  if (currentPage === 'game') {
    return (
      <div>
        <button 
          onClick={() => {
            setCurrentPage('home')
            setSelectedGame(null)
          }}
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
        <GamePage game={selectedGame} />
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
              <div className={`filter-button ${activeDropdown === 'season' ? 'active' : ''} ${selectedFilters.season ? 'selected' : ''}`} onClick={() => toggleDropdown('season')}>
                <span>{selectedFilters.season || 'Season'}</span>
                <span className="filter-chevron">▼</span>
                {activeDropdown === 'season' && (
                  <div className="dropdown-menu">
                    {dropdownData.season.map((item, index) => (
                      <div key={index} className="dropdown-item" onClick={() => handleFilterSelect('season', item)}>{item}</div>
                    ))}
                  </div>
                )}
              </div>
              <div className={`filter-button ${activeDropdown === 'team' ? 'active' : ''} ${selectedFilters.team ? 'selected' : ''}`} onClick={() => toggleDropdown('team')}>
                <span>{selectedFilters.team || 'Team'}</span>
                <span className="filter-chevron">▼</span>
                {activeDropdown === 'team' && (
                  <div className="dropdown-menu">
                    {dropdownData.team.map((item, index) => (
                      <div key={index} className="dropdown-item" onClick={() => handleFilterSelect('team', item)}>{item}</div>
                    ))}
                  </div>
                )}
              </div>
              <div className={`filter-button ${activeDropdown === 'player' ? 'active' : ''} ${selectedFilters.player ? 'selected' : ''}`} onClick={() => toggleDropdown('player')}>
                <span>{selectedFilters.player || 'Player'}</span>
                <span className="filter-chevron">▼</span>
                {activeDropdown === 'player' && (
                  <div className="dropdown-menu">
                    {dropdownData.player.map((item, index) => (
                      <div key={index} className="dropdown-item" onClick={() => handleFilterSelect('player', item)}>{item}</div>
                    ))}
                  </div>
                )}
              </div>
              <div className={`filter-button ${activeDropdown === 'gameType' ? 'active' : ''} ${selectedFilters.gameType ? 'selected' : ''}`} onClick={() => toggleDropdown('gameType')}>
                <span>{selectedFilters.gameType || 'Game Type'}</span>
                <span className="filter-chevron">▼</span>
                {activeDropdown === 'gameType' && (
                  <div className="dropdown-menu">
                    {dropdownData.gameType.map((item, index) => (
                      <div key={index} className="dropdown-item" onClick={() => handleFilterSelect('gameType', item)}>{item}</div>
                    ))}
                  </div>
                )}
              </div>
            </div>
            <div className="search-overlay-results">
              {isLoading && (
                <div className="search-loading">Searching...</div>
              )}
              
              {!isLoading && searchQuery && searchResults.length === 0 && (
                <div className="search-no-results">No games found for "{searchQuery}"</div>
              )}

              {/* Always show Recent Games header and results */}
              {!isLoading && (
                <>
                  <div className="season-indicator">Recent Games</div>
                  <div className="search-results-container">
                    {(searchQuery ? searchResults : searchResults)
                      .sort((a, b) => {
                        // Sort by actual game date (most recent first)
                        const dateA = new Date(a.gameday);
                        const dateB = new Date(b.gameday);
                        return dateB.getTime() - dateA.getTime(); // Most recent date first
                      })
                      .map(game => (
                        <SearchResultGameCard 
                          key={game.game_id} 
                          game={game}
                          onClick={() => handleGameSelect(game)}
                        />
                      ))}
                  </div>
                </>
              )}
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
              <div 
                className="h-trending-tag" 
                onClick={() => {
                  resetFilters() // Reset any existing filters
                  setSearchQuery('latest')
                  setIsSearchOverlayOpen(true)
                  setTimeout(() => searchInputRef.current?.focus(), 100)
                }}
                style={{ cursor: 'pointer' }}
              >
                {popularGames.length > 0 
                  ? `${popularGames[0].away_team} vs ${popularGames[0].home_team}`
                  : 'Eagles vs Cowboys'
                }
              </div>
              <div 
                className="h-trending-tag"
                onClick={() => handleTrendingSearch('currentWeek')}
                style={{ cursor: 'pointer' }}
              >
                Week {currentWeek}
              </div>
            </div>
          </div>
        </div>
        <div className="h-popular-container">
          <p className="h-popular-text">Popular Searches:</p>
          <div className="h-game-cards">
            {popularGames.length > 0 ? (
              popularGames
                .sort((a, b) => {
                  // Sort by actual game date (most recent first)
                  const dateA = new Date(a.gameday);
                  const dateB = new Date(b.gameday);
                  return dateB.getTime() - dateA.getTime(); // Most recent date first
                })
                .map(game => (
                  <MinimizedGameCard 
                    key={game.game_id} 
                    game={game}
                    onClick={() => handleGameSelect(game)}
                  />
                ))
            ) : null}
          </div>
        </div>
      </div>
    </div>
  )
}

export default App