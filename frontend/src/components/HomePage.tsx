import { useState } from 'react'

interface HomePageProps {
  onSearch: (query: string) => void
  isSearchOpen: boolean
  searchQuery: string
  onCloseSearch: () => void
  onGameSelect: (gameId: string) => void
}

const HomePage = ({ onSearch, isSearchOpen, searchQuery, onCloseSearch, onGameSelect }: HomePageProps) => {
  const [searchInput, setSearchInput] = useState('')

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (searchInput.trim()) {
      onSearch(searchInput.trim())
    }
  }

  return (
    <div className={isSearchOpen ? 'search-mode' : 'home-mode'}>
      {/* Background content - gets blurred when search is open */}
      <div className={isSearchOpen ? 'blurred-background' : ''}>
        <h1>SportTwist</h1>
        <form onSubmit={handleSearch}>
          <input 
            type="text" 
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder="Search for past games, teams, weeks, or dates..."
          />
          <button type="submit">Search</button>
        </form>
        
        {/* Trending games grid */}
        <div>
          {/* Your game cards here */}
        </div>
      </div>

      {/* Search overlay - appears when search is open */}
      {isSearchOpen && (
        <div className="search-overlay">
          <button onClick={onCloseSearch}>Close</button>
          <h2>Search Results for: {searchQuery}</h2>
          
          {/* Search filters */}
          <div>
            {/* Season, Team, Player, Game Type filters */}
          </div>
          
          {/* Search results */}
          <div>
            {/* Game results list */}
          </div>
        </div>
      )}
    </div>
  )
}

export default HomePage
