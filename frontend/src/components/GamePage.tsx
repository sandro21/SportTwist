import React from 'react'

interface GamePageProps {
  onBack: () => void
}

const GamePage = ({ onBack }: GamePageProps) => {
  return (
    <div>
      {/* Your game simulation HTML here */}
      <button onClick={onBack}>Back</button>
      <h2>Game Simulation</h2>
      
      {/* What-if controls */}
      <div>
        {/* Your simulation interface */}
      </div>
    </div>
  )
}

export default GamePage
