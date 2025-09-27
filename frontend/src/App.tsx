import React from 'react'
import './App.css'
import MinimizedGameCard from './components/MinimizedGameCard'

function App() {
  return (
    <div className="h-container">
      <div className="h-scale-wrapper">
        <div className="h-header">
          <h1>Sport<span className="h-header-twist">Twist</span></h1>
          <h2>Change a <span className="h-header-highlight">play</span>. See the alternate <span className="h-header-highlight">outcome</span>.</h2>
        </div>
        <div className="h-search">
          <div className="h-search-border">
            <div className="h-search-bar">
              <img src="/search.png" alt="Search" className="h-search-icon" />
              <input type="text" placeholder="Search for past games, teams, weeks, or dates..." />
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