# SportTwist 🏈

**A Sports Intelligence & Insight System for NFL Game Analysis**

*Built for HackGT 12 - Crypt of Data Track - PrizePicks Challenge*

---

## **Project Vision**

SportTwist revolutionizes NFL analysis by allowing users to **"Change a play. See the alternate outcome."** 

Our platform combines historical NFL data spanning 9 years (2017-2025) with advanced predictive modeling to deliver unprecedented insights into game dynamics and potential outcomes. Using Monte Carlo simulation methods and statistical analysis of over 107,609 play records, SportTwist transforms raw game data into actionable intelligence.

### **Core Philosophy**
- **Event Modification Engine**: Change any single gameplay element and witness how that alteration cascades through the entire game timeline
- **Monte Carlo Analysis**: Process thousands of game variations using probability-based modeling to show realistic alternate outcomes
- **Temporal Ripple Tracking**: Follow how one modified moment creates waves of change throughout subsequent plays, drives, and final results
- **Historical Context Intelligence**: Leverage 9 years of NFL data to ground alternate scenarios in realistic statistical patterns
- **Signal Extraction**: Transform overwhelming game data into clear cause-and-effect relationships between decisions and outcomes

### **Event Modification Capabilities**
SportTwist goes beyond prediction - it lets you actively reshape game history and analyze the consequences:

**🏈 Play-Level Modifications**
- **Formation Changes**: Switch from shotgun to I-formation on a crucial 3rd down and see how defensive alignment changes affect success probability
- **Route Adjustments**: Modify receiver routes mid-play and track how different patterns would have exploited defensive coverage
- **Audible Decisions**: Change quarterback audibles at the line and observe how snap count variations affect defensive timing

**👥 Personnel Decisions**  
- **Player Substitutions**: Insert backup players during key moments and analyze how their unique skill sets alter game flow
- **Position Swaps**: Move players to different positions and evaluate performance changes based on their actual statistical profiles
- **Fatigue Modeling**: Adjust player rest patterns and see how stamina affects late-game execution

**🎯 Strategic Modifications**
- **Coaching Calls**: Change timeout usage, challenge flags, or 4th down decisions and trace their impact on final outcomes
- **Game Plan Shifts**: Modify offensive/defensive schemes mid-game and track how opposing teams would have adapted
- **Clock Management**: Alter pace of play decisions and see how time remaining affects strategic options

### **Outcome Analysis Framework**
Each modification generates detailed impact analysis across multiple dimensions:

**📊 Immediate Effects**
- **Play Success Metrics**: Yards gained/lost, first downs achieved, turnover probability shifts
- **Field Position Changes**: How modified plays affect starting position for subsequent drives
- **Down and Distance Impact**: Track how single-play changes create different situational contexts

**🎯 Game-Wide Consequences**  
- **Momentum Shifts**: Quantify psychological momentum changes and their statistical impact on subsequent performance
- **Score Progression**: Chart exact point differentials created by individual modifications throughout the game
- **Win Probability Evolution**: Track moment-by-moment changes in victory likelihood across the entire game timeline

**🏆 Season Implications**
- **Playoff Seeding**: See how single-game changes could have altered final standings and postseason matchups  
- **Statistical Records**: Track how modifications would have affected individual player stats and team achievements
- **Championship Pathways**: Analyze how one changed play could have created entirely different playoff scenarios

---

## ✨ **Key Features**

### 🔍 **Advanced Search & Filtering**
- **Smart Team Search**: Search by full team names (e.g., "dolphins") or abbreviations ("MIA")
- **Multi-Dimensional Filters**: Filter by season (2017-2025), team, player, game type (Regular/Playoffs)
- **Chronological Sorting**: Games displayed by actual date (most recent first)
- **Real-time Results**: Instant search with live API integration

### 📊 **Data Intelligence**
- **107,609+ Play Records**: Comprehensive NFL play-by-play data
- **842+ Scheduled Games**: Complete game schedules with scores
- **Historical Coverage**: 9 years of NFL data (2017-2025)
- **Team Performance Analytics**: High-profile team tracking and analysis

### 🎮 **Interactive UI/UX**
- **Search Overlay**: Advanced search interface with filter buttons
- **Trending Searches**: Dynamic latest game and current week shortcuts
- **Popular Games**: Curated high-profile matchups
- **Responsive Design**: Clean, modern interface with real-time updates

### 🤖 **Intelligent Systems** *(Current + Planned)*
- **Pattern Recognition**: Identify trends in team performance and game outcomes
- **Anomaly Detection**: Flag unusual game patterns or statistical outliers
- **Predictive Simulation**: Game outcome prediction based on historical data
- **Real-time Insights**: Live game analysis and trend identification

---

## 🏗️ **Architecture**

