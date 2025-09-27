import React from 'react'

interface MinimizedGameCardProps {
  teams: string
  date: string
  onClick?: () => void
}

function MinimizedGameCard({ teams, date, onClick }: MinimizedGameCardProps) {
  return (
    <div 
      className="h-game-card" 
      onClick={onClick}
      style={{
        backgroundColor: '#FFFFFF',
        border: '3px solid #F2DFFF',
        borderRadius: '20px',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
        <div className="h-team-card" style={{ display: 'flex', flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' }}>
            <div className="h-team-image"></div>
            <div className="h-team-name">Eagles</div>
            <div className="h-team-score">28</div>
        </div>
        <div className="h-team-card" style={{ display: 'flex', flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' }}>
            <div className="h-team-image"></div>
            <div className="h-team-name">Cowboys</div>
            <div className="h-team-score">24</div>
        </div>
        <div className="h-date">Week 3 • Oct 15, 2023</div>

    </div>
  )
}

export default MinimizedGameCard
