import { useState } from 'react'
import './App.css'

// Import your components
import HomePage from './components/HomePage.tsx'
import GamePage from './components/GamePage.tsx'

type Page = 'home' | 'game'

function App() {
  const [currentPage, setCurrentPage] = useState<Page>('home')
  const [isSearchOpen, setIsSearchOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')

  const handleSearch = (query: string) => {
    setSearchQuery(query)
    setIsSearchOpen(true)
  }

  const handleGameSelect = () => {
    setCurrentPage('game')
  }

  const handleCloseSearch = () => {
    setIsSearchOpen(false)
    setSearchQuery('')
  }

  return (
    <div>
      {currentPage === 'home' && (
        <HomePage 
          onSearch={handleSearch}
          isSearchOpen={isSearchOpen}
          searchQuery={searchQuery}
          onCloseSearch={handleCloseSearch}
          onGameSelect={handleGameSelect}
        />
      )}
      {currentPage === 'game' && (
        <GamePage onBack={() => setCurrentPage('home')} />
      )}
    </div>
  )
}

export default App