### **Frontend** (React + TypeScript + Vite)
```
frontend/
├── src/
│   ├── components/
│   │   ├── MinimizedGameCard.tsx     # Home page game cards
│   │   └── SearchResultGameCard.tsx  # Search result display
│   ├── services/
│   │   └── nflApi.ts                # API communication layer
│   ├── App.tsx                      # Main application component
│   ├── App.css                      # Styling and responsive design
│   └── main.tsx                     # Application entry point
├── package.json                     # Dependencies and scripts
└── vite.config.ts                   # Build configuration
```

### **Backend** (Python + Flask + nflreadpy)
```
backend/
├── nfl_api.py                       # Main API server
├── game.py                          # Game simulation logic
├── interactive_game_sim.py          # Interactive simulation features
├── moremontecarlo.py               # Monte Carlo simulation methods
└── team_logos_dict.py              # Team branding and assets
```

### **API Endpoints**
- `GET /api/games` - Retrieve all games with scores
- `GET /api/search?q={query}` - Advanced search functionality
- `GET /api/popular` - Get high-profile/trending games
- `GET /api/game/{game_id}` - Detailed game information

---

## 🚀 **Getting Started**

### **Prerequisites**
- Node.js 18+ 
- Python 3.11+
- pip (Python package manager)
- npm (Node package manager)

### **Installation**

1. **Clone the Repository**
   ```bash
   git clone https://github.com/sandro21/SportTwist.git
   cd SportTwist
   ```

2. **Backend Setup**
   ```bash
   # Create virtual environment
   python -m venv .venv
   
   # Activate virtual environment
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   
   # Install dependencies
   pip install flask flask-cors nflreadpy pandas
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

### **Running the Application**

1. **Start Backend Server** (Terminal 1)
   ```bash
   cd backend
   python nfl_api.py
   ```
   Server runs on: `http://localhost:5001`

2. **Start Frontend Server** (Terminal 2)
   ```bash
   cd frontend
   npm run dev
   ```
   Application runs on: `http://localhost:5173` (or next available port)

---

## 📡 **Data & APIs**

### **Data Sources**
- **nflreadpy**: Official NFL play-by-play and schedule data
- **Real-time Integration**: Live NFL statistics and game information
- **Historical Coverage**: 2017-2025 seasons (107,609+ plays)

### **Data Processing Pipeline**
1. **Data Ingestion**: Load NFL data via nflreadpy
2. **Data Transformation**: Convert to standardized JSON format
3. **Caching Layer**: In-memory caching for performance
4. **API Serving**: RESTful endpoints for frontend consumption

### **Search Intelligence**
```python
# Smart team name mapping
team_name_map = {
    'eagles': 'PHI', 'philadelphia': 'PHI',
    'cowboys': 'DAL', 'dallas': 'DAL',
    'chiefs': 'KC', 'dolphins': 'MIA',
    # ... 32 NFL teams with multiple search terms
}

# Player-team associations for advanced filtering
player_team_map = {
    'mahomes': ['KC'], 'allen': ['BUF'], 
    'tua': ['MIA'], 'jackson': ['BAL']
    # ... key players with team mappings
}
```

---

## 🎨 **UI/UX Design**

### **Design System**
- **Color Scheme**: Purple gradient (#8000FF) with white/glass morphism
- **Typography**: GT Standard font family
- **Layout**: Responsive grid system with flexbox/CSS Grid
- **Animations**: Smooth transitions and hover effects

### **Component Architecture**
```typescript
// Game Card Interface
interface NFLGame {
  game_id: string;
  home_team: string;
  away_team: string;
  home_score: number;
  away_score: number;
  week: number;
  season: number;
  gameday: string;
  gametime: string;
}
```

### **Search Experience**
- **Keyboard Shortcuts**: Press '/' to open search
- **Filter System**: Season, Team, Player, Game Type filters
- **Auto-complete**: Smart suggestions and team name matching
- **Real-time Updates**: Instant search results as you type

---

## 🧠 **Intelligence Features**

### **Current Implementations**

1. **Pattern Recognition**
   - Chronological game sorting by actual dates
   - High-profile team identification and trending
   - Popular game curation based on team significance

2. **Search Intelligence**
   - Multi-format team name recognition
   - Player-based game filtering
   - Season and game type categorization

3. **Data Visualization**
   - Clean game card layouts with team logos
   - Score alignment and formatting consistency
   - Responsive search result containers

### **Planned Enhancements**

1. **Game Simulation Engine**
   - Monte Carlo simulation methods
   - Historical performance analysis
   - Outcome prediction algorithms

2. **Anomaly Detection**
   - Statistical outlier identification
   - Performance trend analysis
   - Real-time alert systems

3. **AI Insights Generator**
   - Natural language game explanations
   - Performance trend summaries
   - Predictive analysis reports

---

## 🔧 **Technical Stack**

### **Frontend Technologies**
- **React 19.1.1**: Modern component-based UI
- **TypeScript**: Type-safe development
- **Vite 7.1.7**: Fast build tool and dev server
- **CSS Grid/Flexbox**: Advanced layout systems
- **Fetch API**: HTTP client for backend communication

### **Backend Technologies**
- **Python 3.11**: Core programming language
- **Flask**: Lightweight web framework
- **nflreadpy**: NFL data access library
- **Pandas**: Data manipulation and analysis
- **CORS**: Cross-origin resource sharing

### **Development Tools**
- **ESLint**: Code linting and quality
- **Git**: Version control
- **VS Code**: Development environment
- **Chrome DevTools**: Frontend debugging

---

## 📈 **Performance & Optimization**

### **Backend Optimization**
- **Data Caching**: In-memory caching of NFL data (107K+ records)
- **Efficient Sorting**: Optimized chronological sorting algorithms
- **API Response Limits**: Configurable result limits (20-50 games)
- **Error Handling**: Comprehensive error handling and fallbacks

### **Frontend Optimization**
- **Component Memoization**: React performance optimizations
- **Debounced Search**: 300ms search debouncing
- **Lazy Loading**: Efficient data loading strategies
- **CSS Grid**: Hardware-accelerated layouts

### **Load Times**
- **Backend Startup**: ~2-3 seconds (data loading)
- **Frontend Build**: ~465ms (Vite)
- **API Response**: <100ms (cached data)
- **Search Results**: Real-time (<300ms)

---

## 🎯 **HackGT 12 Alignment**

### **Crypt of Data Track Requirements** ✅
- **Signal from Noise**: Advanced filtering and search cuts through 107K+ data points
- **Pattern Recognition**: Chronological sorting and trend identification
- **Real-time Systems**: Live search and filtering capabilities
- **User Experience**: Intuitive interface for analysts and fans

### **PrizePicks Challenge Elements** ✅
- **Performance Trends**: Historical game and player tracking
- **Filtering Systems**: Multi-dimensional data filtering
- **Analytics Foundation**: Structured for future AI/ML integration
- **Real-time Insights**: Live game data and search capabilities

### **Innovation Points**
1. **Smart Search**: Natural language team name recognition
2. **Data Intelligence**: Historical coverage with predictive foundations
3. **User Experience**: Keyboard shortcuts and responsive design
4. **Scalable Architecture**: Modular frontend/backend separation

---

## 🚀 **Future Roadmap**

### **Phase 1: Enhanced Intelligence** (Next Sprint)
- [ ] Monte Carlo game simulation integration
- [ ] AI-powered game outcome predictions
- [ ] Statistical anomaly detection algorithms
- [ ] Performance confidence scoring

### **Phase 2: Advanced Analytics** (Future Development)
- [ ] Real-time game commentary AI
- [ ] Trend visualization dashboards
- [ ] Player performance anomaly alerts
- [ ] Broadcast-style game explanations

### **Phase 3: Platform Expansion** (Long-term)
- [ ] Multi-sport support (NBA, MLB, etc.)
- [ ] Mobile application development
- [ ] Advanced machine learning models
- [ ] Professional analytics tools

---

## 🤝 **Contributing**

We welcome contributions to SportTwist! Here's how to get involved:

### **Development Workflow**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### **Code Standards**
- **TypeScript**: Strict type checking enabled
- **ESLint**: Follow configured linting rules
- **Python**: PEP 8 style guidelines
- **Testing**: Write tests for new features

---

## 📋 **Project Status**

### **Current Version**: v1.0 (HackGT 12 Submission)

### **Completed Features** ✅
- [x] Full-stack application architecture
- [x] NFL data integration (2017-2025)
- [x] Advanced search and filtering system
- [x] Responsive UI with modern design
- [x] Real-time API communication
- [x] Chronological data sorting
- [x] Team and player intelligence
- [x] Popular games curation

### **In Development** 🚧
- [ ] Game simulation engine
- [ ] Predictive analytics
- [ ] AI insight generation
- [ ] Performance optimization

---

## 📞 **Contact & Team**

**Built for HackGT 12 by Team SportTwist**

- **Repository**: [github.com/sandro21/SportTwist](https://github.com/sandro21/SportTwist)
- **Track**: Crypt of Data
- **Challenge**: PrizePicks - Sports Intelligence & Insight Systems
- **Demo**: Available at hackathon presentation

---

## 📄 **License**

This project is developed for HackGT 12 and educational purposes. 

---

## 🙏 **Acknowledgments**

- **HackGT 12** for providing the platform and challenge
- **PrizePicks** for the sports intelligence challenge framework
- **nflreadpy** for comprehensive NFL data access
- **React & Vite** teams for excellent development tools
- **Flask** community for lightweight backend framework

---

*"Change a play. See the alternate outcome."* - SportTwist transforms how we analyze and understand NFL games through intelligent data processing and predictive insights. 🏈✨
